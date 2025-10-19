#!/usr/bin/env python3
"""
Test script to verify the server structure and validate the code without running it.
This script performs static analysis and validation of the FastAPI application.
"""
import ast
import sys
from pathlib import Path


def validate_python_file(filepath):
    """Validate that a Python file has correct syntax."""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        ast.parse(code)
        print(f"✓ {filepath}: Syntax valid")
        return True
    except SyntaxError as e:
        print(f"✗ {filepath}: Syntax error - {e}")
        return False


def check_imports(filepath):
    """Check that imports are properly structured."""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        tree = ast.parse(code)
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        print(f"✓ {filepath}: Found {len(imports)} import statements")
        return True
    except Exception as e:
        print(f"✗ {filepath}: Error checking imports - {e}")
        return False


def check_fastapi_structure(filepath):
    """Check FastAPI app structure."""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        
        # Check for required elements
        checks = [
            ("FastAPI app initialization", "FastAPI(" in code),
            ("Health endpoint", "@app.get(\"/health\"" in code or '@app.get("/health"' in code),
            ("Inference endpoint", "@app.post(\"/inference\"" in code or '@app.post("/inference"' in code),
            ("Request validation", "class InferenceRequest" in code),
            ("Response model", "class InferenceResponse" in code),
            ("Error handling", "HTTPException" in code),
            ("Startup event", "@app.on_event(\"startup\")" in code or "@app.on_event('startup')" in code),
            ("Model loading", "AutoModelForCausalLM" in code),
        ]
        
        all_passed = True
        for check_name, result in checks:
            status = "✓" if result else "✗"
            print(f"{status} {check_name}: {'Present' if result else 'Missing'}")
            all_passed = all_passed and result
        
        return all_passed
    except Exception as e:
        print(f"✗ Error checking FastAPI structure - {e}")
        return False


def check_config_structure(filepath):
    """Check configuration file structure."""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        
        checks = [
            ("Settings class", "class Settings" in code),
            ("BaseSettings inheritance", "BaseSettings" in code),
            ("Environment variables support", "env_file" in code),
            ("Model settings", "model_name" in code),
            ("Server settings", "host" in code and "port" in code),
        ]
        
        all_passed = True
        for check_name, result in checks:
            status = "✓" if result else "✗"
            print(f"{status} {check_name}: {'Present' if result else 'Missing'}")
            all_passed = all_passed and result
        
        return all_passed
    except Exception as e:
        print(f"✗ Error checking config structure - {e}")
        return False


def main():
    """Main validation function."""
    print("=" * 60)
    print("FastAPI Inference Server - Code Validation")
    print("=" * 60)
    print()
    
    # Check main files exist
    main_py = Path("main.py")
    config_py = Path("config.py")
    requirements_txt = Path("requirements.txt")
    gitignore = Path(".gitignore")
    readme = Path("README.md")
    
    files_exist = all([
        main_py.exists(),
        config_py.exists(),
        requirements_txt.exists(),
        gitignore.exists(),
        readme.exists()
    ])
    
    if not files_exist:
        print("✗ Not all required files exist")
        return False
    
    print("✓ All required files exist")
    print()
    
    # Validate Python syntax
    print("Validating Python syntax:")
    print("-" * 60)
    syntax_valid = all([
        validate_python_file(main_py),
        validate_python_file(config_py)
    ])
    print()
    
    # Check imports
    print("Checking imports:")
    print("-" * 60)
    imports_ok = all([
        check_imports(main_py),
        check_imports(config_py)
    ])
    print()
    
    # Check FastAPI structure
    print("Checking FastAPI structure:")
    print("-" * 60)
    fastapi_ok = check_fastapi_structure(main_py)
    print()
    
    # Check config structure
    print("Checking configuration structure:")
    print("-" * 60)
    config_ok = check_config_structure(config_py)
    print()
    
    # Check requirements.txt
    print("Checking requirements.txt:")
    print("-" * 60)
    with open(requirements_txt, 'r') as f:
        requirements = f.read()
    required_packages = ["fastapi", "uvicorn", "pydantic", "transformers", "torch"]
    requirements_ok = all(pkg in requirements for pkg in required_packages)
    for pkg in required_packages:
        status = "✓" if pkg in requirements else "✗"
        print(f"{status} {pkg}: {'Present' if pkg in requirements else 'Missing'}")
    print()
    
    # Summary
    print("=" * 60)
    print("Validation Summary:")
    print("=" * 60)
    all_checks = [
        ("Files exist", files_exist),
        ("Python syntax", syntax_valid),
        ("Imports", imports_ok),
        ("FastAPI structure", fastapi_ok),
        ("Configuration", config_ok),
        ("Requirements", requirements_ok)
    ]
    
    for check_name, result in all_checks:
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
    
    all_passed = all(result for _, result in all_checks)
    print()
    print("=" * 60)
    if all_passed:
        print("✓ All validations passed!")
        print("The server code is correctly structured and ready to run.")
        print()
        print("To run the server:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Start the server: python main.py")
        print("  3. Access the API docs at: http://localhost:8000/docs")
    else:
        print("✗ Some validations failed")
        return False
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
