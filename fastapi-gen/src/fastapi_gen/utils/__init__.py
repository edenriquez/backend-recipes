"""Utility functions for the FastAPI Generator."""
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
import json
import shutil
from rich.console import Console

console = Console()

def _process_template_file(source: Path, dest: Path) -> None:
    """Process a single template file, handling both .j2 and regular files."""
    if source.suffix == '.j2':
        dest = dest.with_suffix('')
        console.print(f"  Creating: {dest.relative_to(dest.parents[1])}")
    else:
        console.print(f"  Copying: {dest.relative_to(dest.parents[1])}")
    shutil.copy2(source, dest)

def copy_template_files(template_dir: Path, 
                      destination: Path, 
                      context: Optional[Dict[str, Any]] = None) -> None:
    """Copy template files from source to destination, processing them as Jinja2 templates.
    
    Args:
        template_dir: Source directory containing template files
        destination: Target directory for processed files
        context: Optional context dictionary for template processing
    """
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")
    
    destination.mkdir(parents=True, exist_ok=True)
    
    for item in template_dir.iterdir():
        dest_path = destination / item.name
        
        if item.is_dir():
            copy_template_files(item, dest_path, context)
        else:
            _process_template_file(item, dest_path)

def _load_yaml_or_json(file_path: Path) -> Dict[str, Any]:
    """Load data from YAML or JSON file based on extension."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f) if file_path.suffix in ('.yaml', '.yml') else json.load(f)

def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from a YAML or JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dict containing the loaded configuration or empty dict if file doesn't exist
    """
    if not config_path.exists():
        return {}
    return _load_yaml_or_json(config_path)

def _dump_to_file(file_path: Path, data: Dict[str, Any]) -> None:
    """Dump data to file in appropriate format based on extension."""
    with open(file_path, 'w') as f:
        if file_path.suffix == '.json':
            json.dump(data, f, indent=2)
        else:
            yaml.dump(data, f, default_flow_style=False)

def save_config(config_path: Path, config: Dict[str, Any]) -> None:
    """Save configuration to a YAML or JSON file.
    
    Args:
        config_path: Path where to save the configuration
        config: Configuration data to save
    """
    config_path.parent.mkdir(parents=True, exist_ok=True)
    _dump_to_file(config_path, config)

def validate_project_path(project_path: Path) -> bool:
    """Validate if the given path contains a valid FastAPI project.
    
    Args:
        project_path: Path to validate as a FastAPI project
        
    Returns:
        bool: True if valid FastAPI project, False otherwise
    """
    required_files = ["pyproject.toml", "src"]
    return all((project_path / file).exists() for file in required_files)

def replace_in_file(file_path: Path, replacements: Dict[str, str]) -> None:
    """Replace placeholders in a file with actual values.
    
    Args:
        file_path: Path to the file to process
        replacements: Dictionary of placeholders and their replacements
    """
    try:
        content = file_path.read_text()
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        file_path.write_text(content)
    except Exception as e:
        raise RuntimeError(f"Error processing {file_path}: {str(e)}")

def process_template_files(project_dir: Path, project_name: str) -> None:
    """Process all template files in the project directory.
    
    Args:
        project_dir: Root directory of the project
        project_name: Name of the project to replace placeholders with
    """
    replacements = {
        "{{project_name}}": project_name,
        # Add other template variables here if needed
    }
    
    # Define file patterns to process
    patterns = [
        "*.py", "*.md", "*.toml", "*.yaml", "*.yml", "*.json",
        "Dockerfile", "Makefile", "*.sh"
    ]
    
    for pattern in patterns:
        for file_path in project_dir.rglob(pattern):
            if file_path.is_file() and not any(p.startswith('.') or p == '__pycache__' for p in file_path.parts):
                try:
                    replace_in_file(file_path, replacements)
                except Exception as e:
                    print(f"Warning: {e}")
