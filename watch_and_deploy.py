#!/usr/bin/env python3
"""
Watch and Auto-Deploy Script
Monitors file changes and automatically deploys when changes are detected
"""

import os
import time
import subprocess
from datetime import datetime
from pathlib import Path

class FileWatcher:
    def __init__(self, watch_directory=".", ignore_patterns=None):
        self.watch_directory = Path(watch_directory)
        self.ignore_patterns = ignore_patterns or [
            '__pycache__',
            '.git',
            'node_modules',
            '.env',
            '*.pyc',
            '*.log',
            'backups',
            'instance',
            'venv',
            'new_env'
        ]
        self.last_modified = {}
        self.scan_files()
    
    def should_ignore(self, file_path):
        """Check if file should be ignored"""
        path_str = str(file_path)
        for pattern in self.ignore_patterns:
            if pattern in path_str:
                return True
        return False
    
    def scan_files(self):
        """Scan all files and record modification times"""
        for file_path in self.watch_directory.rglob('*'):
            if file_path.is_file() and not self.should_ignore(file_path):
                try:
                    self.last_modified[str(file_path)] = file_path.stat().st_mtime
                except (OSError, PermissionError):
                    pass
    
    def check_changes(self):
        """Check for file changes"""
        changes = []
        current_files = {}
        
        # Check existing files for modifications
        for file_path in self.watch_directory.rglob('*'):
            if file_path.is_file() and not self.should_ignore(file_path):
                try:
                    file_str = str(file_path)
                    current_mtime = file_path.stat().st_mtime
                    current_files[file_str] = current_mtime
                    
                    if file_str in self.last_modified:
                        if current_mtime > self.last_modified[file_str]:
                            changes.append(f"Modified: {file_path.name}")
                    else:
                        changes.append(f"Added: {file_path.name}")
                except (OSError, PermissionError):
                    pass
        
        # Check for deleted files
        for file_str in self.last_modified:
            if file_str not in current_files:
                changes.append(f"Deleted: {Path(file_str).name}")
        
        self.last_modified = current_files
        return changes

def auto_deploy():
    """Run auto-deploy script"""
    try:
        print(f"\n🚀 Starting deployment at {datetime.now().strftime('%H:%M:%S')}")
        result = subprocess.run(['python', 'auto_deploy.py'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Deployment completed successfully")
            return True
        else:
            print(f"❌ Deployment failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⏰ Deployment timed out")
        return False
    except Exception as e:
        print(f"❌ Deployment error: {str(e)}")
        return False

def main():
    """Main watch and deploy loop"""
    print("👀 File Watcher and Auto-Deploy Started")
    print("📁 Watching directory:", os.getcwd())
    print("⏹️  Press Ctrl+C to stop")
    print("="*50)
    
    watcher = FileWatcher()
    last_deploy_time = 0
    deploy_cooldown = 60  # 1 minute cooldown between deployments
    
    try:
        while True:
            changes = watcher.check_changes()
            
            if changes:
                print(f"\n📝 Changes detected at {datetime.now().strftime('%H:%M:%S')}:")
                for change in changes[:5]:  # Show max 5 changes
                    print(f"   {change}")
                if len(changes) > 5:
                    print(f"   ... and {len(changes) - 5} more changes")
                
                current_time = time.time()
                if current_time - last_deploy_time > deploy_cooldown:
                    if auto_deploy():
                        last_deploy_time = current_time
                    else:
                        print("⚠️  Deployment failed, will retry on next change")
                else:
                    remaining = int(deploy_cooldown - (current_time - last_deploy_time))
                    print(f"⏳ Deployment cooldown: {remaining}s remaining")
            
            time.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\n⏹️  File watcher stopped by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()