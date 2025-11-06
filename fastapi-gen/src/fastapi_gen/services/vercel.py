"""Vercel deployment service for FastAPI applications."""
from pathlib import Path
from typing import Dict, Any
import json
import shutil
import sys

from ..utils import console, process_template_files, load_config, save_config

# Get the template directory
try:
    TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "services" / "vercel"
except Exception as e:
    console.print(f"❌ Error locating template directory: {e}", style="bold red")
    sys.exit(1)

def setup_vercel(project_dir: Path, project_name: str) -> None:
    """Set up Vercel configuration for the project.
    
    Args:
        project_dir: Root directory of the project
        project_name: Name of the project
    """
    vercel_dir = project_dir / ".vercel"
    vercel_dir.mkdir(exist_ok=True)
    
    # Create vercel.json
    vercel_config = {
        "version": 2,
        "builds": [
            {
                "src": "src/index.py",
                "use": "@vercel/python",
                "config": {
                    "maxLambdaSize": "15mb",
                    "pythonVersion": "3.9"
                }
            }
        ],
        "routes": [
            {
                "src": "/(.*)",
                "dest": "/src/index.py"
            }
        ]
    }
    
    with open(project_dir / "vercel.json", "w") as f:
        json.dump(vercel_config, f, indent=2)
    
    # Create .vercelignore
    vercelignore = """# Python
__pycache__/
*.py[cod]
*$py.class

# Virtual Environment
venv/
env/
.venv/

# Environment variables
.env
.env.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# Local development
*.log

# Testing
.coverage
htmlcov/
.pytest_cache/

# Build
dist/
build/
*.egg-info/

# Project specific
tests/
"""
    with open(project_dir / ".vercelignore", "w") as f:
        f.write(vercelignore)
    
    # Update requirements.txt for Vercel
    requirements_path = project_dir / "requirements.txt"
    if requirements_path.exists():
        with open(requirements_path, "a") as f:
            f.write("\n# Vercel specific\npython-multipart\n")
    
    console.print("✅ Vercel configuration added successfully!", style="bold green")
    console.print("\nTo deploy to Vercel:")
    console.print("1. Install Vercel CLI: npm install -g vercel")
    console.print("2. Run: vercel")
    console.print("3. Follow the prompts to deploy your application\n")

    # Update fastapi-gen.json
    config_path = project_dir / "fastapi-gen.json"
    config = load_config(config_path)
    services = config.get("services", [])
    if "vercel" not in services:
        services.append("vercel")
        config["services"] = services
        save_config(config_path, config)

def remove_vercel(project_dir: Path) -> None:
    """Remove Vercel configuration from the project.
    
    Args:
        project_dir: Root directory of the project
    """
    files_to_remove = [
        "vercel.json",
        ".vercelignore",
        ".vercel"
    ]
    
    for file_name in files_to_remove:
        path = project_dir / file_name
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    
    # Clean up requirements.txt
    requirements_path = project_dir / "requirements.txt"
    if requirements_path.exists():
        with open(requirements_path, "r") as f:
            lines = f.readlines()
        
        with open(requirements_path, "w") as f:
            for line in lines:
                if "# Vercel specific" not in line and "python-multipart" not in line:
                    f.write(line)

    # Update fastapi-gen.json
    config_path = project_dir / "fastapi-gen.json"
    config = load_config(config_path)
    services = config.get("services", [])
    if "vercel" in services:
        services.remove("vercel")
        config["services"] = services
        save_config(config_path, config)
    
    console.print("✅ Vercel configuration removed successfully!", style="bold green")
