#!/usr/bin/env python3
"""
Tiered Test Runner for Person.ai Integration Testing
Implements the scaling strategy for 150+ integrations with parallel execution
"""
import subprocess
import sys
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

class TieredTestRunner:
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
    
    def run_command(self, cmd, component, tier):
        """Run a test command and capture results"""
        print(f"🚀 Running {tier} tests for {component}...")
        start = time.time()
        
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=f"./{component}"
            )
            duration = time.time() - start
            
            self.results[f"{component}_{tier}"] = {
                'component': component,
                'tier': tier,
                'duration': duration,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
            status = "✅ PASSED" if result.returncode == 0 else "❌ FAILED"
            print(f"   {status} {component} ({tier}) - {duration:.2f}s")
            
        except Exception as e:
            duration = time.time() - start
            self.results[f"{component}_{tier}"] = {
                'component': component,
                'tier': tier,
                'duration': duration,
                'returncode': 1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
            print(f"   ❌ ERROR {component} ({tier}) - {duration:.2f}s: {e}")

    def run_tier1_critical(self, parallel=True):
        """Run Tier 1 Critical tests (Slack, Gmail, E2E) - Every commit"""
        print("\n🔥 TIER 1 CRITICAL TESTS (Every Commit)")
        print("=" * 50)
        
        commands = [
            ("pytest -m 'tier1_critical and standalone' -v", "slack-mock", "tier1"),
            ("pytest -m 'tier1_critical and standalone' -v", "e2e-testing", "tier1"),
        ]
        
        # Only run integration tests if not in CI or if Docker is available
        if not os.getenv('CI') or os.getenv('DOCKER_SERVICES_RUNNING'):
            commands.append(("pytest -m 'tier1_critical and integration' -v", "slack-mock", "tier1_integration"))
        
        if parallel:
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(self.run_command, cmd, comp, tier) for cmd, comp, tier in commands]
                for future in as_completed(futures):
                    future.result()
        else:
            for cmd, comp, tier in commands:
                self.run_command(cmd, comp, tier)

    def run_tier2_important(self, parallel=True):
        """Run Tier 2 Important tests (QuickBooks, Salesforce) - Schema changes"""
        print("\n⚡ TIER 2 IMPORTANT TESTS (Schema Changes)")
        print("=" * 50)
        
        commands = [
            ("pytest -m 'tier2_important and standalone' -v", "test-data-seeding", "tier2"),
            ("pytest -m 'tier2_important and integration' -v", "test-data-seeding", "tier2_integration"),
        ]
        
        if parallel:
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(self.run_command, cmd, comp, tier) for cmd, comp, tier in commands]
                for future in as_completed(futures):
                    future.result()
        else:
            for cmd, comp, tier in commands:
                self.run_command(cmd, comp, tier)

    def run_tier3_secondary(self, parallel=True):
        """Run Tier 3 Secondary tests (Monitoring, UI) - Weekly"""
        print("\n📊 TIER 3 SECONDARY TESTS (Weekly)")
        print("=" * 50)
        
        commands = [
            ("pytest -m 'tier3_secondary and standalone' -v", "monitoring-system", "tier3"),
            ("pytest -m 'tier3_secondary and standalone' -v", "bubble-frontend-mock", "tier3"),
        ]
        
        if parallel:
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(self.run_command, cmd, comp, tier) for cmd, comp, tier in commands]
                for future in as_completed(futures):
                    future.result()
        else:
            for cmd, comp, tier in commands:
                self.run_command(cmd, comp, tier)

    def run_smoke_tests(self):
        """Run quick smoke tests for basic functionality"""
        print("\n💨 SMOKE TESTS (Quick Validation)")
        print("=" * 50)
        
        commands = [
            ("pytest -m smoke -v", "slack-mock", "smoke"),
            ("pytest -m smoke -v", "test-data-seeding", "smoke"),
            ("pytest -m smoke -v", "e2e-testing", "smoke"),
        ]
        
        for cmd, comp, tier in commands:
            self.run_command(cmd, comp, tier)

    def run_regression_suite(self):
        """Run full regression test suite"""
        print("\n🔄 FULL REGRESSION SUITE")
        print("=" * 50)
        
        components = ["slack-mock", "test-data-seeding", "e2e-testing", "monitoring-system", "bubble-frontend-mock"]
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.run_command, "pytest -v", comp, "regression") for comp in components]
            for future in as_completed(futures):
                future.result()

    def print_summary(self):
        """Print test execution summary"""
        total_time = time.time() - self.start_time
        successful = sum(1 for r in self.results.values() if r['success'])
        total = len(self.results)
        
        print("\n" + "=" * 60)
        print("📊 TEST EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        print(f"Success Rate: {(successful/total)*100:.1f}%")
        print(f"Total Time: {total_time:.2f}s")
        
        print("\n📋 DETAILED RESULTS:")
        for key, result in self.results.items():
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['component']} ({result['tier']}) - {result['duration']:.2f}s")
            if not result['success'] and result['stderr']:
                print(f"    Error: {result['stderr'][:100]}...")

def main():
    parser = argparse.ArgumentParser(description='Tiered Test Runner for Person.ai')
    parser.add_argument('--tier', choices=['1', '2', '3', 'smoke', 'regression', 'all'], 
                       default='1', help='Which tier to run')
    parser.add_argument('--parallel', action='store_true', default=True, 
                       help='Run tests in parallel')
    parser.add_argument('--sequential', action='store_true', 
                       help='Run tests sequentially')
    
    args = parser.parse_args()
    
    runner = TieredTestRunner()
    
    if args.sequential:
        args.parallel = False
    
    print("🎯 Person.ai Tiered Test Runner")
    print("=" * 60)
    print("Strategy: Critical tests run fast, secondary tests run when needed")
    print("Scaling: Parallel execution for 150+ integrations")
    print("=" * 60)
    
    if args.tier == '1' or args.tier == 'all':
        runner.run_tier1_critical(parallel=args.parallel)
    
    if args.tier == '2' or args.tier == 'all':
        runner.run_tier2_important(parallel=args.parallel)
    
    if args.tier == '3' or args.tier == 'all':
        runner.run_tier3_secondary(parallel=args.parallel)
    
    if args.tier == 'smoke' or args.tier == 'all':
        runner.run_smoke_tests()
    
    if args.tier == 'regression' or args.tier == 'all':
        runner.run_regression_suite()
    
    runner.print_summary()

if __name__ == "__main__":
    main()
