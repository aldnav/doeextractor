============
doeextractor
============


.. image:: https://img.shields.io/pypi/v/doeextractor.svg
        :target: https://pypi.python.org/pypi/doeextractor


.. image:: https://readthedocs.org/projects/doeextractor/badge/?version=latest
        :target: https://doeextractor.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
        :target: https://github.com/pre-commit/pre-commit
        :alt: pre-commit



DOE Reports Extractor


* Free software: Apache Software License 2.0
* Documentation: https://doeextractor.readthedocs.io.


Features
--------

* Extract tables from PDF reports of DOE_ using Tabula_


Usage
-----

**Available commands**

::

    $ doeextractor --help
    Usage: doeextractor [OPTIONS] COMMAND [ARGS]...

    Console script for doeextractor.

    Options:
    --help  Show this message and exit.

    Commands:
    extract          Extract tables from a PDF file using Tabula
    show-debug-info  Debug info for DOE Extractor

**Extracting a report**

::

    $ doeextractor extract -i 'reports/2022-05-18/petro_min_2022-may-10.pdf'
    Running tabula with this command:
    java -jar tabula-1.0.5-jar-with-dependencies.jar --lattice -f CSV --pages 1 /Users/pro/retailprices/reports/2022-05-18/petro_min_2022-may-10.pdf
    AREA,PRODUCT,PETRON,SHELL,CALTEX,PHOENIX,FLYING V,SEAOIL,JETTI,MY GAS,INDEPENDENT,OVERALL,COMMON,AVERAGE,
    "",,Liquid Fuels Price Range,,,,,,,,,,,,
    "",REGION IX,,,,,,,,,,,,,
    OUTLET",N.A,82.41 - 82.61,NONE,82.51.A,82.41 - 82.61,,N.A,"NO BRANCH/
    "",,RON 95,79.61 - 79.86,80.11 - 81.11,79.61 - 79.61,82.11 - 82.11,,79.61 - 79.61,79.61 - 81.66,79.61 - 82.11,79.61,80.22,,
    "",,RON 91,78.86 - 79.11,79.36 - 79.36,78.86 - 78.86,81.36 - 81.36,NO BRANCH/,78.86 - 78.86,78.86 - 78.86,78.86 - 81.36,78.86,79.31,,
    "",,DIESEL,81.02 - 81.23,81.52 - 83.92,81.02 - 81.03,83.53 - 83.53,OUTLET,80.02 - 80.02,81.03 - 83.95,80.02 - 83.95,81.03,81.59,,
    "",,DIESEL PLUS,83.02 - 83.02,87.42 - 87.42,N.A,N.A,,N.A,N.A,83.02 - 87.42,87.42,85.95,,
    "",,KEROSENE,83.70 - 83.70,-,83.13 - 83.13,N.A,,N.A,-,83.13 - 83.70,83.13,83.32,,
    OUTLET",78.45 - 78.45,78.20 - 78.45,78.20,78.25.20 - 78.20,-,"NO BRANCH/
    "",,RON 91,77.70 - 77.70,-,-,-,NO BRANCH/,77.70 - 77.70,-,77.95 - 77.95,77.70 - 77.95,77.70,77.76,
    "",,DIESEL,80.30 - 80.30,-,-,-,OUTLET,80.30 - 80.30,-,80.55 - 80.55,80.30 - 80.55,80.30,80.35,
    "",,KEROSENE,-,-,-,N.A,,N.A,N.A,80.20 - 80.20,80.20 - 80.20,NONE,80.20,
    OUTLET",77.21 - 79.21,NONE,78.22 - 77.21,79.21 - 79.21,78.25 - 78.25,-,,-,"NO BRANCH/
    "",,RON 91,76.71 - 76.71,-,78.05 - 78.05,-,,-,76.71 - 78.05,NONE,77.38,,,
    "",,DIESEL,82.57 - 82.57,83.82 - 83.82,83.85 - 83.85,-,,-,82.57 - 83.85,NONE,83.41,,,
    "",Dipolog City,RON 100,-,-,-,-,-,-,-,-,-,-,NONE,NONE
    "",,RON 97,-,N.A,N.A,-,N.A,N.A,N.A,N.A,N.A,-,NONE,NONE
    "",,RON 95,74.21 - 77.21,77.71 - 79.11,78.55 - 78.55,-,-,77.21 - 77.21,-,-,75.50 - 75.50,74.21 - 79.11,77.21,77.21
    "",,RON 91,73.56 - 76.71,77.21 - 78.96,78.30 - 78.30,-,-,76.71 - 76.71,-,-,75.50 - 75.50,73.56 - 78.96,76.71,76.81
    "",,DIESEL,78.22 - 82.57,83.07 - 84.31,83.80 - 83.80,-,-,82.57 - 82.57,-,-,76.65 - 76.65,76.65 - 84.31,82.57,81.99
    "",,DIESEL PLUS,-,90.27 - 90.27,N.A,N.A,N.A,-,N.A,N.A,N.A,90.27 - 90.27,90.27,90.27
    "",,KEROSENE,-,-,-,N.A,-,N.A,N.A,-,-,-,NONE,NONE
    OUTLET",-,-,NONE,NONERON 95,"NO BRANCH/
    RON 91,81.85 - 81.85,81.85 - 81.85,81.85,81.85,,,,,,,,,,
    DIESEL,84.35 - 84.85,84.35 - 84.85,84.35,84.52,,,,,,,,,,
    KEROSENE,80.60 - 80.60,80.60 - 80.60,NONE,80.60,,,,,,,,,,


**Output in JSON format and write to file**

::

    $ doeextractor extract --pages all -i '/Users/pro/retailprices/reports/2022-05-18/petro_min_2022-may-10.pdf' -f JSON -o samples/petro_min_2022-may-10.json
    Running tabula with this command:
    java -jar /Users/pro/tabula-1.0.5-jar-with-dependencies.jar --lattice -f JSON --pages all /Users/pro/retailprices/reports/2022-05-18/petro_min_2022-may-10.pdf -o /Users/pro/doeextractor/samples/petro_min_2022-may-10.json
    $ file samples/petro_min_2022-may-10.json
    samples/petro_min_2022-may-10.json: JSON data

.. _Tabula: https://github.com/tabulapdf/tabula-java
.. _DOE: https://www.doe.gov.ph/


**Parsing the extracted report**

::

    $ doeextractor parse samples/petro_min_2022-may-10.json -o samples/parsed_output.json
    Parse extracted tables
    Output file saved to: /Users/pro/doeextractor/samples/parsed_output.json
