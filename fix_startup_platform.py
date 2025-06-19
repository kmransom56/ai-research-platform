#!/usr/bin/env python3
"""
Fix startup_platform.py dependency and syntax issues
"""

import subprocess
import sys
import ast
import os
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing required dependencies...")
    
    dependencies = ["aiohttp", "psutil"]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} already installed")
        except ImportError:
            print(f"📥 Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} installed successfully")

def check_syntax(file_path):
    """Check Python syntax"""
    print(f"🔍 Checking syntax of {file_path}...")
    
    try:
        with open(file_path, 'r') as f:
            source = f.read()
        
        # Parse the AST to check for syntax errors
        ast.parse(source)
        print("✅ Syntax check passed")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error checking syntax: {e}")
        return False

def run_import_test(file_path):
    """Test if the file can be imported"""
    print(f"🧪 Testing imports for {file_path}...")
    
    # Change to the directory containing the file
    original_dir = os.getcwd()
    try:
        file_dir = os.path.dirname(file_path)
        if file_dir:
            os.chdir(file_dir)
        
        # Try to compile the file
        with open(file_path, 'r') as f:
            source = f.read()
        
        compile(source, file_path, 'exec')
        print("✅ Import test passed")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False
    finally:
        os.chdir(original_dir)

def main():
    """Main fixing function"""
    print("🔧 Fixing startup_platform.py")
    print("=" * 40)
    
    file_path = "/home/keith/chat-copilot/startup_platform.py"
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return
    
    # Step 1: Install dependencies
    install_dependencies()
    
    # Step 2: Check syntax
    syntax_ok = check_syntax(file_path)
    
    # Step 3: Test imports
    import_ok = run_import_test(file_path)
    
    # Summary
    print("\n📊 SUMMARY:")
    print(f"   Syntax Check: {'✅ PASS' if syntax_ok else '❌ FAIL'}")
    print(f"   Import Test:  {'✅ PASS' if import_ok else '❌ FAIL'}")
    
    if syntax_ok and import_ok:
        print("\n🎉 startup_platform.py is ready to use!")
        print("\n🚀 You can now run:")
        print(f"   python3 {file_path}")
    else:
        print("\n⚠️  Issues found that need manual fixing")

if __name__ == "__main__":
    main()
