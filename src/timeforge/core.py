#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from contextlib import contextmanager
from datetime import datetime, date, timedelta
import feiertage
import itertools
import os
from pypdf import PdfReader, PdfWriter
import requests
import sys
import tempfile
from typing import Any
from . import config


def PrintDictAsTable(dataset: dict, title_keys: str, title_values: str):
    """
    This function prints a dictionary as a table.
    This is really useful for debugging purposes and will be called multiple times when the verbose flag is set.

    Parameters
    ----------
    dataset : dict
        The dictionary which should be printed
    title_keys : str
        A title for the dictionary keys column
    title_values : str
        A title for the dictionary values column

    """
    # get the max length of a string in the key and in the value section
    max_key_len, max_value_len = len(title_keys), len(title_values)
    for (i, j) in zip([*dataset.keys()], [*dataset.values()]):
        max_key_len = max(len(str(i)), max_key_len)
        max_value_len = max(len(str(j)), max_value_len)

    print("┌─" + "─" * max_key_len + "─┬─" + "─" * max_value_len + "─┐")
    print("│ " + title_keys + " " * (max_key_len - len(title_keys)) + " │ " + title_values + " " * (max_value_len - len(title_values)) + " │")
    print("├─" + "─" * max_key_len + "─┼─" + "─" * max_value_len + "─┤")
    for (i, j) in zip([*dataset.keys()], [*dataset.values()]):
        print("│ " + str(i) + " " * (max_key_len - len(str(i))) + " │ " + str(j) + " " * (max_value_len - len(str(j))) + " │")
    print("└─" + "─" * max_key_len + "─┴─" + "─" * max_value_len + "─┘")


def PrintListAsTable(dataset: list, title: str):
    """
    This function prints a list as a table.
    This is really useful for debugging purpose and will be called multiple times when the verbose flag is set.

    Parameters
    ----------
    dataset : list
        The list which should be printed as a table
    title : str
        The title of the list

    """
    max_len = len(title)
    for i in dataset:
        max_len = max(len(str(i)), max_len)

    print("┌─" + "─" * max_len + "─┐")
    print("│ " + title + " " * (max_len - len(title)) + " │")
    print("├─" + "─" * max_len + "─┤")
    for i in dataset:
        print("│ " + str(i) + " " * (max_len - len(str(i))) + " │")
    print("└─" + "─" * max_len + "─┘")


