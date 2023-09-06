#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import argparse
import argcomplete
from datetime import date, timedelta, datetime


def main():
    """
    This whole script was wrapped into a main function. This behaviour is mandatory to create an installable executable for pip
    """
    parser = argparse.ArgumentParser(
        prog='TimeForge',
        description='Create fake but realistic looking working time documentation for your student job at KIT',
        epilog='For further information take a look at the Repository for this program: '
               'https://github.com/MitchiLaser/timeforge')

    parser.add_argument('-n', '--name', type=str, required=True,
                        help='Name of the working person')

    parser.add_argument('-m', '--month', type=int, default=datetime.now().month, metavar="[1-12]", choices=range(1, 13),
                        help='The month in which the job was done as number, default value will be taken from the system clock')

    parser.add_argument('-y', '--year', type=int, default=datetime.now().year,
                        help='the year in which the work was done, default value will be taken from the system clock')

    parser.add_argument('-t', '--time', type=float, required=True,
                        help='the amount of working time in a month')

    parser.add_argument('-p', '--personell', type=int, required=True,
                        help='personell number (please do not put it in quotation marks')

    parser.add_argument('-s', '--salary', type=float, required=True,
                        help="the salary (per hour) in euros")

    parser.add_argument('-O', '--organisation', type=str, required=True,
                        help='Name of the KIT organisational unit')

    parser.add_argument('-g', action='store_true',
                        help='the Großforschungsbereich (GF) field in the form, currently not usable')

    parser.add_argument('-u', action='store_true',
                        help='the Universitätsbereich (UB) field in the form, currently not usable')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='more detailed information printing for debugging purpose')

    parser.add_argument('-o', '--output', type=str, required=True,
                        help='Output File where the content will be written to')

    parser.add_argument('-j', '--job', type=str, required=True,
                        help='description of the job task')

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    #########################################

    # prevent autopep8 from moving these imports to the front
    if True:
        import feiertage
        import os
        from pypdf import PdfReader, PdfWriter
        import requests
        import sys
        import tempfile
        from . import helpers
        from . import config
        from . import core

    #########################################

    if args.verbose:
        core.PrintDictAsTable(
            {
                "Name": args.month,
                "Month": args.month,
                "Year": args.year,
                "Working Time": args.time,
                "Personell number": args.personell,
                "Salary": str(args.salary) + '€',
                "Organisation unit": args.organisation,
                "GF": args.g,
                "UB": args.u,
                "Verbose": args.verbose,
                "Output-File": args.output,
                "Job-task": args.job,
            },
            "Command Line Arguments",
            "Values"
        )

    #########################################

    form_data = {
        'Std': args.time,
        'Summe': args.time,
        'monatliche SollArbeitszeit': args.time,
        'Urlaub anteilig': 0,
        'Übertrag vom Vormonat': 0,
        'Übertrag in den Folgemonat': 0,
        'Stundensatz': "%.2f" % (args.salary) + '€',
        'Personalnummer': args.personell,
        'OE': args.organisation,
        'GF': args.name,  # Name, Vorname
        'abc': args.month,
        'abdd': args.year,
        'undefined': '',  # Datum, Unterschrift Dienstvorgesetzte/r
        'Ich bestätige die Richtigkeit der Angaben': (date(year=args.year, month=args.month, day=1) + timedelta(days=31)).replace(day=1)
    }

    #########################################

    # list of national holidays in the German state "Baden-Württemberg"
    feiertage_list = feiertage.Holidays(config.FEDERAL_STATE).get_holidays_list()

    #########################################

    if args.verbose:
        core.PrintListAsTable(feiertage_list, "Calculated Holidays")

    #########################################

    # Generate the content for the PDF file
    table_row = 1
    month = helpers.Month_Dataset(args.year, args.month, args.time, args.job, feiertage_list)
    days = month.days
    for day in sorted(days):
        form_data['Tätigkeit Stichwort ProjektRow' + str(table_row)] = day.job
        form_data["ttmmjjRow" + str(table_row)] = day.date.strftime("%d.%m.%y")
        form_data["hhmmRow" + str(table_row)] = day.start_time.strftime("%H:%M")
        form_data["hhmmRow" + str(table_row) + "_2"] = day.end_time.strftime("%H:%M")
        form_data["hhmmRow" + str(table_row) + "_3"] = day.pause.strftime("%H:%M")
        form_data["hhmmRow" + str(table_row) + "_4"] = day.work_hours.strftime("%H:%M")
        table_row += 1

    #########################################

    if args.verbose:
        core.PrintDictAsTable(form_data, "PDF Form field", "Value")

    #########################################

    with core.ProvideOutputFile(args.output) as (WriteInPDF, fields):
        for field in fields:                    # fill out all the fields in the form
            if field in form_data:
                WriteInPDF.update_page_form_field_values(WriteInPDF.pages[0], {field: form_data[field]})


if __name__ == "__main__":
    main()
