#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import argparse, argcomplete
from datetime import date, timedelta, datetime, time

parser = argparse.ArgumentParser(
    prog='TimeForge',
    description = 'Create fake but realistic looking working time documentation for your student job at KIT',
    epilog='For further information take a look at the Repository for this program: https://github.com/MitchiLaser/timeforge')

parser.add_argument('-n', '--name', type=str, required=True,
                   help='Name of the working person')

parser.add_argument('-m', '--month', type=int, default= datetime.now().month,
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

parser.add_argument('-i', '--input', type=str, required=True,
                    help='the location of the input file (The MiLoG-Arbeitszeitdokumentation.pdf from the PSE website)')

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
    tab.add_row(["Input File", args.input])
    tab.add_row(["Output-File", args.output])
    tab.add_row(["Job-task", args.job])
    print(tab)
#########################################

#check args
import sys
if args.month > 12 or args.month < 1:
    print("Monat muss zwischen 1 und 12 liegen")
    sys.exit()

if args.year < 0:
    print("Jahr muss größer 0 sein")
    sys.exit()

if args.time < 0:
    print("Arbeitszeit muss größer 0 sein")
    sys.exit()

if args.salary < 0:
    print("Gehalt muss größer 0 sein")
    sys.exit()
#########################################

# prevent autopep8 from moving these imports to the front
if True:
    from pypdf import PdfReader, PdfWriter

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

# Generate the content for the PDF file
import _extensions as ex

table_row = 1
month = ex.Month(args.year, args.month, args.time, args.job)
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
    from pprint import pprint
    print("\nForm Data:")
    pprint(form_data)

#########################################

pdf_reader = PdfReader( open(args.input, 'rb') )
pdf_writer = PdfWriter()

fields = pdf_reader.get_form_text_fields()  # get the field names from the form in the pdf
for field in fields:                    # fill out all the fields in the form
    if field in form_data:
        pdf_writer.update_page_form_field_values(pdf_reader.pages[0],{field: form_data[field]}) 

pdf_writer.add_page(pdf_reader.pages[0])    # put form content and page in a pdf-writer object

#########################################

with open(args.output, 'wb') as output_file:    # write file
    pdf_writer.write(output_file)
output_file.close()
