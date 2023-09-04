#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from contextlib import contextmanager
import os
from pypdf import PdfReader, PdfWriter
import requests
import sys
import tempfile
from . import config


@contextmanager
def ProvideOutputFile(output_file: str):
    # store the online PDF in a temporary file which will automatically be deleted when this contextmanager will be left
    with tempfile.TemporaryFile() as temp:

        # download online form and store it in a temp file
        try:
            r: requests.Response = requests.get(config.MILOG_FORM_URL, allow_redirects=True)
        except Exception as e:
            print(f"Exception when downloading PSE-Hiwi Formular -> {e}\n")
            sys.exit(os.EX_UNAVAILABLE)

        temp.write(r.content)
        temp.seek(0)    # move cursor back to the beginning of the file

        pdf_reader = PdfReader(temp)
        pdf_writer = PdfWriter(clone_from=pdf_reader)   # to copy everything else pdf_writer= PdfWriter();pdf_writer.append(pdf_reader)

        fields = pdf_reader.get_form_text_fields()  # get the field names from the form in the pdf

        try:
            yield pdf_writer, fields
        finally:
            with open(output_file, 'wb') as output_file:    # write file
                pdf_writer.write(output_file)
