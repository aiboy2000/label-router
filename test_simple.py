#!/usr/bin/env python3
"""
Simple test to verify code structure without dependencies
"""

import os
import sys
from pathlib import Path

def test_project_structure():
    """Test that all required files and directories exist"""
    
    print("=== Label Router Structure Test ===\n")
    
    base_path = Path(__file__).parent
    
    # Check directories
    required_dirs = [
        "src",
        "src/api",
        "src/core", 
        "src/models",
        "src/utils",
        "tests",
        "docs"
    ]
    
    print("Checking directories...")
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ - Missing")
    
    print("\nChecking core files...")
    
    # Check files
    required_files = [
        "requirements.txt",
        "setup.py",
        "src/__init__.py",
        "src/api/__init__.py",
        "src/api/main.py",
        "src/api/storage.py",
        "src/core/__init__.py",
        "src/core/rule_tagger.py",
        "src/core/ml_tagger.py",
        "src/core/smart_tagger.py",
        "src/models/__init__.py",
        "src/models/tags.py",
        "src/ui_demo.py",
        "docs/API_DOCUMENTATION.md",
        "docs/USAGE_EXAMPLES.md",
        "README_IMPLEMENTATION.md"
    ]
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists() and full_path.is_file():
            size = full_path.stat().st_size
            print(f"✓ {file_path} ({size} bytes)")
        else:
            print(f"✗ {file_path} - Missing")
    
    print("\nChecking Python syntax...")
    
    # Check Python files can be parsed
    python_files = [
        "src/api/main.py",
        "src/api/storage.py",
        "src/core/rule_tagger.py",
        "src/core/ml_tagger.py",
        "src/core/smart_tagger.py",
        "src/models/tags.py",
        "src/ui_demo.py"
    ]
    
    for file_path in python_files:
        full_path = base_path / file_path
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                code = f.read()
                compile(code, file_path, 'exec')
            print(f"✓ {file_path} - Valid Python syntax")
        except SyntaxError as e:
            print(f"✗ {file_path} - Syntax error: {e}")
        except Exception as e:
            print(f"✗ {file_path} - Error: {e}")
    
    print("\n=== Structure Test Complete ===")


if __name__ == "__main__":
    test_project_structure()