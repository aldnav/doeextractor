import base64
import os
from json import load
from pathlib import Path
from typing import Any, Union

import boto3
from dotenv import load_dotenv

from .file_helpers import (
    add_file_to_local_cache,
    convert_pdf_to_png,
    is_file_already_analyzed,
)

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", None)
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", None)
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY", None)
if not AWS_REGION or not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
    raise Exception(
        """\
        Incomplete credentials for AWS Textract. \
        Please set AWS_REGION, AWS_ACCESS_KEY, AWS_SECRET_KEY"""
    )


def get_table_csv_results(input_file: Path):
    input_as_image = convert_pdf_to_png(input_file)
    # contents = bytearray(input_as_image.read_bytes())
    input_images = []
    if input_as_image.is_dir():
        input_images.extend(input_as_image.glob("*.png"))
    else:
        input_images = [input_as_image]

    csv_results = []
    print("Analyzing...")
    client = boto3.client(
        "textract",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
    )
    for idx, input_png in enumerate(input_images):
        with open(input_png, "rb") as document:
            # contents = bytearray(document.read())
            contents = bytearray(document.read())
        # contents = base64.b64encode(input_as_image.read_bytes())
        print(f"{idx} / {len(input_images)}")
        response = client.analyze_document(
            Document={"Bytes": contents}, FeatureTypes=["TABLES"]
        )

        blocks = response["Blocks"]

        blocks_map = {}
        table_blocks = []
        for block in blocks:
            blocks_map[block["Id"]] = block
            if block["BlockType"] == "TABLE":
                table_blocks.append(block)

        if len(table_blocks) == 0:
            return None

        csv = ""
        for index, table in enumerate(table_blocks):
            csv += generate_table_csv(table, blocks_map, index + 1)
            csv += "\n\n"
        csv_results.append(csv)
    print(f"{len(input_images)} / {len(input_images)}")

    return csv_results


def generate_table_csv(table_result, blocks_map, table_index):
    rows = get_rows_columns_map(table_result, blocks_map)
    # table_id = "Table_" + str(table_index)
    # get cells.
    # csv = "Table: {0}\n\n".format(table_id)
    csv = ""
    for row_index, cols in rows.items():
        for col_index, text in cols.items():
            csv += "{}".format(text) + ","
        csv += "\n"
    csv += "\n\n\n"
    return csv


def get_rows_columns_map(table_result, blocks_map):
    rows = {}
    for relationship in table_result["Relationships"]:
        if relationship["Type"] == "CHILD":
            for child_id in relationship["Ids"]:
                cell = blocks_map[child_id]
                if cell["BlockType"] == "CELL":
                    row_index = cell["RowIndex"]
                    col_index = cell["ColumnIndex"]
                    if row_index not in rows:
                        # create new row
                        rows[row_index] = {}
                    # get the text value
                    rows[row_index][col_index] = get_text(cell, blocks_map)
    return rows


def get_text(result, blocks_map):
    text = ""
    if "Relationships" in result:
        for relationship in result["Relationships"]:
            if relationship["Type"] == "CHILD":
                for child_id in relationship["Ids"]:
                    word = blocks_map[child_id]
                    if word["BlockType"] == "WORD":
                        text += word["Text"] + " "
                    if word["BlockType"] == "SELECTION_ELEMENT":
                        if word["SelectionStatus"] == "SELECTED":
                            text += "X "
    return text


def extract(input_file_path: Union[str, Path]):
    """
    Extract tables from a PDF file using Amazon Textract
    """
    if isinstance(input_file_path, str):
        input_file_path = Path(input_file_path).absolute()
    # Check if the file is already analyzed
    is_file_analyzed_before, initial_result = is_file_already_analyzed(input_file_path)
    if is_file_already_analyzed and initial_result:
        # TODO Return the analysis result
        print("File is already analyzed")
        print(initial_result)
        return 0

    csv_results = get_table_csv_results(input_file_path)
    if not bool(csv_results):
        print("Cannot analyze or no CSV results")
        return 0

    output_file_path = input_file_path.with_suffix(".csv")
    with open(output_file_path, "w") as f:
        for csv_result in csv_results:
            f.write(csv_result)
    add_file_to_local_cache(input_file_path, output_file_path)
    print("CSV results are written to {}".format(input_file_path.with_suffix(".csv")))
    return 0
