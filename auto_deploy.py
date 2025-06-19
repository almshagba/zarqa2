#!/usr/bin/env python3
"""
Auto Deploy Script for Employee Management System
This script automates the deployment process to Render
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr.strip()}")
        return False

def check_git_status():
    """Check if there are uncommitted changes"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        return len(result.stdout.strip()) == 0
    except:
        return False

def auto_deploy():
    """Main auto-deploy function"""
    print("🚀 Starting Auto-Deploy Process for Employee Management System")
    print(f"📅 Deployment started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not in a git repository. Please run this script from the project root.")
        return False
    
    # Check for uncommitted changes
    if not check_git_status():
        print("\n📝 Uncommitted changes detected. Adding and committing...")
        
        # Add all changes
        if not run_command('git add .', 'Adding all changes'):
            return False
        
        # Commit changes with timestamp
        commit_msg = f"Auto-deploy: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        if not run_command(f'git commit -m "{commit_msg}"', 'Committing changes'):
            return False
    else:
        print("✅ No uncommitted changes found")
    
    # Push to GitHub
    if not run_command('git push origin master', 'Pushing to GitHub'):
        return False
    
    print("\n🎉 Auto-deploy completed successfully!")
    print("📡 Render will automatically deploy the latest changes.")
    print("🔗 Check your Render dashboard for deployment status.")
    
    return True

if __name__ == "__main__":
    try:
        success = auto_deploy()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)