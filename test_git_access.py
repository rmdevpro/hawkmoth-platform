import subprocess
import os

def test_git():
    git_paths = [
        'git',
        'C:\\Program Files\\Git\\cmd\\git.exe',
        'C:\\Program Files\\Git\\bin\\git.exe'
    ]
    
    for git_path in git_paths:
        try:
            result = subprocess.run([git_path, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"SUCCESS: Found Git at {git_path}")
                print(f"Version: {result.stdout.strip()}")
                return git_path
            else:
                print(f"FAILED: {git_path} - {result.stderr}")
        except Exception as e:
            print(f"ERROR: {git_path} - {e}")
    
    return None

if __name__ == "__main__":
    print("Testing Git access from Python...")
    git_path = test_git()
    if git_path:
        print(f"Git is accessible at: {git_path}")
        
        # Test basic Git operations
        try:
            os.chdir("G:\\Claud\\ACNE-Project")
            
            # Test git status
            result = subprocess.run([git_path, 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            print(f"Git status: {result.stdout}")
            
            # Test if we're in a Git repo
            result = subprocess.run([git_path, 'rev-parse', '--git-dir'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Git repository found at: {result.stdout.strip()}")
            else:
                print("Not in a Git repository")
                
        except Exception as e:
            print(f"Git operations failed: {e}")
    else:
        print("Git is not accessible from Python")
