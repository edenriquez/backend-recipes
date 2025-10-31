""Utility functions for the FastAPI Generator."""
from pathlib import Path
from typing import Any, Dict
import yaml
import json
import shutil
from rich.console import Console

console = Console()

def copy_template_files(template_dir: Path, destination: Path, context: Dict[str, Any] = None):
    """Copy template files from source to destination, processing them as Jinja2 templates."""
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")
    
    destination.mkdir(parents=True, exist_ok=True)
    
    for item in template_dir.iterdir():
        dest_path = destination / item.name
        
        if item.is_dir():
            copy_template_files(item, dest_path, context)
        else:
            if item.suffix == '.j2':
                # Process as template
                dest_path = dest_path.with_suffix('')  # Remove .j2 extension
                console.print(f"  Creating: {dest_path.relative_to(destination.parent)}")
                # TODO: Add Jinja2 template processing
                shutil.copy2(item, dest_path)
            else:
                # Copy as-is
                console.print(f"  Copying: {dest_path.relative_to(destination.parent)}")
                shutil.copy2(item, dest_path)

def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from a YAML or JSON file."""
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r') as f:
        if config_path.suffix == '.json':
            return json.load(f)
        return yaml.safe_load(f) or {}

def save_config(config_path: Path, config: Dict[str, Any]):
    """Save configuration to a YAML or JSON file."""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        if config_path.suffix == '.json':
            json.dump(config, f, indent=2)
        else:
            yaml.dump(config, f, default_flow_style=False)

def validate_project_path(project_path: Path) -> bool:
    """Validate if the given path contains a valid FastAPI project."""
    required_files = ["pyproject.toml", "src"]
    return all((project_path / file).exists() for file in required_files)
