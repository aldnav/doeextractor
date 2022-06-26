"""Console script for doeextractor."""
import sys

import click

from doeextractor.constants import ExtractMethod, Formats

from .parser import parse as do_parse
from .tabula import debug_info
from .tabula import extract as do_extract
from .textract_parser import parse as do_textract_parse
from .textractor import extract as do_textract


@click.group()
def cli():
    """Console script for doeextractor."""
    # click.echo("Main CLI")
    return 0


@cli.command(
    help="Extract tables from a PDF file using Tabula",
)
@click.option(
    "-a",
    "--area",
    default=None,
    help="""
    Portion of the page to analyze.\n
    Example: --area 269.875,12.75,790.5,561.
    """,
)
@click.option(
    "-b",
    "--batch",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="Convert all .pdfs in the provided directory.",
)
@click.option(
    "-c",
    "--columns",
    help="""X coordinates of column boundaries. Example
                            --columns 10.1,20.2,30.3. If all values are
                            between 0-100 (inclusive) and preceded by '%',
                            input will be taken as % of actual width of
                            the page. Example: --columns %25,50,80.6""",
)
@click.option(
    "-f",
    "--output-format",
    type=click.Choice(list(Formats.__members__.keys()), case_sensitive=False),
    default=Formats.CSV.name,
    show_default=True,
)
@click.option(
    "-e",
    "--extract-method",
    type=click.Choice(list(ExtractMethod.__members__.keys()), case_sensitive=False),
    default=ExtractMethod.LATTICE.name,
    show_default=True,
)
@click.option(
    "-g",
    "--guess",
    is_flag=True,
    show_default=True,
    default=False,
    help="Guess the portion of the page to analyze per page.",
)
@click.option(
    "-p",
    "--pages",
    help="""
    Comma separated list of ranges, or all.
    Examples: --pages 1-3,5-7, --pages 3 or
    --pages all. Default is --pages 1
    """,
    default="1",
)
@click.option(
    "-s",
    "--password",
    help="Password to decrypt document. Default is empty",
)
@click.option(
    "-u",
    "--use-line-returns",
    is_flag=True,
    show_default=True,
    default=False,
    help="""Use embedded line returns in cells. (Only in
                            spreadsheet mode.)""",
)
@click.option(
    "-i",
    "--input_file_path",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
)
@click.option(
    "-o",
    "--output_file_path",
    type=click.Path(dir_okay=False, file_okay=True, writable=True),
)
def tabula_extract(
    area,
    batch,
    columns,
    output_format,
    extract_method,
    guess,
    pages,
    password,
    use_line_returns,
    input_file_path,
    output_file_path,
):
    extract_method_value = ExtractMethod[extract_method]
    do_extract(
        area=area,
        batch_directory=batch,
        columns=columns,
        output_format=output_format,
        extract_method=extract_method_value,
        guess=guess,
        pages=pages,
        password=password,
        use_line_returns=use_line_returns,
        input_file_path=input_file_path,
        output_file_path=output_file_path,
    )
    return 0


@cli.command(help="Extract tables from a PDF file using Amazon Textract")
@click.argument(
    "input_file_path",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
)
def extract(input_file_path):
    do_textract(
        input_file_path=input_file_path,
    )
    return 0


@cli.command(help="Debug info for DOE Extractor")
def show_debug_info():
    click.echo(debug_info())
    return 0


@cli.command(help="Parse extracted tables from Tabula")
@click.argument(
    "input_file_path", type=click.Path(exists=True, dir_okay=False, file_okay=True)
)
@click.option(
    "-o",
    "--output_file_path",
    type=click.Path(dir_okay=False, file_okay=True, writable=True),
)
def tabula_parse(input_file_path, output_file_path):
    click.echo("Parse extracted tables")
    do_parse(input_file_path, output_file_path)
    return 0


@cli.command(help="Parse extracted tables from Amazon Textract")
@click.argument(
    "input_file_path", type=click.Path(exists=True, dir_okay=False, file_okay=True)
)
@click.option(
    "-o",
    "--output_file_path",
    type=click.Path(dir_okay=False, file_okay=True, writable=True),
)
@click.option(
    "-c",
    "--clean",
    is_flag=True,
    default=False,
)
def parse(input_file_path, output_file_path, clean):
    click.echo("Parse extracted tables")
    do_textract_parse(input_file_path, output_file_path, clean_input=clean)
    return 0


main = cli


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
