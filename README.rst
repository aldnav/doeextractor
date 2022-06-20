doeextractor
============

|pre-commit|

**DOE Reports Extractor**

-  Free software: Apache Software License 2.0
-  Documentation: https://aldnav.github.io/doeextractor/

Requirements
------------

Tabula

Poppler via pdf2image

https://github.com/Belval/pdf2image#how-to-install

Amazon Textract

AWS Subscription (Access Key and Secret Key)

Features
-----------

-  Extract tables from PDF reports of `DOE <https://www.doe.gov.ph/>`__
   using Amazon Textract (Online, more accurate, may incur charges.)
-  Extract tables from PDF reports of `DOE <https://www.doe.gov.ph/>`__
   using `Tabula <https://github.com/tabulapdf/tabula-java>`__ (Offline,
   less accurate, free and open source.)

Usage
--------

**Available commands**

::

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

--------------

Please check the `documentation <https://aldnav.github.io/doeextractor/>`_ for more info

.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
