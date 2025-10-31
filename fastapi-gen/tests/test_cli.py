""Tests for the FastAPI Generator CLI."""
import pytest
from typer.testing import CliRunner
from fastapi_gen.cli import app

runner = CliRunner()

def test_create_command():
    ""Test the create command."""
    result = runner.invoke(app, ["create", "testproject"])
    assert result.exit_code == 0
    assert "Creating new FastAPI project: testproject" in result.output

def test_add_command():
    ""Test the add command."""
    result = runner.invoke(app, ["add", "redis", "testproject"])
    assert result.exit_code == 0
    assert "Adding service: redis" in result.output

def test_remove_command():
    ""Test the remove command."""
    result = runner.invoke(app, ["remove", "redis", "testproject"])
    assert result.exit_code == 0
    assert "Removing service: redis" in result.output

def test_list_services_command():
    ""Test the list-services command."""
    result = runner.invoke(app, ["list-services"])
    assert result.exit_code == 0
    assert "Available services:" in result.output
    assert "- rabbitmq" in result.output
    assert "- redis" in result.output
    assert "- oauth" in result.output
