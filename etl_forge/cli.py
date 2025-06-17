"""
Command-line interface for ETLForge.
"""

import click
from .generator import DataGenerator
from .validator import DataValidator
from .exceptions import ETLForgeError
from . import __version__


@click.group()
@click.version_option(version=__version__, prog_name="etl-forge")
def cli():
    """ETLForge - Generate synthetic test data and validate ETL outputs."""
    pass


@cli.command()
@click.option(
    "--schema",
    "-s",
    required=True,
    type=click.Path(exists=True),
    help="Path to schema file (YAML or JSON)",
)
@click.option(
    "--rows",
    "-r",
    default=100,
    type=int,
    help="Number of rows to generate (default: 100)",
)
@click.option(
    "--output",
    "-o",
    required=True,
    type=click.Path(),
    help="Output file path (CSV or Excel)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "excel"], case_sensitive=False),
    help="Output format (auto-detected from file extension if not specified)",
)
def generate(schema, rows, output, format):
    """Generate synthetic test data based on a schema."""
    try:
        click.echo(f"Loading schema from: {schema}")
        generator = DataGenerator(schema)

        click.echo(f"Generating {rows} rows of synthetic data...")
        df = generator.generate_data(rows)

        click.echo(f"Saving data to: {output}")
        generator.save_data(df, output, format)

        click.echo(
            click.style(f"✅ Successfully generated {len(df)} rows.", fg="green")
        )

    except ETLForgeError as e:
        click.echo(click.style(f"❌ Schema/Generation Error: {e}", fg="red"), err=True)
        click.echo(click.style("💡 Tip: Check your schema file format and field definitions", fg="yellow"), err=True)
        raise click.Abort()
    except FileNotFoundError as e:
        click.echo(click.style(f"❌ File not found: {e}", fg="red"), err=True)
        click.echo(click.style("💡 Tip: Verify that all file paths are correct", fg="yellow"), err=True)
        raise click.Abort()
    except PermissionError as e:
        click.echo(click.style(f"❌ Permission denied: {e}", fg="red"), err=True)
        click.echo(click.style("💡 Tip: Check file/directory permissions", fg="yellow"), err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected error: {e}", fg="red"), err=True)
        click.echo(click.style("💡 Please report this issue at: https://github.com/kkartas/etl-forge/issues", fg="yellow"), err=True)
        raise click.Abort()


@cli.command()
@click.option(
    "--input",
    "-i",
    required=True,
    type=click.Path(exists=True),
    help="Path to input data file (CSV or Excel)",
)
@click.option(
    "--schema",
    "-s",
    required=True,
    type=click.Path(exists=True),
    help="Path to schema file (YAML or JSON)",
)
@click.option(
    "--report",
    "-r",
    type=click.Path(),
    help="Path to save invalid rows report (optional)",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed validation errors for up to the first 20 invalid records")
def check(input, schema, report, verbose):
    """Validate data against a schema."""
    try:
        click.echo(f"Loading schema from: {schema}")
        validator = DataValidator(schema)

        click.echo(f"Loading data from: {input}")
        click.echo("Running validation checks...")

        result = validator.validate_and_report(input, report)

        # Print summary
        validator.print_validation_summary(result)

        if report and result.invalid_rows:
            click.echo(f"📄 Invalid rows report saved to: {report}")

        if verbose and not result.is_valid:
            click.echo("\nDetailed Errors:")
            click.echo("-" * 40)
            for i, error in enumerate(
                result.errors[:20], 1
            ):  # Limit to first 20 errors
                row_info = f" (row {error['row']})" if error["row"] is not None else ""
                click.echo(
                    f"{i}. {error['type']} in column '{error['column']}'{row_info}"
                )
                if error["message"]:
                    click.echo(f"   {error['message']}")

            if len(result.errors) > 20:
                click.echo(f"   ... and {len(result.errors) - 20} more errors")

        if result.is_valid:
            click.echo(click.style("✅ Validation PASSED", fg="green"))
        else:
            click.echo(click.style("❌ Validation FAILED", fg="red"), err=True)
            # Use exit code 1 to indicate failure, which is more standard for CLI tools
            # than click.Abort() which prints "Aborted!".
            ctx = click.get_current_context()
            ctx.exit(1)

    except ETLForgeError as e:
        click.echo(click.style(f"❌ Schema/Validation Error: {e}", fg="red"), err=True)
        click.echo(click.style("💡 Tip: Check your schema file format and data structure", fg="yellow"), err=True)
        raise click.Abort()
    except FileNotFoundError as e:
        click.echo(click.style(f"❌ File not found: {e}", fg="red"), err=True)
        click.echo(click.style("💡 Tip: Verify that all file paths are correct", fg="yellow"), err=True)
        raise click.Abort()
    except PermissionError as e:
        click.echo(click.style(f"❌ Permission denied: {e}", fg="red"), err=True)
        click.echo(click.style("💡 Tip: Check file/directory permissions", fg="yellow"), err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(click.style(f"❌ Unexpected error: {e}", fg="red"), err=True)
        click.echo(click.style("💡 Please report this issue at: https://github.com/kkartas/etl-forge/issues", fg="yellow"), err=True)
        raise click.Abort()


@cli.command("create-schema")
@click.argument("schema_path", type=click.Path())
def create_example_schema(schema_path):
    """Create an example schema file."""
    example_schema = {
        "fields": [
            {
                "name": "id",
                "type": "int",
                "unique": True,
                "nullable": False,
                "range": {"min": 1, "max": 10000},
            },
            {
                "name": "name",
                "type": "string",
                "nullable": False,
                "length": {"min": 5, "max": 20},
                "faker_template": "name",
            },
            {
                "name": "email",
                "type": "string",
                "nullable": False,
                "unique": True,
                "faker_template": "email",
            },
            {
                "name": "age",
                "type": "int",
                "nullable": False,
                "range": {"min": 18, "max": 80},
            },
            {
                "name": "salary",
                "type": "float",
                "nullable": True,
                "range": {"min": 30000.0, "max": 150000.0},
                "precision": 2,
            },
            {
                "name": "department",
                "type": "category",
                "nullable": False,
                "values": ["Engineering", "Marketing", "Sales", "HR", "Finance"],
            },
            {
                "name": "hire_date",
                "type": "date",
                "nullable": False,
                "range": {"start": "2020-01-01", "end": "2024-12-31"},
                "format": "%Y-%m-%d",
            },
        ]
    }

    import yaml

    with open(schema_path, "w") as f:
        yaml.dump(example_schema, f, default_flow_style=False, indent=2)

    click.echo(f"✅ Example schema created at: {schema_path}")


if __name__ == "__main__":
    cli()
