import dataclasses
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=2)

from doeextractor.models import FuelLinePriceItem, FuelPrice

from .token_types import (
    FEATURES,
    TOKEN_TYPES,
    TYPE_BRAND,
    TYPE_CITY,
    TYPE_HEADER,
    TYPE_NONE_TYPE,
    TYPE_PRICE,
    TYPE_PRODUCT_TYPE,
    UNCATEGORIZED,
)

logger = logging.getLogger(__name__)


logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("log_file.log")
formatter = logging.Formatter(
    "%(asctime)s : %(name)s  : %(funcName)s : %(levelname)s : %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


class Token:
    def __init__(self, value, token_type: str) -> None:
        self.value = value
        self.token_type = token_type

    def __str__(self) -> str:
        return f"{self.value} ({self.token_type})"

    __repr__ = __str__

    def is_overall_range_header(self) -> bool:
        return self.token_type == "header" and self.value.lower() == "overall range"


def _clean(text_entries: list):
    """
    Clean text entries.
    """
    to_split = []  # [(start_index, text1), (start_index+1, text2)]

    # Normalize entries
    for idx, text_entry in enumerate(text_entries):
        text_entry = text_entry.lower().strip()
        if "no branch" in text_entry or text_entry == "outlet":
            text_entry = "no branch/outlet"
        elif text_entry == "overall":
            text_entry = "overall range"
        elif text_entry == "common":
            text_entry = "common price"
        elif text_entry == "average":
            text_entry = "average price"
        elif text_entry == "noneron 95":
            text_entry = "none"
            to_split.append((idx + 1, "ron 95"))
        elif text_entry == "-none":
            text_entry = "none"
        text_entries[idx] = text_entry  # write back modifications

    # Insert entries needed
    for idx, text_entry in to_split:
        text_entries.insert(idx, text_entry)

    yield from text_entries


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


def tokenize(text_data: list):
    cleaned_text = _clean(text_data)
    while True:
        try:
            text = next(cleaned_text)
        except StopIteration:
            break
        else:
            yield Token(text, classify(text))


def _get_hash(data):
    """
    Get hash of input file.
    """
    m = hashlib.sha256()
    m.update(data)
    return m.hexdigest()


def _build_data(tokens) -> list:
    # TODO: Something wrong with the input data especially when report includes "NO BRANCH/OUTLET"
    data = []

    # 1. Identify from header row the sequence of fuel providers (oil company)
    # Typical sequence of the header:
    # [Area, Product, Company 1, ..., Company N, Overall Range, Common Price, Average Price]
    header_slice = tokens[:20]  # TODO: Make it configurable
    fuel_provider_sequence_start = None
    fuel_provider_sequence_end = None
    first_fuel_provider_is_found = False
    for idx, token in enumerate(header_slice):
        if not first_fuel_provider_is_found:
            if token.token_type == "brand":
                fuel_provider_sequence_start = idx
                first_fuel_provider_is_found = True
        elif token.is_overall_range_header():
            fuel_provider_sequence_end = idx
            break
    if fuel_provider_sequence_start is None or fuel_provider_sequence_end is None:
        raise Exception("Could not identify fuel provider sequence")
    header_end = fuel_provider_sequence_end + 3

    fuel_provider_sequence = header_slice[
        fuel_provider_sequence_start:fuel_provider_sequence_end
    ]
    full_header = tokens[0:header_end]
    # 2. Start complete sequence
    current_line_price_item = None
    adding_prices = False
    iter_fuel_provider_and_prices_sequence = iter(
        header_slice[fuel_provider_sequence_start : fuel_provider_sequence_end + 3]
    )  # Additional headers are "Overall, common, and average"
    current_city = None
    for idx, token in enumerate(tokens):
        if token.token_type == TYPE_HEADER:
            continue
        if token.token_type == TYPE_CITY:
            # 3. Start populating an entry
            current_city = token.value
            # TODO Check if completed line item before creating a new one?

        if token.token_type == TYPE_PRODUCT_TYPE:
            current_line_price_item = FuelLinePriceItem(
                municity=current_city,
                product=token.value,
            )
            adding_prices = True
        # 4. Adding prices
        if adding_prices:
            if token.token_type in [TYPE_NONE_TYPE, TYPE_PRICE]:
                # Get which brand/header
                try:
                    fuel_provider = next(iter_fuel_provider_and_prices_sequence)
                except StopIteration:
                    adding_prices = False
                    data.append(dataclasses.asdict(current_line_price_item))
                    iter_fuel_provider_and_prices_sequence = iter(
                        header_slice[
                            fuel_provider_sequence_start : fuel_provider_sequence_end
                            + 3
                        ]
                    )
                else:
                    if fuel_provider.token_type == TYPE_BRAND:
                        current_line_price_item.prices.append(
                            FuelPrice(company=fuel_provider.value, price=token.value)
                        )
                    elif fuel_provider.value == "overall range":
                        current_line_price_item.overall_range = token.value
                    elif fuel_provider.value == "common price":
                        current_line_price_item.common_price = token.value
                    elif fuel_provider.value == "average price":
                        current_line_price_item.average_price = token.value
    return data


def parse(input_file_path: str, output_file_path: str = None):
    """
    Simple parser for extracted tables.
    """
    # Metadata
    metadata = {
        "query_datetime": datetime.now().isoformat(),
    }

    try:
        file_contents = Path(input_file_path).read_bytes()
        raw_data = json.loads(file_contents)
    except json.JSONDecodeError:
        raise Exception("Input file is not a valid JSON file")
    except Exception as e:
        raise Exception(f"Error parsing input file: {e}")
    meta_hash = _get_hash(file_contents)
    metadata["meta_id"] = meta_hash
    # TODO Ask interactively to continue parse if there exists the same hash as input file

    all_text = []
    for page in raw_data:
        for data in page.get("data", []):
            for entry in data:
                # if entry.get("text"):  # NOTE Maybe the blank texts are important?
                all_text.append(entry["text"].lower())

    tokens = list(tokenize(all_text))
    results = _build_data(tokens)

    response = {
        "metadata": metadata,
        "results": results,
    }
    if not output_file_path:
        pp.pprint(response)
    else:
        full_output_path = str(Path(output_file_path).absolute())
        with open(full_output_path, "w") as f:
            json.dump(response, f, indent=2)
            print("Output file saved to:", full_output_path)
    return response
