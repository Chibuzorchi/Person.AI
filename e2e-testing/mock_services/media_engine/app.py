"""
Media Engine Mock Service (ElevenLabs-style)
"""
import os
import json
import time
import tempfile
import uuid
from datetime import datetime
from flask import Flask, jsonify, request, send_file
import pyttsx3

app = Flask(__name__)

class MediaEngineMock:
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY', 'mock_key')
        self.voice_id = 'mock_voice_id'
        self.output_dir = '/app/output'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_audio(self, text, voice_id=None):
        """Generate audio from text (ElevenLabs-style)"""
        # For now, use fallback audio generation to avoid pyttsx3 issues in Docker
        return self._create_fallback_audio(text, voice_id)
    
    def _create_fallback_audio(self, text, voice_id):
        """Create fallback audio file"""
        audio_filename = f"brief_{uuid.uuid4().hex[:8]}.wav"
        audio_path = os.path.join(self.output_dir, audio_filename)
        
        # Create a simple WAV file header
        with open(audio_path, 'wb') as f:
            # WAV file header
            f.write(b'RIFF')
            f.write((36 + len(text) * 2).to_bytes(4, 'little'))
            f.write(b'WAVE')
            f.write(b'fmt ')
            f.write((16).to_bytes(4, 'little'))
            f.write((1).to_bytes(2, 'little'))  # PCM
            f.write((1).to_bytes(2, 'little'))  # Mono
            f.write((22050).to_bytes(4, 'little'))  # Sample rate
            f.write((44100).to_bytes(4, 'little'))  # Byte rate
            f.write((2).to_bytes(2, 'little'))  # Block align
            f.write((16).to_bytes(2, 'little'))  # Bits per sample
            f.write(b'data')
            f.write((len(text) * 2).to_bytes(4, 'little'))
            
            # Simple audio data (silence)
            for _ in range(len(text)):
                f.write(b'\x00\x00')
        
        return {
            'audio_file': audio_path,
            'filename': audio_filename,
            'duration': len(text) * 0.1,
            'file_size': os.path.getsize(audio_path),
            'voice_id': voice_id or self.voice_id,
            'quality': 'standard',
            'format': 'wav',
            'generated_at': datetime.now().isoformat()
        }

# Initialize service
media_engine = MediaEngineMock()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'media-engine-mock',
        'timestamp': datetime.now().isoformat(),
        'voice_id': media_engine.voice_id
    })

@app.route('/v1/text-to-speech/<voice_id>', methods=['POST'])
def text_to_speech(voice_id):
    """ElevenLabs-style text-to-speech endpoint"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        # Generate audio
        result = media_engine.generate_audio(text, voice_id)
        
        return jsonify({
            'audio_file': result['filename'],
            'duration': result['duration'],
            'file_size': result['file_size'],
            'voice_id': result['voice_id'],
            'quality': result['quality'],
            'format': result['format'],
            'generated_at': result['generated_at']
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audio/<filename>', methods=['GET'])
def get_audio_file(filename):
    """Get generated audio file"""
    try:
        audio_path = os.path.join(media_engine.output_dir, filename)
        
        if not os.path.exists(audio_path):
            return jsonify({"error": "Audio file not found"}), 404
        
        return send_file(audio_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-audio', methods=['POST'])
def generate_audio():
    """Generate audio from text endpoint"""
    try:
        data = request.json
        text = data.get('text', '')
        voice_id = data.get('voice_id', media_engine.voice_id)
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        # Generate audio
        result = media_engine.generate_audio(text, voice_id)
        
        return jsonify({
            'status': 'success',
            'result': result,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
