# ACNE Version Manager
import json
import os
import shutil
from datetime import datetime
from typing import List

class VersionManager:
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.version_file = os.path.join(project_root, "version.json")
    
    def get_current_version(self) -> str:
        """Get current version from version.json"""
        try:
            with open(self.version_file, 'r') as f:
                data = json.load(f)
            return data.get('version', '1.0.0-dev')
        except:
            return '1.0.0-dev'
    
    def bump_version(self, bump_type: str, changes: List[str] = None) -> str:
        """Bump version number"""
        current = self.get_current_version()
        
        # Parse current version
        version_part = current.split('-')[0]  # Remove -dev suffix
        major, minor, patch = map(int, version_part.split('.'))
        
        # Bump based on type
        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump_type == 'minor':
            minor += 1 
            patch = 0
        elif bump_type == 'patch':
            patch += 1
        else:
            raise ValueError("bump_type must be 'major', 'minor', or 'patch'")
        
        new_version = f"{major}.{minor}.{patch}"
        
        # Update version.json
        version_data = {
            "version": new_version,
            "previous_version": current,
            "release_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "release",
            "bump_type": bump_type,
            "changes": changes or []
        }
        
        with open(self.version_file, 'w') as f:
            json.dump(version_data, f, indent=2)
        
        return new_version
    
    def create_release(self, version: str = None) -> str:
        """Create release directory with current code"""
        if not version:
            version = self.get_current_version().replace('-dev', '')
        
        # Create release directory
        release_dir = os.path.join(self.project_root, "releases", f"v{version}")
        os.makedirs(release_dir, exist_ok=True)
        
        # Copy current source files
        src_dir = os.path.join(self.project_root, "src", f"v{version}")
        
        if os.path.exists(src_dir):
            for file in os.listdir(src_dir):
                shutil.copy2(
                    os.path.join(src_dir, file),
                    os.path.join(release_dir, file)
                )
        
        # Create changelog
        changelog_path = os.path.join(release_dir, "CHANGELOG.md")
        with open(changelog_path, 'w') as f:
            f.write(f"# ACNE v{version} Release Notes\n\n")
            f.write(f"Released: {datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write("## Features\n")
            f.write("- Real GitHub repository deployment\n")
            f.write("- Git self-management\n")
            f.write("- Enhanced conversation interface\n")
        
        return release_dir

# CLI usage for version management
def main():
    import sys
    
    vm = VersionManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'current':
            print(f"Current version: {vm.get_current_version()}")
        elif command == 'bump':
            bump_type = sys.argv[2] if len(sys.argv) > 2 else 'patch'
            new_version = vm.bump_version(bump_type)
            print(f"Version bumped to: {new_version}")
        elif command == 'release':
            release_dir = vm.create_release()
            print(f"Release created: {release_dir}")
    else:
        print("ACNE Version Manager")
        print("Commands: current, bump [major|minor|patch], release")

if __name__ == "__main__":
    main()
