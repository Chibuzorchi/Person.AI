#!/usr/bin/env python3
"""
CI/CD Status Dashboard
Shows the status of all GitHub Actions workflows
"""

import requests
import json
from datetime import datetime
import os

def get_workflow_status(owner, repo, token=None):
    """Get workflow run status from GitHub API"""
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching workflow status: {e}")
        return None

def format_status(status):
    """Format status with emoji"""
    status_map = {
        'completed': '✅',
        'in_progress': '🔄',
        'queued': '⏳',
        'failed': '❌',
        'cancelled': '⏹️'
    }
    return status_map.get(status, '❓')

def main():
    print("🔄 Person.ai CI/CD Status Dashboard")
    print("=" * 50)
    
    # Get repository info from git
    try:
        import subprocess
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            remote_url = result.stdout.strip()
            if 'github.com' in remote_url:
                # Extract owner/repo from URL
                parts = remote_url.replace('.git', '').split('/')
                owner = parts[-2]
                repo = parts[-1]
                print(f"Repository: {owner}/{repo}")
            else:
                print("Not a GitHub repository")
                return
        else:
            print("Could not determine repository")
            return
    except Exception as e:
        print(f"Error getting repository info: {e}")
        return
    
    # Get GitHub token from environment
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("⚠️  GITHUB_TOKEN not set. Some features may be limited.")
    
    # Get workflow runs
    workflow_data = get_workflow_status(owner, repo, token)
    if not workflow_data:
        return
    
    print(f"\n📊 Recent Workflow Runs (Last 10)")
    print("-" * 50)
    
    for run in workflow_data['workflow_runs'][:10]:
        workflow_name = run['name']
        status = run['status']
        conclusion = run['conclusion']
        created_at = run['created_at']
        html_url = run['html_url']
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            time_str = created_at
        
        # Determine final status
        if status == 'completed':
            final_status = conclusion
        else:
            final_status = status
        
        status_emoji = format_status(final_status)
        
        print(f"{status_emoji} {workflow_name}")
        print(f"   Status: {final_status}")
        print(f"   Time: {time_str}")
        print(f"   URL: {html_url}")
        print()
    
    print("🔗 View all workflows:")
    print(f"   https://github.com/{owner}/{repo}/actions")
    
    print("\n📋 Workflow Schedule:")
    print("   • Slack Integration: On push/PR + manual")
    print("   • Test Data Seeding: Daily at 2 AM")
    print("   • E2E Pipeline: Daily at 4 AM")
    print("   • Monitoring System: Every 6 hours")
    print("   • Bubble Frontend: Daily at 8 AM")
    print("   • Integration Tests: Daily at 6 AM")
    print("   • Master CI/CD: Daily at 1 AM")

if __name__ == "__main__":
    main()
