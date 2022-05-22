import json
import logging
from pathlib import Path

from .token_types import FEATURES, TOKEN_TYPES, UNCATEGORIZED

logger = logging.getLogger(__name__)


class Token:
    def __init__(self, value, token_type: str) -> None:
        self.value = value
        self.token_type = token_type

    def __str__(self) -> str:
        return f"{self.value} ({self.token_type})"


def _clean(text_entries: list):
    """
    Clean text entries.
    """
    to_split = []  # [(start_index, text1), (start_index+1, text2)]

    # Normalize entries
    for idx, text_entry in enumerate(text_entries):
        text_entry = text_entry.lower()
        if "no branch" in text_entry:
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
    return token_type


def tokenize(text_data: list):
    cleaned_text = _clean(text_data)

    # for text in cleaned_text[:50]:
    #     print(f"{text}\t:{cl.classify(text)}")
    while True:
        try:
            text = next(cleaned_text)
        except StopIteration:
            break
        else:
            yield Token(text, classify(text))


def parse(input_file_path: str, output_file_path: str = None):
    """
    Simple parser for extracted tables.
    """
    try:
        raw_data = json.loads(Path(input_file_path).read_text())
    except json.JSONDecodeError:
        raise Exception("Input file is not a valid JSON file")
    except Exception as e:
        raise Exception(f"Error parsing input file: {e}")

    all_text = []
    for page in raw_data:
        for data in page.get("data", []):
            for entry in data:
                # if entry.get("text"):  # NOTE Maybe the blank texts are important?
                all_text.append(entry["text"].lower())

    for token in tokenize(all_text):
        print(token)
