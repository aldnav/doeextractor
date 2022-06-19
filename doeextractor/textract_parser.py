import csv
import dataclasses
import hashlib
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from pprint import PrettyPrinter

from doeextractor import analyser
from doeextractor.models.fuel_line_price import FuelLinePriceItem, FuelPrice
from doeextractor.token_types import FEATURES, TOKEN_TYPES, UNCATEGORIZED

pp = PrettyPrinter(indent=2)


logger = logging.getLogger(__name__)


logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("log_file.log")
formatter = logging.Formatter(
    "%(asctime)s : %(name)s  : %(funcName)s : %(levelname)s : %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def clean(input_file_path: Path, overwrite=False):
    """
    Clean extracted tables.
    """
    input_file = Path(input_file_path, exists=True).absolute()
    output_file = input_file.with_suffix(".clean.csv")
    with open(input_file, "r") as input_file_obj:
        with open(output_file, "w") as output_file_obj:
            for line in input_file_obj:
                if line.startswith("Table:"):
                    continue
                if line.startswith("\n"):
                    continue
                if line.startswith("\r"):
                    continue
                if line.startswith("\r\n"):
                    continue
                output_file_obj.write(line)
    if overwrite:
        input_file.unlink()
        output_file.rename(input_file)
    return output_file


def _get_hash(data):
    """
    Get hash of input file.
    """
    m = hashlib.sha256()
    m.update(data)
    return m.hexdigest()


def _get_input_file_metadata(input_file_path: str):
    """
    Get metadata from input file.
    """
    try:
        file_contents = Path(input_file_path).read_bytes()
    except Exception as e:
        raise Exception(f"Error parsing input file: {e}")
    return _get_hash(file_contents)


def _clean_cell(text, is_header=False):
    text_entry = text.lower().strip()
    if "no branch" in text_entry or "outlet" in text_entry:
        text_entry = "no branch/outlet"
    elif text_entry.startswith("overall"):
        text_entry = "overall range"
    elif text_entry.startswith("common"):
        text_entry = "common price"
    elif text_entry.startswith("average"):
        text_entry = "average price"
    # elif re.match(PPriceRange, text_entry):
    #     # @NOTE Yields many potentially false positive results
    #     potential_range = len(text_entry.split(" ")) > 1
    #     if "-" not in text_entry and potential_range:
    #         text_entry = "-".join(text_entry.split(" "))
    if is_header:
        text_entry = text_entry.replace(" ", "_")
    return text_entry


def classify(text):
    """
    Classify text simplified for DOE reports
    """
    # Prefer simpler cases early
    text = text.lower().strip()
    token_type = TOKEN_TYPES.get("default")
    for feature, feature_func in FEATURES.items():
        if feature_func(text):
            token_type = TOKEN_TYPES[feature]
            break
    if token_type == UNCATEGORIZED:
        logger.debug("Uncategorized token: %s", text)
        print("Uncategorized token:", text)
    return token_type


def tokenize_input(input_file_path: str):
    """
    Tokenize input file.
    """
    input_file = Path(input_file_path, exists=True).absolute()
    skip_first_cell = False  # Skip first cell if header has region
    skip_last_cell = False  # Skip last cell if last cell is just empty/padding
    # Cities to correct. e.g. {"koronadal": "koronadal city"}
    corrections_for_cities = dict()
    with open(input_file, "r") as input_file_obj:
        reader = csv.reader(input_file_obj)
        raw_header = next(reader)
        # clean header
        print("[.] Getting headers")
        header = [_clean_cell(cell, is_header=True) for cell in raw_header]
        alternate_header = [_clean_cell(cell) for cell in raw_header]
        if len(header[0]) == 0 and header[1] == "area":
            # header has region in it
            header = header[1:]
            alternate_header = alternate_header[1:]
            skip_first_cell = True

        if len(header[-1]) == 0:
            # header has a padding
            header = header[:-1]
            alternate_header = alternate_header[:-1]
            skip_last_cell = True

        current_location = None
        last_product_identifier = "kerosene"  # TODO Constant?

        line_entry_data = []
        location_for_rows = []  # [()]
        index_with_no_location = -1
        context_row_idx = 0
        print("[.] Reading data")
        for row_idx, row in enumerate(reader):
            if skip_first_cell:
                row = row[1:]
            if skip_last_cell:
                row = row[:-1]
            row = [_clean_cell(cell) for cell in row]

            # Sometimes the header gets repeated
            if (
                row == header
                or row == alternate_header
                or row[:2] == ["cities", ""]
                or row[1:] == alternate_header[1:]
            ):
                continue

            # Get current location
            previous_location = current_location
            if len(row[0]) > 1:
                current_location = row[0]
            elif len(row[0]) == 0 and index_with_no_location == -1:
                index_with_no_location = context_row_idx
            elif len(row[0]) == 0 and current_location:
                # line_entry.area = current_location
                row[0] = current_location
            if current_location != previous_location:
                if (
                    current_location == "city"
                ):  # quite possibly the "city" part is split into the cell below
                    current_location = f"{previous_location} city"
                    if previous_location not in corrections_for_cities:
                        corrections_for_cities[previous_location] = current_location
                    # write back modification
                    row[0] = current_location

            if last_product_identifier in row:
                location_for_rows.append(
                    (index_with_no_location, context_row_idx, current_location)
                )
                # Last product identified, reset some variables
                current_location = None
                index_with_no_location = -1

            line_entry = row
            line_entry_data.append(line_entry)
            context_row_idx += 1

        # Corrections on locations
        print("[.] Correcting locations")
        # Do correction on location names
        for entry_idx, entry in enumerate(line_entry_data):
            entry_location = entry[0]
            if entry_location in corrections_for_cities:
                entry[0] = corrections_for_cities[entry_location]

        # Fill in blank locations
        while True:
            try:
                start_idx, end_idx, location = location_for_rows.pop(0)
            except IndexError:
                break
            else:
                for slice_row in line_entry_data[start_idx:end_idx]:
                    if slice_row[0] == "":
                        slice_row[0] = location

        # Break up merged lines
        print("[.] Breaking up merged lines")
        merged_rows = []  # [(source_idx, fixed_row)]
        inserts_done = 0
        for row_idx, line_entry in enumerate(line_entry_data):
            new_row = line_entry[:]
            to_insert = False
            if line_entry[1].endswith(" diesel"):
                # e.g. "ron 91 diesel"
                line_entry[1] = line_entry[1].replace(" diesel", "")
                # Fixing the source product
                line_entry[1] = line_entry[1].rsplit(" diesel")[0]
                # Fixing the new row
                new_row[1] = "diesel"  # Fix the product of new row
                to_insert = True
            elif re.match(r"^.*\s(ron)\s\d+$", line_entry[1]):
                line_entry[1], new_row[1] = re.findall(
                    r"ron\s\d+|kerosene", line_entry[1]
                )
                # TODO Not working. Gets rearranged
                # if line_entry[1] == "kerosene":
                #     # Do not copy all for new row since i t marks another start of entry
                #     try:
                #         new_row[0] = line_entry_data[row_idx + inserts_done + 1][0]
                #     except IndexError:
                #         new_row[0] = ""
                to_insert = True
            # Fixing merged prices
            for cell_idx, cell in enumerate(
                line_entry[2:]
            ):  # Index 2 is where prices start
                cell_split = cell.split(" ")
                for_prices = True
                try:
                    list(map(float, cell_split))
                except ValueError:
                    for_prices = False
                else:
                    if len(cell_split) % 2 == 0 and len(cell_split) > 2 and for_prices:
                        # Even number of elements, so it's probably a merged cell
                        # e.g. "81.60 81.60 82.40 82.40"
                        line_entry[cell_idx + 2] = " ".join(
                            cell_split[: len(cell_split) // 2]
                        )
                        new_row[cell_idx + 2] = " ".join(
                            cell_split[len(cell_split) // 2 :]
                        )
                        to_insert = True
            if to_insert:
                merged_rows.append((row_idx + inserts_done, new_row))
                inserts_done += 1

        # Re-insert merged rows
        if merged_rows:
            print(f"[.] Re-inserting merged {len(merged_rows)} rows")
        while True:
            try:
                insert_idx, new_row = merged_rows.pop(0)
            except IndexError:
                break
            else:
                line_entry_data.insert(insert_idx, new_row)

        # For debug purposes only
        # for row_idx, line_entry in enumerate(line_entry_data):
        #     print(row_idx, line_entry)

        return line_entry_data, header


def _build_data(parsed_data, header) -> list:
    """Parsed data is then transformed to the output format"""
    results = []
    for idx, data in enumerate(parsed_data):
        line_price_item = FuelLinePriceItem(
            municity=data[0],
            product=data[1],
            overall_range=data[-3],
            common_price=data[-2],
            average_price=data[-1],
        )
        price_cols = data[2:-3]
        company_cols = header[2:-3]
        line_price_item.prices = [
            FuelPrice(company=company, price=col_data)
            for col_data, company in zip(price_cols, company_cols)
        ]
        results.append(dataclasses.asdict(line_price_item))
    return results


def parse(input_file_path: str, output_file_path: str = None, clean_input=True):
    """
    Simple parser for extracted tables.
    """
    input_file = Path(input_file_path, exists=True).absolute()
    if clean_input:
        input_file = clean(input_file, overwrite=True)

    # Metadata
    metadata = {
        "query_datetime": datetime.now().isoformat(),
    }
    meta_hash = _get_input_file_metadata(input_file_path)
    metadata["meta_id"] = meta_hash

    # Tokenize
    tokens, header = tokenize_input(input_file_path)
    results = _build_data(tokens, header)
    analysis = analyser.analyse(results)
    response = {
        "metadata": metadata,
        "results": results,
        "analysis": analysis,
    }
    if not output_file_path:
        pp.pprint(response)
    else:
        full_output_path = str(Path(output_file_path).absolute())
        with open(full_output_path, "w") as f:
            json.dump(response, f, indent=2)
            print("Output file saved to:", full_output_path)
    print("[.] Done")

    return 0


if __name__ == "__main__":
    parse("/Users/aldnav/pro/doeextractor/samples/petro_min_2022-may-10.csv")
