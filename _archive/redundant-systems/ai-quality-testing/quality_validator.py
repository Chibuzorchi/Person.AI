#!/usr/bin/env python3
"""
AI Output Quality Testing Framework
Implements semantic similarity, structure validation, and business rule validation for OpenAI and ElevenLabs outputs
"""

import json
import re
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from pathlib import Path
import requests
import librosa
import soundfile as sf

class QualityMetric(Enum):
    SEMANTIC_SIMILARITY = "semantic_similarity"
    STRUCTURE_VALIDATION = "structure_validation"
    BUSINESS_RULES = "business_rules"
    AUDIO_QUALITY = "audio_quality"
    CONSISTENCY = "consistency"

@dataclass
class QualityResult:
    metric: QualityMetric
    score: float  # 0.0 to 1.0
    passed: bool
    details: str
    baseline_comparison: Optional[Dict[str, Any]] = None

@dataclass
class AIOutputValidation:
    text_content: str
    audio_script: str
    audio_file_path: Optional[str] = None
    metadata: Dict[str, Any] = None

class SemanticSimilarityValidator:
    """Validates semantic similarity using embedding-based comparison"""
    
    def __init__(self, baseline_file: str = "baselines/semantic_baselines.json"):
        self.baseline_file = Path(baseline_file)
        self.baseline_file.parent.mkdir(exist_ok=True)
        self.baselines = self._load_baselines()
    
    def _load_baselines(self) -> Dict[str, Any]:
        """Load semantic similarity baselines"""
        if self.baseline_file.exists():
            with open(self.baseline_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_baselines(self):
        """Save updated baselines"""
        with open(self.baseline_file, 'w') as f:
            json.dump(self.baselines, f, indent=2)
    
    def _get_text_embedding(self, text: str) -> List[float]:
        """Get text embedding using simple word vector approach"""
        # In production, this would use OpenAI embeddings or similar
        # For now, using a simple TF-IDF-like approach
        words = text.lower().split()
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Create a simple vector representation
        all_words = set(words)
        vector = [word_counts.get(word, 0) for word in sorted(all_words)]
        
        # Normalize vector
        magnitude = sum(x**2 for x in vector) ** 0.5
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
        
        return vector
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        # Pad vectors to same length
        max_len = max(len(vec1), len(vec2))
        vec1 = vec1 + [0] * (max_len - len(vec1))
        vec2 = vec2 + [0] * (max_len - len(vec2))
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a**2 for a in vec1) ** 0.5
        magnitude2 = sum(b**2 for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def validate_semantic_similarity(self, new_output: str, baseline_key: str, 
                                   threshold: float = 0.8) -> QualityResult:
        """Validate semantic similarity against baseline"""
        if baseline_key not in self.baselines:
            # Create new baseline
            embedding = self._get_text_embedding(new_output)
            self.baselines[baseline_key] = {
                'embedding': embedding,
                'text': new_output,
                'created_at': datetime.now().isoformat()
            }
            self._save_baselines()
            
            return QualityResult(
                metric=QualityMetric.SEMANTIC_SIMILARITY,
                score=1.0,
                passed=True,
                details=f"New baseline created for {baseline_key}",
                baseline_comparison={'similarity': 1.0, 'is_new_baseline': True}
            )
        
        # Compare with existing baseline
        baseline = self.baselines[baseline_key]
        baseline_embedding = baseline['embedding']
        new_embedding = self._get_text_embedding(new_output)
        
        similarity = self._cosine_similarity(baseline_embedding, new_embedding)
        
        passed = similarity >= threshold
        
        return QualityResult(
            metric=QualityMetric.SEMANTIC_SIMILARITY,
            score=similarity,
            passed=passed,
            details=f"Similarity: {similarity:.3f} (threshold: {threshold})",
            baseline_comparison={
                'similarity': similarity,
                'threshold': threshold,
                'baseline_text': baseline['text'][:100] + "...",
                'is_new_baseline': False
            }
        )

class StructureValidator:
    """Validates structure and formatting of AI outputs"""
    
    def __init__(self, structure_rules: Dict[str, Any] = None):
        self.structure_rules = structure_rules or self._get_default_rules()
    
    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default structure validation rules"""
        return {
            'required_sections': ['Daily Brief', 'Email Summary', 'Key Insights', 'Action Items'],
            'required_headers': ['#', '##', '###'],
            'max_length': 2000,
            'min_length': 100,
            'required_placeholders': ['{date}', '{time}'],
            'forbidden_patterns': [r'ERROR:', r'FAILED:', r'NULL'],
            'required_formatting': {
                'bullet_points': True,
                'date_format': r'\d{4}-\d{2}-\d{2}',
                'time_format': r'\d{2}:\d{2}'
            }
        }
    
    def validate_structure(self, text_content: str) -> QualityResult:
        """Validate text structure and formatting"""
        errors = []
        warnings = []
        score = 1.0
        
        # Check required sections
        for section in self.structure_rules['required_sections']:
            if section not in text_content:
                errors.append(f"Missing required section: {section}")
                score -= 0.2
        
        # Check length constraints
        if len(text_content) > self.structure_rules['max_length']:
            errors.append(f"Content too long: {len(text_content)} > {self.structure_rules['max_length']}")
            score -= 0.1
        elif len(text_content) < self.structure_rules['min_length']:
            warnings.append(f"Content too short: {len(text_content)} < {self.structure_rules['min_length']}")
            score -= 0.05
        
        # Check for forbidden patterns
        for pattern in self.structure_rules['forbidden_patterns']:
            if re.search(pattern, text_content, re.IGNORECASE):
                errors.append(f"Contains forbidden pattern: {pattern}")
                score -= 0.3
        
        # Check formatting requirements
        if self.structure_rules['required_formatting']['bullet_points']:
            if not re.search(r'^\s*[•\-\*]\s+', text_content, re.MULTILINE):
                warnings.append("Missing bullet points")
                score -= 0.05
        
        # Check date format
        date_pattern = self.structure_rules['required_formatting']['date_format']
        if not re.search(date_pattern, text_content):
            warnings.append("Missing date in required format")
            score -= 0.05
        
        passed = len(errors) == 0
        details = f"Errors: {len(errors)}, Warnings: {len(warnings)}"
        if errors:
            details += f" | {', '.join(errors[:3])}"
        
        return QualityResult(
            metric=QualityMetric.STRUCTURE_VALIDATION,
            score=max(0.0, score),
            passed=passed,
            details=details
        )

class BusinessRulesValidator:
    """Validates business rules and logical consistency"""
    
    def __init__(self, business_rules: Dict[str, Any] = None):
        self.business_rules = business_rules or self._get_default_rules()
    
    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default business validation rules"""
        return {
            'financial_rules': {
                'no_negative_revenue': True,
                'no_negative_invoices': True,
                'currency_format': r'\$[\d,]+\.?\d*'
            },
            'date_rules': {
                'no_future_dates': True,
                'no_past_year': True
            },
            'content_rules': {
                'no_duplicate_insights': True,
                'min_action_items': 1,
                'max_action_items': 10
            }
        }
    
    def validate_business_rules(self, text_content: str, metadata: Dict[str, Any] = None) -> QualityResult:
        """Validate business rules and logical consistency"""
        errors = []
        warnings = []
        score = 1.0
        
        # Financial rules validation
        if self.business_rules['financial_rules']['no_negative_revenue']:
            if re.search(r'-\$[\d,]+', text_content):
                errors.append("Negative revenue detected")
                score -= 0.3
        
        if self.business_rules['financial_rules']['no_negative_invoices']:
            if re.search(r'invoice.*-\$[\d,]+', text_content, re.IGNORECASE):
                errors.append("Negative invoice amount detected")
                score -= 0.3
        
        # Date rules validation
        if self.business_rules['date_rules']['no_future_dates']:
            today = datetime.now().date()
            date_matches = re.findall(r'(\d{4}-\d{2}-\d{2})', text_content)
            for date_str in date_matches:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                    if date_obj > today:
                        errors.append(f"Future date detected: {date_str}")
                        score -= 0.2
                except ValueError:
                    pass
        
        # Content rules validation
        if self.business_rules['content_rules']['no_duplicate_insights']:
            insights = re.findall(r'•\s*([^•\n]+)', text_content)
            if len(insights) != len(set(insights)):
                warnings.append("Duplicate insights detected")
                score -= 0.1
        
        # Count action items
        action_items = re.findall(r'Action Items?:.*?(?=Key|$)', text_content, re.DOTALL | re.IGNORECASE)
        if action_items:
            item_count = len(re.findall(r'•\s*', action_items[0]))
            min_items = self.business_rules['content_rules']['min_action_items']
            max_items = self.business_rules['content_rules']['max_action_items']
            
            if item_count < min_items:
                errors.append(f"Too few action items: {item_count} < {min_items}")
                score -= 0.2
            elif item_count > max_items:
                warnings.append(f"Too many action items: {item_count} > {max_items}")
                score -= 0.1
        
        passed = len(errors) == 0
        details = f"Errors: {len(errors)}, Warnings: {len(warnings)}"
        if errors:
            details += f" | {', '.join(errors[:3])}"
        
        return QualityResult(
            metric=QualityMetric.BUSINESS_RULES,
            score=max(0.0, score),
            passed=passed,
            details=details
        )

class AudioQualityValidator:
    """Validates audio quality and consistency"""
    
    def __init__(self, baseline_audio_dir: str = "baselines/audio"):
        self.baseline_audio_dir = Path(baseline_audio_dir)
        self.baseline_audio_dir.mkdir(exist_ok=True)
    
    def validate_audio_quality(self, audio_file_path: str, baseline_key: str = None) -> QualityResult:
        """Validate audio file quality and consistency"""
        if not Path(audio_file_path).exists():
            return QualityResult(
                metric=QualityMetric.AUDIO_QUALITY,
                score=0.0,
                passed=False,
                details="Audio file not found"
            )
        
        try:
            # Load audio file
            audio_data, sample_rate = librosa.load(audio_file_path, sr=None)
            duration = len(audio_data) / sample_rate
            
            # Basic quality checks
            errors = []
            warnings = []
            score = 1.0
            
            # Check duration
            if duration < 10:  # Less than 10 seconds
                errors.append(f"Audio too short: {duration:.1f}s")
                score -= 0.3
            elif duration > 300:  # More than 5 minutes
                warnings.append(f"Audio too long: {duration:.1f}s")
                score -= 0.1
            
            # Check sample rate
            if sample_rate < 16000:
                errors.append(f"Low sample rate: {sample_rate}Hz")
                score -= 0.2
            
            # Check for silence
            silence_threshold = 0.01
            silent_samples = np.sum(np.abs(audio_data) < silence_threshold)
            silence_ratio = silent_samples / len(audio_data)
            
            if silence_ratio > 0.5:
                errors.append(f"Too much silence: {silence_ratio:.1%}")
                score -= 0.3
            elif silence_ratio > 0.3:
                warnings.append(f"High silence ratio: {silence_ratio:.1%}")
                score -= 0.1
            
            # Check audio level
            rms_level = np.sqrt(np.mean(audio_data**2))
            if rms_level < 0.01:
                errors.append(f"Audio level too low: {rms_level:.4f}")
                score -= 0.2
            elif rms_level > 0.5:
                warnings.append(f"Audio level too high: {rms_level:.4f}")
                score -= 0.1
            
            # Compare with baseline if provided
            baseline_comparison = None
            if baseline_key:
                baseline_file = self.baseline_audio_dir / f"{baseline_key}.wav"
                if baseline_file.exists():
                    baseline_data, baseline_sr = librosa.load(str(baseline_file), sr=sample_rate)
                    
                    # Compare duration
                    duration_diff = abs(duration - len(baseline_data) / baseline_sr)
                    if duration_diff > 10:  # More than 10 seconds difference
                        warnings.append(f"Duration differs from baseline: {duration_diff:.1f}s")
                        score -= 0.1
                    
                    baseline_comparison = {
                        'baseline_duration': len(baseline_data) / baseline_sr,
                        'current_duration': duration,
                        'duration_diff': duration_diff
                    }
            
            passed = len(errors) == 0
            details = f"Duration: {duration:.1f}s, Level: {rms_level:.3f}, Silence: {silence_ratio:.1%}"
            if errors:
                details += f" | Errors: {', '.join(errors)}"
            
            return QualityResult(
                metric=QualityMetric.AUDIO_QUALITY,
                score=max(0.0, score),
                passed=passed,
                details=details,
                baseline_comparison=baseline_comparison
            )
            
        except Exception as e:
            return QualityResult(
                metric=QualityMetric.AUDIO_QUALITY,
                score=0.0,
                passed=False,
                details=f"Audio validation error: {str(e)}"
            )

class AIQualityValidator:
    """Main AI quality validation orchestrator"""
    
    def __init__(self, baselines_dir: str = "baselines"):
        self.baselines_dir = Path(baselines_dir)
        self.baselines_dir.mkdir(exist_ok=True)
        
        self.semantic_validator = SemanticSimilarityValidator(
            str(self.baselines_dir / "semantic_baselines.json")
        )
        self.structure_validator = StructureValidator()
        self.business_validator = BusinessRulesValidator()
        self.audio_validator = AudioQualityValidator(
            str(self.baselines_dir / "audio")
        )
    
    def validate_ai_output(self, output: AIOutputValidation, 
                          baseline_key: str = None) -> Dict[str, QualityResult]:
        """Validate complete AI output quality"""
        results = {}
        
        print(f"🔍 Validating AI output quality...")
        
        # Semantic similarity validation
        if baseline_key:
            semantic_result = self.semantic_validator.validate_semantic_similarity(
                output.text_content, f"{baseline_key}_text"
            )
            results['semantic_similarity'] = semantic_result
            print(f"  Semantic Similarity: {semantic_result.score:.3f} {'✅' if semantic_result.passed else '❌'}")
        
        # Structure validation
        structure_result = self.structure_validator.validate_structure(output.text_content)
        results['structure_validation'] = structure_result
        print(f"  Structure Validation: {structure_result.score:.3f} {'✅' if structure_result.passed else '❌'}")
        
        # Business rules validation
        business_result = self.business_validator.validate_business_rules(
            output.text_content, output.metadata
        )
        results['business_rules'] = business_result
        print(f"  Business Rules: {business_result.score:.3f} {'✅' if business_result.passed else '❌'}")
        
        # Audio quality validation
        if output.audio_file_path:
            audio_result = self.audio_validator.validate_audio_quality(
                output.audio_file_path, baseline_key
            )
            results['audio_quality'] = audio_result
            print(f"  Audio Quality: {audio_result.score:.3f} {'✅' if audio_result.passed else '❌'}")
        
        return results
    
    def get_overall_score(self, results: Dict[str, QualityResult]) -> float:
        """Calculate overall quality score"""
        if not results:
            return 0.0
        
        scores = [result.score for result in results.values()]
        return sum(scores) / len(scores)
    
    def get_overall_status(self, results: Dict[str, QualityResult]) -> bool:
        """Check if all validations passed"""
        return all(result.passed for result in results.values())

def create_sample_ai_output() -> AIOutputValidation:
    """Create sample AI output for testing"""
    text_content = """
Daily Brief - 2024-01-15

Email Summary:
• Quarterly Sales Report - john@company.com
• Client Meeting Request - sarah@client.com
• Invoice Payment Overdue - billing@vendor.com

Key Insights:
• 3 urgent items require immediate attention
• 2 client meetings scheduled for this week
• 1 invoice payment overdue
• New project proposal received

Action Items:
• Review quarterly sales report
• Schedule follow-up meeting with client
• Process invoice payment
• Prepare project proposal

Generated by Person.ai
    """.strip()
    
    audio_script = """
Good morning! Here's your daily brief for January 15, 2024.

You have 4 important emails today. The quarterly sales report from John requires immediate attention. Sarah from our client wants to schedule a meeting this week. There's an overdue invoice payment from our vendor, and we've received a new project proposal.

Key insights for today: 3 urgent items require immediate attention, 2 client meetings scheduled for this week, 1 invoice payment overdue, and a new project proposal received.

Your action items: Review quarterly sales report, schedule follow-up meeting with client, process invoice payment, and prepare project proposal.

This brief was generated by Person.ai. Have a productive day!
    """.strip()
    
    return AIOutputValidation(
        text_content=text_content,
        audio_script=audio_script,
        metadata={
            'generation_time': time.time(),
            'email_count': 4,
            'confidence_score': 0.85
        }
    )

if __name__ == "__main__":
    # Create sample AI output
    sample_output = create_sample_ai_output()
    
    # Initialize validator
    validator = AIQualityValidator()
    
    # Validate AI output
    results = validator.validate_ai_output(sample_output, "daily_brief_sample")
    
    # Print results
    print(f"\n📊 AI Quality Validation Results")
    print(f"Overall Score: {validator.get_overall_score(results):.3f}")
    print(f"Overall Status: {'✅ PASS' if validator.get_overall_status(results) else '❌ FAIL'}")
    
    for metric, result in results.items():
        print(f"\n{metric.replace('_', ' ').title()}:")
        print(f"  Score: {result.score:.3f}")
        print(f"  Status: {'✅ PASS' if result.passed else '❌ FAIL'}")
        print(f"  Details: {result.details}")
