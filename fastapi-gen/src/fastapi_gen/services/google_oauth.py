"""Google OAuth integration service."""
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import tomlkit
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False

from ..utils import console, load_config, save_config

def _add_dependency_to_toml(project_dir: Path, dependency: str) -> None:
    """Add a dependency to pyproject.toml if it doesn't already exist."""
    if not TOML_AVAILABLE:
        console.print("⚠️  tomlkit not available. Please install it with 'pip install tomlkit'", style="bold yellow")
        return
        
    pyproject_path = project_dir / "pyproject.toml"
    if not pyproject_path.exists():
        return
        
    with open(pyproject_path, "r") as f:
        pyproject = tomlkit.parse(f.read())
    
    # Check if dependency already exists
    deps = pyproject.get("project", {}).get("dependencies", [])
    if not any(dep.startswith(dependency.split("[")[0]) for dep in deps):
        deps.append(dependency)
        pyproject["project"]["dependencies"] = deps
        
        with open(pyproject_path, "w") as f:
            f.write(tomlkit.dumps(pyproject))

def _copy_oauth_templates(project_dir: Path) -> None:
    """Copy OAuth template files to the project.
    
    Args:
        project_dir: Root directory of the project
    """
    try:
        # Get the template directory
        template_dir = Path(__file__).parent.parent / "templates" / "services" / "google_oauth"
        
        if not template_dir.exists():
            raise FileNotFoundError(f"Google OAuth template directory not found: {template_dir}")
        
        console.print("\n📁 Copying Google OAuth templates...", style="bold blue")
        
        # Copy all template files to the project
        for src_file in template_dir.rglob("*"):
            if src_file.is_file():
                # Calculate the relative path from the template directory
                rel_path = src_file.relative_to(template_dir)
                dest_path = project_dir / rel_path
                
                # Create the destination directory if it doesn't exist
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy the file
                shutil.copy2(src_file, dest_path)
                console.print(f"  Added: {rel_path}")
        
        # Add dependencies to pyproject.toml
        _add_dependency_to_toml(project_dir, "python-jose[cryptography]>=3.3.0")
        _add_dependency_to_toml(project_dir, "aiohttp>=3.8.0")
        _add_dependency_to_toml(project_dir, "python-multipart>=0.0.5")
        
    except Exception as e:
        console.print(f"❌ Error copying OAuth templates: {e}", style="bold red")
        raise

def setup_google_oauth(project_dir: Path, project_name: str = "") -> None:
    """Set up Google OAuth for the project.

    Args:
        project_dir: Root directory of the project
        project_name: Name of the project (unused, kept for consistency with other services)
    """
    try:
        # Create or update .env file
        env_file = project_dir / ".env"
        if not env_file.exists():
            with open(env_file, "w") as f:
                f.write("""# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
""")
        else:
            # Append to existing .env file if needed variables are missing
            with open(env_file, "r+") as f:
                content = f.read()
                if "GOOGLE_CLIENT_ID" not in content:
                    f.write("""
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
""")
                if "SECRET_KEY" not in content:
                    f.write("""
# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
""")
        
        # Copy template files
        _copy_oauth_templates(project_dir)

        # Update fastapi-gen.json
        config_path = project_dir / "fastapi-gen.json"
        config = load_config(config_path)
        services = config.get("services", [])
        if "google_oauth" not in services:
            services.append("google_oauth")
            config["services"] = services
            save_config(config_path, config)

        console.print("\n✅ Google OAuth setup successfully!", style="bold green")
        console.print("\nNext steps:", style="bold")
        console.print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
        console.print("2. Create a new project or select an existing one")
        console.print("3. Navigate to 'APIs & Services' > 'Credentials'")
        console.print("4. Create an OAuth 2.0 Client ID")
        console.print("5. Add authorized redirect URIs (e.g., http://localhost:8000/auth/google/callback)")
        console.print("6. Update the .env file with your credentials and settings")
        console.print("\nYour OAuth endpoints are available at:")
        console.print("  - GET /auth/google - Start Google OAuth flow")
        console.print("  - GET /auth/google/callback - OAuth callback (handled automatically)")
        console.print("  - GET /auth/me - Get current user info (requires authentication)", style="yellow")
        
    except Exception as e:
        console.print(f"❌ Error setting up Google OAuth: {e}", style="bold red")
        raise

def remove_google_oauth(project_dir: Path) -> None:
    """Remove Google OAuth configuration from the project.

    Args:
        project_dir: Root directory of the project
    """
    try:
        # Files to remove
        files_to_remove = [
            project_dir / "src" / "infrastructure" / "services" / "oauth_utils.py",
            project_dir / "src" / "infrastructure" / "services" / "auth_service.py",
            project_dir / "src" / "infrastructure" / "api" / "v1" / "endpoints" / "auth.py",
        ]
        
        # Remove files
        removed = False
        for file_path in files_to_remove:
            if file_path.exists():
                file_path.unlink()
                console.print(f"✅ Removed: {file_path.relative_to(project_dir)}")
                removed = True
        
        # Update fastapi-gen.json
        config_path = project_dir / "fastapi-gen.json"
        if config_path.exists():
            config = load_config(config_path)
            services = config.get("services", [])
            if "google_oauth" in services:
                services.remove("google_oauth")
                config["services"] = services
                save_config(config_path, config)
                console.print("✅ Updated fastapi-gen.json")
        
        if removed:
            console.print("\n✅ Google OAuth removed successfully!", style="bold green")
            console.print("Note: Environment variables in .env were not removed. Please remove them manually if needed.", style="yellow")
        else:
            console.print("ℹ️  No Google OAuth files found to remove", style="yellow")
            
    except Exception as e:
        console.print(f"❌ Error removing Google OAuth: {e}", style="bold red")
        raise
