doeextractor
============

[![image](https://img.shields.io/pypi/v/doeextractor.svg)](https://pypi.python.org/pypi/doeextractor) [![Documentation Status](https://readthedocs.org/projects/doeextractor/badge/?version=latest)](https://doeextractor.readthedocs.io/en/latest/?version=latest) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

**DOE Reports Extractor**

-   Free software: Apache Software License 2.0
-   Documentation: <https://doeextractor.readthedocs.io>.

Requirements
------------

Tabula

Poppler via pdf2image

<https://github.com/Belval/pdf2image#how-to-install>

Amazon Textract

AWS Subscription (Access Key and Secret Key)

Overview
--------

## Features
--------

-   Extract tables from PDF reports of [DOE](https://www.doe.gov.ph/)
    using Amazon Textract (Online, more accurate, may incur charges.)
-   Extract tables from PDF reports of [DOE](https://www.doe.gov.ph/)
    using [Tabula](https://github.com/tabulapdf/tabula-java) (Offline,
    less accurate, free and open source.)

## Usage
-----

**Available commands**

    $ doeextractor --help
    Usage: doeextractor [OPTIONS] COMMAND [ARGS]...

    Console script for doeextractor.

    Options:
    --help  Show this message and exit.

    Commands:
    extract          Extract tables from a PDF file using Amazon Textract
    parse            Parse extracted tables from Amazon Textract
    show-debug-info  Debug info for DOE Extractor
    tabula-extract   Extract tables from a PDF file using Tabula
    tabula-parse     Parse extracted tables from Tabula

---

Please check [docs](docs/) for more info