class APP_Data:

    def __init__(self):
        # this is all the data that goes into the form in the pdf.
        # the dictionary provides a translation from the internal keywords to the names of the pdf fields
        self.translation_table = {
            "name": 'GF',
            "month": 'abc',
            "year": 'abdd',
            "time": ['Std', 'Summe', 'monatliche SollArbeitszeit'],
            "personell": 'Personalnummer',
            "salary": 'Stundensatz',
            "organisation": 'OE',
            "signature_pse": 'undefined',
            "signature": 'Ich bestätige die Richtigkeit der Angaben',
            "holiday": 'Urlaub anteilig',
            "from_last_month": 'Übertrag vom Vormonat',
            "for_next_month": 'Übertrag in den Folgemonat',
        }
        # TODO: the GF and UB fields (both default False) are currently no usable, maybe the newest version of pypdf can check boxes

        # this dataset contains the data which the application needs to run.
        # some of it will be used within the pdf form and some might be used at other locations.
        # the dataset is filled with some predefined default values.
        self.dataset = {
            "verbose": False,       # default value: False, the user only wants a verbose output for debugging
            "signature_pse": '',    # Datum, Unterschrift Dienstvorgesetzte/r, always empty
            "holiday": 0,           # holidays are currently not supported by this application
            "from_last_month": 0,   # transferring holidays from the last month is currently not supported by this application
            "for_next_month": 0,   # transferring holidays to the next month is currently not supported by this application
            "month": datetime.now().month,  # default month will be taken from the system clock
            "year": datetime.now().year,    # default year will be taken from the system clock
        }

        # from here one some functions are defined which will be needed for validating the input arguments

        # this returns a function which does the type checking of the input parameters
        def try_convert(target_type, error_msg):
            def convert(value):
                try:
                    value = target_type(value)
                except (ValueError, TypeError):
                    raise ValueError(error_msg)
                return value
            return convert

        # the month needs an additional range checking
        def check_month(month):
            try:
                month = try_convert(int, "")(month)
                assert month in list(range(1, 13))    # month is integer 1 to 12
            except (ValueError, AssertionError):
                raise ValueError("Month must be an integer between 1 and 12")
            return month

        # the jobs also need a special validation
        def check_jobs(jobs):
            if (not isinstance(jobs, list)) or (len(jobs) < 1):
                raise ValueError("Jobs argument must be of type list with minimum length of 1")
            return jobs

        # this is a dictionary which contains the validation functions for each keyword which has to be validated
        self.validation = {
            "name": try_convert(str, "Name "),
            "year": try_convert(int, "Year must be an integer"),
            "month": check_month,   # month also needs a range check, therefore there is a special validation function for the month
            "time": try_convert(float, "Working time must be a number with the dot '.' as decimal separator"),
            "personell": try_convert(int, "Personell Number must be an integer"),
            "salary": try_convert(float, "Salary time must be a number with the dot '.' as decimal separator"),
            "organisation": try_convert(str, "Organisation name  must be a string or convertible to a string"),
            "verbose": try_convert(bool, "Verbose must be a boolean (True / False)"),
            "jobs": check_jobs,  # jobs must be checked separately because they have to be of the type list with minimal length of 1
        }

        # there are some keys which have no validation, no default value and will not be present in the pdf file. These are listed here:
        self.misc_keys = {
            "output",   # output file
        }

        # this is the set of all the available keywords which the dataset should be able to hold
        # the 'signature' key is the one which will be automatically generated by the pdf_content() function
        self.keys = ({*self.translation_table} - {"signature"}) | {*self.dataset} | {*self.validation} | self.misc_keys

    def set(self, key: str, value: Any):
        """
        set a value in the dataset

        Parameters
        ----------
        key : str
            a key name for the dataset. If the key is not in the list of valid keys the application throws a 'KeyError' exception
        value : Any
            the value which should be set to the corresponding key

        Raises
        ------
        KeyError :
            In case the key parameter is not in the list of valid keys

        """
        if key in self.keys:
            # if the key is on the list of keys which should be validated: perform a validation
            if key in {*self.validation}:
                value = self.validation[key](value)
            # add the value to the dataset
            self.dataset[key] = value
        else:
            raise KeyError("Key is not in the list of valid keys")

    def get(self, key: str):
        """
        get a value from the dataset

        Parameters
        ----------
        key : str
            The key in the dataset which should be fetched

        Raises
        ------
        KeyError :
            In case no attribute with this key is available within the dataset

        Returns
        -------
        value : Any
            The value behind the key parameter
            If the key parameter was not present in the dataset, a KeyError exception will be thrown

        """
        if key in {*self.dataset}:
            return self.dataset[key]
        else:
            # the key is not in the dataset, raise an exception
            raise KeyError("This key was not set in the dataset")

    def missing_keys(self):
        """
        Return the list of missing keys

        Returns
        -------
        missing_keys: set
            a set which contains all the missing keys
        """
        # check the difference between all available keywords and the ones which are present in the dataset.
        # If there is a difference: the dataset is not complete
        return self.keys - {*self.dataset}

    def pdf_content(self):
        """

        Returns
        -------
        pdf_dict : dict
            This is a dictionary with the content in the right state for the pdf file

        Raises
        ------
        RuntimeError :
            if there are some missing keys (which can be checked with the missing_keys() methode) then a RuntimeError will be thrown
        """
        if len(self.missing_keys()) != 0:
            raise RuntimeError("Error: one or more keys are missing in the dataset")
        # create another dict which contains only the keys of the translation_table but with the translated key table
        pdf_dict = dict()
        for i in {*self.translation_table}:
            pdf_key = self.translation_table[i]
            if isinstance(pdf_key, list):
                # if the translation table contains a list: use all keys in the list
                for j in pdf_key:
                    pdf_dict[j] = str(self.dataset[i])
            elif i == "signature":
                # change to the first day of the next month
                pdf_dict[pdf_key] = str((date(year=self.dataset["year"], month=self.dataset["month"], day=1) + timedelta(days=31)).replace(day=1))
            elif i == "salary":
                # this value should be formatted with two digits after the decimal separater
                pdf_dict[pdf_key] = "%.2f" % (self.dataset[i]) + " €"
            else:
                pdf_dict[pdf_key] = str(self.dataset[i])
        return pdf_dict


@contextmanager
def ProvideOutputFile(output_file: str):
    # store the online PDF in a temporary file which will automatically be deleted when this contextmanager will be left
    with tempfile.TemporaryFile(suffix=".pdf") as temp:

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


class MonthDataset:

    def __init__(self, year: date, month: date, total_work_time: float, jobs: list[str]):
        self.feiertage = feiertage.Holidays(config.FEDERAL_STATE).get_holidays_list()
        # TODO
        raise NotImplementedError
