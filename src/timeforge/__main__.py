#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import configargparse
from datetime import date, timedelta, datetime
import feiertage
import os
from pypdf import PdfReader, PdfWriter
import requests
import sys
import tempfile
from . import helpers
from . import config
from . import core


def main():
    """
    This whole script was wrapped into a main function. This behaviour is mandatory to create an installable executable for pip
    """
    parser = configargparse.ArgParser(
        prog='TimeForge',
        description='Create fake but realistic looking working time documentation for your student job at KIT',
        epilog='For further information take a look at the Repository for this program: '
               'https://github.com/MitchiLaser/timeforge')
    parser.add('-c', '--config', is_config_file=True, help='Location of the config file')
    parser.add('-n', '--name', type=str, required=True, help='Name of the working person')
    parser.add('-m', '--month', type=int, default=datetime.now().month, metavar="[1-12]", choices=range(1, 13), help='The month in which the job was done as number, default value will be taken from the system clock')
    parser.add('-y', '--year', type=int, default=datetime.now().year, help='the year in which the work was done, default value will be taken from the system clock')
    parser.add('-t', '--time', type=float, required=True, help='the amount of working time in a month')
    parser.add('-p', '--personell', type=int, required=True, help='personell number (please do not put it in quotation marks')
    parser.add('-s', '--salary', type=float, required=True, help="the salary (per hour) in euros")
    parser.add('-O', '--organisation', type=str, required=True, help='Name of the KIT organisational unit')
    parser.add('-g', action='store_true', help='the Großforschungsbereich (GF) field in the form, currently not usable')
    parser.add('-u', action='store_true', help='the Universitätsbereich (UB) field in the form, currently not usable')
    parser.add('-v', '--verbose', action='store_true', help='more detailed information printing for debugging purpose')
    parser.add('-o', '--output', type=str, required=True, help='Output File where the content will be written to')
    parser.add('-j', '--job', type=str, required=True, help='description of the job task')
    args = parser.parse_args()

    if args.verbose:
        # print command line arguments
        core.PrintDictAsTable(
            {
                "Name": args.name,
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

    user_input = core.APP_Data()
    user_input.set("month", args.month)
    user_input.set("year", args.year)
    user_input.set("name", args.name)
    user_input.set("personell", args.personell)
    user_input.set("organisation", args.organisation)
    user_input.set("time", args.time)
    user_input.set("salary", str(args.salary))
    user_input.set("jobs", [args.job])
    user_input.set("output", args.output)
    if len(missing := user_input.missing_keys()) != 0:
        raise RuntimeError(f"Missing keys in the internal dataset, cannot generate pdf: {missing}")
    form_data = user_input.pdf_content()

    #########################################

    # list of national holidays in the German state "Baden-Württemberg"
    feiertage_list = feiertage.Holidays(config.FEDERAL_STATE, year=args.year).get_holidays_list()

    if args.verbose:
        core.PrintListAsTable(feiertage_list, "Calculated Holidays")

    #########################################

    # Generate the content for the PDF file
    # TODO: this should be outsourced into the core module
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

    if args.verbose:
        core.PrintDictAsTable(form_data, "PDF Form field", "Value")

    #########################################

    with core.ProvideOutputFile(args.output) as (WriteInPDF, fields):
        for field in fields:                    # fill out all the fields in the form
            if field in form_data:
                WriteInPDF.update_page_form_field_values(WriteInPDF.pages[0], {field: form_data[field]})


if __name__ == "__main__":
    main()
