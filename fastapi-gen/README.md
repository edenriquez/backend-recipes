# FastAPI Generator

A CLI tool for generating FastAPI projects with clean architecture and optional service integrations.

## Features

- 🚀 Generate new FastAPI projects with clean architecture
- 🔌 Add/remove services like RabbitMQ, Redis, and OAuth
- 🛠️ Easy to extend with new templates and services
- 🎨 Beautiful CLI interface with rich formatting

## Installation

```bash
# Install in development mode
pip install -e .
```

## Usage

```bash
# Create a new project
fastapi-gen create myproject

# Add services to a project
fastapi-gen add rabbitmq myproject
fastapi-gen add redis myproject
fastapi-gen add oauth myproject

# Remove a service
fastapi-gen remove redis myproject

# List available services
fastapi-gen list-services
```

## Development

### Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Running Tests

```bash
pytest
```

## License

MIT
