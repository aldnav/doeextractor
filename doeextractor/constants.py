from enum import Enum


class ExtractMethod(Enum):
    LATTICE = "--lattice"
    STREAM = "--stream"


class Formats(Enum):
    CSV = "CSV"
    JSON = "JSON"
    TSV = "TSV"
