"""
FastAPI Generator CLI application.
"""
import typer
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from rich.console import Console

# Import utility functions
from .utils import (
    copy_template_files,
    validate_project_path,
    save_config,
    load_config
)

# Import services
from .services import setup_vercel, remove_vercel

# Define available services and their handlers
SERVICES = {
    "vercel": {
        "setup": setup_vercel,
        "remove": remove_vercel,
        "description": "Vercel deployment configuration"
    },
    # Add more services here
}

# Initialize console
console = Console()

# Create Typer app
app = typer.Typer(
    name="fastapi-gen",
    help="CLI tool for generating FastAPI projects with clean architecture",
    add_completion=False,
)

def _is_valid_project_name(name: str) -> bool:
    """Validate project name format."""
    return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name))

def _setup_project_directory(
    project_name: str, 
    output_dir: Path
) -> Path:
    """Set up and validate the project directory."""
    if project_name == ".":
        project_dir = Path(".")
        if any(project_dir.iterdir()):
            console.print(
                "⚠️  Warning: Current directory is not empty. Some files may be overwritten.",
                style="bold yellow"
            )
    else:
        project_dir = output_dir / project_name
        if project_dir.exists() and any(project_dir.iterdir()):
            console.print(
                f"❌ Error: Directory '{project_dir}' already exists and is not empty",
                style="bold red"
            )
            raise typer.Exit(1)
    
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir

# Commands
@app.command()
def create(
    project_name: str = typer.Argument(..., help="Name of the project to create"),
    output_dir: Path = typer.Option(
        ".", "--output", "-o", help="Directory to create the project in"
    ),
):
    """Create a new FastAPI project with clean architecture."""
    # Validate project name for non-current directory cases
    if project_name != "." and not _is_valid_project_name(project_name):
        console.print(
            "❌ Error: Project name must be a valid Python identifier "
            "(letters, numbers, underscores, or hyphens, starting with a letter)",
            style="bold red"
        )
        raise typer.Exit(1)
    
    # Set up paths
    template_dir = Path(__file__).parent / "templates" / "base"
    
    try:
        # Set up and validate project directory
        project_dir = _setup_project_directory(project_name, output_dir)
        console.print(f"Project will be created in: {project_dir.absolute()}")
        console.print(f"\n🚀 Creating new FastAPI project: {project_name}", style="bold green")
        
        # Copy template files
        console.print("\n📁 Copying project files...")
        copy_template_files(template_dir, project_dir)
        
        # Process template files to replace placeholders
        from .utils import process_template_files
        try:
            process_template_files(project_dir, project_name)
        except Exception as e:
            console.print(f"⚠️  Warning: Failed to process template variables: {e}", style="bold yellow")
        
        # Create or update project configuration
        config_path = project_dir / "fastapi-gen.json"
        config = load_config(config_path)
        config.update({
            "project_name": project_name,
            "created_at": str(typer.get_app_dir("fastapi-gen")),
        })
        save_config(config_path, config)
        
        # Validate the created project structure
        if not validate_project_path(project_dir):
            console.print(
                "⚠️  Warning: The generated project structure might be incomplete.",
                style="bold yellow"
            )
        
        console.print("\n✅ Project created successfully!", style="bold green")
        console.print(f"\nTo get started, run:\n\n    cd {project_dir}\n    pip install -r requirements.txt\n    uvicorn src.main:app --reload\n")
        
        # Show next steps
        console.print("\nNext steps:")
        console.print(f"  cd {project_dir}")
        console.print("  pip install -r requirements.txt")
        console.print("  uvicorn src.main:app --reload\n")
    
    except Exception as e:
        console.print(f"\n❌ Error creating project: {str(e)}", style="bold red")
        raise typer.Exit(1)
@app.command()
def add(
    service: str = typer.Argument(..., help="Service to add (e.g., vercel, redis, postgres)"),
    project_path: Path = typer.Argument(
        ".", help="Path to the project directory"
    ),
):
    """Add a service to an existing project."""
    project_path = project_path.absolute()
    if not validate_project_path(project_path):
        console.print("❌ Error: Not a valid FastAPI project directory", style="bold red")
        raise typer.Exit(1)
    
    if service not in SERVICES:
        console.print(f"❌ Error: Unknown service '{service}'", style="bold red")
        console.print("\nAvailable services:", style="bold")
        for name, svc in SERVICES.items():
            console.print(f"- {name}: {svc['description']}")
        raise typer.Exit(1)
    
    console.print(f"\n🛠️  Adding {service} service...", style="bold blue")
    try:
        SERVICES[service]["setup"](project_path, project_path.name)
        console.print(f"✅ Successfully added {service} service", style="bold green")
    except Exception as e:
        console.print(f"❌ Error adding {service} service: {str(e)}", style="bold red")
        raise typer.Exit(1)

@app.command()
def remove(
    service: str = typer.Argument(..., help="Service to remove"),
    project_path: Path = typer.Argument(
        ".", help="Path to the project directory"
    ),
):
    """Remove a service from a project."""
    project_path = project_path.absolute()
    if not validate_project_path(project_path):
        console.print("❌ Error: Not a valid FastAPI project directory", style="bold red")
        raise typer.Exit(1)
    
    if service not in SERVICES:
        console.print(f"❌ Error: Unknown service '{service}'", style="bold red")
        console.print("\nAvailable services:", style="bold")
        for name, svc in SERVICES.items():
            console.print(f"- {name}: {svc['description']}")
        raise typer.Exit(1)
    
    console.print(f"\n🗑️  Removing {service} service...", style="bold blue")
    try:
        SERVICES[service]["remove"](project_path)
        console.print(f"✅ Successfully removed {service} service", style="bold green")
    except Exception as e:
        console.print(f"❌ Error removing {service} service: {str(e)}", style="bold red")
        raise typer.Exit(1)

@app.command()
def list_services():
    """List all available services that can be added."""
    if not SERVICES:
        console.print("\nNo services available.", style="bold")
        return
        
    console.print("\nAvailable services:", style="bold")
    for name, svc in SERVICES.items():
        console.print(f"- {name}: {svc['description']}")

# Main entry point
if __name__ == "__main__":
    app()
