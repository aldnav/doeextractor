import os
import subprocess
from logging import getLogger
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .constants import ExtractMethod, Formats
from .exceptions import NotFoundException

load_dotenv()
logger = getLogger(__name__)


TABULA_JAR_PATH = os.getenv("TABULA_JAR_PATH", None)
if TABULA_JAR_PATH is None:
    raise Exception("TABULA_JAR_PATH is not set")
if not os.path.exists(TABULA_JAR_PATH):
    raise Exception("Tabula jar file does not exist")


def _tabula(
    input_file_path=None,
    batch_directory=None,
    columns=None,
    output_format=Formats.CSV,
    extract_method=ExtractMethod.LATTICE,
    pages="1",
    password=None,
    area=None,
    guess=False,
    use_line_returns=False,
    output_file_path=None,  # If None, output to stdout
):
    """
    Run tabula
    """
    # Command looks like:
    # java -jar tabula-1.0.5-jar-with-dependencies.jar -l -f JSON --pages all reports/2022-05-18/petro_min_2022-may-10.pdf -o output.json
    command = ["java", "-jar", TABULA_JAR_PATH]
    command.append(extract_method.value)
    output_format = (
        output_format if isinstance(output_format, str) else output_format.value
    )
    command.extend(["-f", output_format])
    if area:
        command.extend(["--area", area])
    if guess:
        command.append("--guess")
    if columns:
        command.extend(["--columns", columns])
    command.extend(["--pages", pages])
    if password:
        command.extend(["--password", password])
    if use_line_returns:
        command.append("--use-line-returns")

    # Must be on the last part
    if batch_directory and input_file_path:
        raise TypeError("Cannot specify both batch_directory and input_file_path")
    if batch_directory is None and input_file_path is None:
        raise TypeError("Must specify either batch_directory or input_file_path")
    if batch_directory:
        command.extend(["--batch", str(Path(batch_directory).absolute())])
    elif input_file_path:
        command.append(str(Path(input_file_path).absolute()))
    if output_file_path:
        command.extend(["-o", str(Path(output_file_path).absolute())])
    print("Running tabula with this command:")
    print(" ".join(command))

    result = _run_tabula(command)
    return result.stdout.decode("utf-8")


def _java_version():
    try:
        result = subprocess.run(
            ["java", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            check=True,
        )
    except FileNotFoundError:
        raise NotFoundException("Java is not installed or not set in PATH")
    except subprocess.CalledProcessError as e:
        logger.error(
            "Error occured while running java:\n{}\n".format(e.stderr.decode("utf-8"))
        )
        raise
    return result.stdout.decode("utf-8")


def _run_tabula(command: Optional[list] = None):
    if not command:
        command = ["java", "-jar", TABULA_JAR_PATH, "-v"]
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            check=True,
        )
    except FileNotFoundError:
        raise NotFoundException("Tabula is not installed or not set in PATH")
    except subprocess.CalledProcessError as e:
        logger.error(
            "Error occured while running tabula:\n{}\n".format(e.stderr.decode("utf-8"))
        )
        raise
    return result


def _tabula_version():
    result = _run_tabula()  # command is for debug (default)
    return result.stdout.decode("utf-8")


def debug_info(silent=False):
    java_version = _java_version()
    tabula_version = _tabula_version()
    if silent:
        return
    return (
        f"DOE Extractor\n\n"
        + f"Java:\n"
        + f"{java_version}\n\n"
        + "Tabula:\n"
        + f"{tabula_version}"
    )


def extract(*args, **kwargs):
    """
    Extract data from PDFs using tabula
    """
    debug_info(silent=True)
    print(_tabula(*args, **kwargs))
