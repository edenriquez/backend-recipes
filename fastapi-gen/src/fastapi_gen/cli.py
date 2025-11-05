"""
FastAPI Generator CLI application.
"""
import typer
from typing import Optional
from pathlib import Path
from rich.console import Console

# Initialize console
console = Console()

# Create Typer app
app = typer.Typer(
    name="fastapi-gen",
    help="CLI tool for generating FastAPI projects with clean architecture",
    add_completion=False,
)

# Commands
@app.command()
def create(
    project_name: str = typer.Argument(..., help="Name of the project to create"),
    output_dir: Path = typer.Option(
        ".", "--output", "-o", help="Directory to create the project in"
    ),
):
    """Create a new FastAPI project with clean architecture."""
    from pathlib import Path
    import shutil
    import re
    from datetime import datetime
    
    # Skip validation if using current directory
    if project_name != ".":
        # Validate project name for non-current directory cases
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', project_name):
            console.print(
                "❌ Error: Project name must be a valid Python identifier (letters, numbers, underscores, or hyphens, starting with a letter)",
                style="bold red"
            )
            raise typer.Exit(1)
    
    # Set up paths
    template_dir = Path(__file__).parent / "templates" / "base"
    
    # Handle output directory
    if str(output_dir) == "." and project_name == ".":
        # Special case: fastapi-gen create .
        project_dir = Path(".")
        if any(Path('.').iterdir()):
            console.print(
                "⚠️  Warning: Current directory is not empty. Some files may be overwritten.",
                style="bold yellow"
            )
    elif str(output_dir) == ".":
        # fastapi-gen create myproject
        project_dir = Path(project_name)
        if project_dir.exists() and any(project_dir.iterdir()):
            console.print(
                f"❌ Error: Directory '{project_dir}' already exists and is not empty",
                style="bold red"
            )
            raise typer.Exit(1)
    else:
        # fastapi-gen create myproject --output /some/path
        project_dir = output_dir / project_name
        output_dir.mkdir(parents=True, exist_ok=True)
        if project_dir.exists() and any(project_dir.iterdir()):
            console.print(
                f"❌ Error: Directory '{project_dir}' already exists and is not empty",
                style="bold red"
            )
            raise typer.Exit(1)
    
    console.print(f"Project will be created in: {project_dir.absolute()}")
    console.print(f"\n🚀 Creating new FastAPI project: {project_name}", style="bold green")
    
    try:
        # Create project directory
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy template files
        console.print("\n📁 Copying project files...")
        
        # Create a requirements.txt if it doesn't exist
        requirements_path = project_dir / "requirements.txt"
        if not requirements_path.exists():
            with open(requirements_path, 'w') as f:
                f.write("fastapi>=0.68.0\nuvicorn>=0.15.0\npython-multipart\npython-jose[cryptography]\npasslib[bcrypt]\npython-dotenv")
        
        # Process each file in the template
        for item in template_dir.rglob('*'):
            if item.is_file() and item.name != '.DS_Store':  # Skip system files
                # Get relative path from template directory
                rel_path = item.relative_to(template_dir)
                
                # Skip __pycache__ and other Python cache directories
                if '__pycache__' in rel_path.parts:
                    continue
                
                # For files in src/, we want to keep them directly in the project root
                dest_rel_path = rel_path
                
                # Create destination path
                dest_path = project_dir / dest_rel_path
                
                # Create parent directories if they don't exist
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Process file content
                content = item.read_text()
                
                # Replace placeholders in content
                content = content.replace('{{project_name}}', project_name)
                
                # For .j2 templates, remove the extension
                if item.suffix == '.j2':
                    dest_path = dest_path.with_suffix('')  # Remove .j2 extension
                
                # Write the processed content
                dest_path.write_text(content)
                
                # Show user-friendly path in output
                display_path = str(dest_rel_path)
                if item.suffix == '.j2':
                    display_path = str(dest_rel_path).replace('.j2', '')
                console.print(f"  ✓ Created: {display_path}")
        
        # Create .env file from example
        env_example = project_dir / ".env.example"
        if env_example.exists():
            shutil.copy2(env_example, project_dir / ".env")
            console.print("  ✓ Created: .env")
        
        console.print("\n✅ Project created successfully!", style="bold green")
        
        # Show next steps
        console.print("\nNext steps:")
        console.print(f"  cd {project_dir}")
        console.print("  pip install -r requirements.txt")
        console.print("  uvicorn src.index:app --reload\n")
        
        # Vercel deployment instructions
        console.print("\n🚀 Vercel Deployment:")
        console.print("  1. Make sure you have Vercel CLI installed: npm install -g vercel")
        console.print("  2. Run: vercel")
        console.print("  3. Follow the prompts to deploy your FastAPI application\n")
        
    except Exception as e:
        # Clean up in case of error
        if project_dir.exists():
            shutil.rmtree(project_dir)
        console.print(f"\n❌ Error creating project: {str(e)}", style="bold red")
        raise typer.Exit(1)

@app.command()
def add(
    service: str = typer.Argument(..., help="Service to add (e.g., rabbitmq, redis, oauth)"),
    project_path: Path = typer.Argument(
        ".", help="Path to the project directory"
    ),
):
    """Add a service to an existing project."""
    console.print(f"Adding service: {service}", style="bold blue")
    # Implementation will be added here

@app.command()
def remove(
    service: str = typer.Argument(..., help="Service to remove"),
    project_path: Path = typer.Argument(
        ".", help="Path to the project directory"
    ),
):
    """Remove a service from a project."""
    console.print(f"Removing service: {service}", style="bold yellow")
    # Implementation will be added here

@app.command()
def list_services():
    """List all available services that can be added."""
    services = ["rabbitmq", "redis", "oauth"]
    console.print("\nAvailable services:", style="bold")
    for service in services:
        console.print(f"- {service}")

# Main entry point
if __name__ == "__main__":
    app()
