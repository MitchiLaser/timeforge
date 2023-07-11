#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import argparse
import argcomplete
from datetime import date, timedelta, datetime

MILOG_FORM_URL = r"https://www.pse.kit.edu/downloads/Formulare/KIT%20Arbeitszeitdokumentation%20MiLoG.pdf"

parser = argparse.ArgumentParser(
    prog='TimeForge',
    description='Create fake but realistic looking working time documentation for your student job at KIT',
    epilog='For further information take a look at the Repository for this program: '
           'https://github.com/MitchiLaser/timeforge')

parser.add_argument('-n', '--name', type=str, required=True,
                    help='Name of the working person')

parser.add_argument('-m', '--month', type=int, default= datetime.now().month, metavar="[1-12]", choices=range(1,13),
                    help='The month in which the job was done as number, default value will be taken from the system clock')

parser.add_argument('-y', '--year', type=int, default= datetime.now().year,
                    help='the year in which the work was done, default value will be taken from the system clock')

parser.add_argument('-t', '--time', type=float, required=True,
                    help='the amount of working time in a month') 

parser.add_argument('-p', '--personell', type=int, required=True,
                    help='personell number (please do not put it in quotation marks')

parser.add_argument('-s','--salary', type=float, required=True,
                    help="the salary (per hour) in euros")

parser.add_argument('-O', '--organisation', type=str, required=True,
                    help='Name of the KIT organisational unit')

parser.add_argument('-g', '--low-income', action='store_true',
                    help='the Großforschungsbereich (GF) field in the form, default: False')

parser.add_argument('-u', action='store_true',
                    help='the Universitätsbereich (UB) field in the form, default: True')

parser.add_argument('-v', '--verbose', action='store_true',
                    help='more detailed information printing for debugging purpose')

parser.add_argument('-o', '--output', type=str, required=True,
                    help='Output File where the content will be written to')

parser.add_argument('-j', '--job', type=str, required=True,
                    help='description of the job task')

argcomplete.autocomplete(parser)
args = parser.parse_args()

#########################################

if args.verbose:
    from prettytable import PrettyTable
    tab = PrettyTable()
    tab.field_names = ["Parameter", "Value"]
    tab.add_row(["Name", args.name])
    tab.add_row(["Month", args.month])
    tab.add_row(["Year", args.year])
    tab.add_row(["Working Time", args.time])
    tab.add_row(["Personell number", args.personell])
    tab.add_row(["Salary", str(args.salary) + '€'])
    tab.add_row(["Organisation unit", args.organisation])
    tab.add_row(["GF", args.low_income])
    tab.add_row(["UB", args.u])
    tab.add_row(["Verbose", args.verbose])
    tab.add_row(["Output-File", args.output])
    tab.add_row(["Job-task", args.job])
    print(tab)

#########################################

# prevent autopep8 from moving these imports to the front
if True:
    import sys
    import os
    from pypdf import PdfReader, PdfWriter
    import tempfile
    import requests
    import feiertage
    from . import helpers

#########################################

form_data = {
    'Std' : args.time,
    'Summe' : args.time,
    'monatliche SollArbeitszeit' : args.time,
    'Urlaub anteilig' : 0,
    'Übertrag vom Vormonat' : 0, 
    'Übertrag in den Folgemonat' : 0, 
    'Stundensatz' : "%.2f"%(args.salary)+'€', 
    'Personalnummer' : args.personell, 
    'OE' : args.organisation,
    'GF' : args.name, #Name, Vorname
    'abc' : args.month,
    'abdd' : args.year,
    'undefined' : '', #Datum, Unterschrift Dienstvorgesetzte/r
    'Ich bestätige die Richtigkeit der Angaben' : (date(year=args.year,month=args.month,day=1) + timedelta(days=31)).replace(day=1)
}

#########################################

# list of national holidays in the German state "Baden-Württemberg"
feiertage_list = feiertage.Holidays("BW").get_holidays_list()

#########################################

if args.verbose:
    from pprint import pprint
    print("\nResponse form the Feiertage API:")
    pprint(feiertage_list)

#########################################

# Generate the content for the PDF file
table_row = 1
month = helpers.Month_Dataset(args.year, args.month, args.time, args.job, feiertage_list)
days = month.days
for day in sorted(days):
    form_data['Tätigkeit Stichwort ProjektRow'+str(table_row)] = day.job
    form_data["ttmmjjRow"+str(table_row)] = day.date.strftime("%d.%m.%y")
    form_data["hhmmRow"+str(table_row)] = day.start_time.strftime("%H:%M")
    form_data["hhmmRow"+str(table_row)+"_2"] = day.end_time.strftime("%H:%M")
    form_data["hhmmRow"+str(table_row)+"_3"] = day.pause.strftime("%H:%M")
    form_data["hhmmRow"+str(table_row)+"_4"] = day.work_hours.strftime("%H:%M")
    table_row += 1


#########################################

if args.verbose:
    print("\nForm Data:")
    pprint(form_data)

#########################################

with tempfile.TemporaryFile() as temp:

    # download online form and store it in a temp file
    try:
        r: requests.Response = requests.get(MILOG_FORM_URL, allow_redirects=True)
    except Exception as e:
        print(f"Exception when downloading PSE-Hiwi Formular -> {e}\n")
        sys.exit(os.EX_UNAVAILABLE)

    temp.write(r.content)
    temp.seek(0)    # move cursor back to the beginning of the file

    pdf_reader = PdfReader(temp)
    pdf_writer = PdfWriter(clone_from=pdf_reader)   # to copy everything else pdf_writer= PdfWriter();pdf_writer.append(pdf_reader)

    fields = pdf_reader.get_form_text_fields()  # get the field names from the form in the pdf
    for field in fields:                    # fill out all the fields in the form
        if field in form_data:
            pdf_writer.update_page_form_field_values(pdf_writer.pages[0], {field: form_data[field]})

#########################################

with open(args.output, 'wb') as output_file:    # write file
    pdf_writer.write(output_file)
