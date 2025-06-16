import pytest
from click.testing import CliRunner
from etl_forge.cli import cli


@pytest.fixture(scope="module")
def runner():
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@pytest.fixture(scope="module")
def cli_entry_point():
    """Fixture for the main CLI entry point."""
    return cli
