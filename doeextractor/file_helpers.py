import hashlib
import sqlite3
import tempfile
from pathlib import Path

from pdf2image import convert_from_path
from PIL import Image

DB_PATH = Path(__file__).parent.parent / "cache.db"


def get_checksum(file_path):
    """
    Calculates the checksum of a file.
    """
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def add_file_to_local_cache(file_path, output_file_path="") -> str:
    """
    Add file to local cache.
    """
    checksum = get_checksum(file_path)
    con = _get_or_create_cache()
    with con:
        cur = con.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO cache VALUES (?, ?, ?)",
            (checksum, str(file_path), str(output_file_path)),
        )
    return checksum


def _get_or_create_cache() -> sqlite3.Connection:
    """
    Get or create cache.
    """
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS cache (checksum TEXT PRIMARY KEY, file_path TEXT, output_file_path TEXT)"
    )
    return con


def is_file_already_analyzed(file_path):
    """
    Checks if a file is already analyzed.
    """
    checksum = get_checksum(file_path)
    with _get_or_create_cache() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM cache WHERE checksum = ?", (checksum,))
        first_result = cur.fetchone()
        return first_result is not None, first_result


def convert_pdf_to_png(file_path, merge_pages=False) -> Path:
    """
    Convert a PDF file to PNG.
    """
    if merge_pages:
        output_file_path = (
            Path(__file__).parent.parent / "output" / (file_path.stem + ".png")
        )
        if output_file_path.exists():
            print("Output file already exists.")
            return output_file_path.absolute()
    else:
        output_file_dir = Path(__file__).parent.parent / "output" / file_path.stem
        has_files = False
        try:
            has_files = len(list(output_file_dir.iterdir())) > 0
        except FileNotFoundError:
            pass
        if has_files:
            print("Output directory already exists and is not empty.")
            return output_file_dir.absolute()
        else:
            output_file_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as path:
        images_from_path = convert_from_path(file_path, output_folder=path)

        if merge_pages:
            new_width = images_from_path[0].size[0]
            new_heigth = images_from_path[0].size[1] * len(images_from_path)
            new_image = Image.new("RGB", (new_width, new_heigth), color=(255, 255, 255))
            for i, image in enumerate(images_from_path):
                new_image.paste(image, (0, i * image.size[1]))
            # TODO make output directory a variable
            output_dir = Path(__file__).parent.parent / "output"
            new_image.save(output_file_path, format="PNG")
            print("Saved to " + str(output_file_path))
            return output_file_path.absolute()
        else:
            for i, image in enumerate(images_from_path):
                new_image = Image.new("RGB", image.size, color=(255, 255, 255))
                new_image.paste(image)
                new_image.save(output_file_dir / (str(i) + ".png"), format="PNG")
            print(f"Saved {len(images_from_path)} pages to {str(output_file_dir)}")
            return output_file_dir.absolute()
