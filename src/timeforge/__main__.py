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
                    help='The month in which the job was done, default value will be taken from the system clock')

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
    import sys, os
    from deutschland import feiertage
    from deutschland.feiertage.api import default_api
    from pypdf import PdfReader, PdfWriter
    import tempfile
    import requests

#########################################

with feiertage.ApiClient() as api_client:
    api_instance = default_api.DefaultApi(api_client)
    nur_land = "BW" # only check for the federal state of Baden-Württemberg
    nur_daten = 1   # dismiss additional information about the day

    try:
        feiertage_api_response = api_instance.get_feiertage(str(args.year), nur_land=nur_land, nur_daten=nur_daten)
    except feiertage.ApiException as e:
        print("Exception when calling Feiertage API -> get_feiertage: %s\n"%e)
        sys.exit(os.EX_UNAVAILABLE)

#########################################

if args.verbose:
    from pprint import pprint
    print("\nResponse form the Feiertage API:")
    pprint(feiertage_api_response)

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

# Generate the content for the PDF file
date_day = 1
table_row = 1
work_hours_left = args.time
while (work_hours_left > 0) and (date_day < 28): # February has 28 days and is therefore the shortest month of all
    if ( ( d := date( year=args.year, month=args.month, day=date_day) ).weekday() <= 5 ) and ( not d in feiertage_api_response ):
        worktime = timedelta( hours = ( h := min(work_hours_left, 4) ) ) # 4h maximum to work
        form_data['Tätigkeit Stichwort ProjektRow'+str(table_row)] = args.job
        form_data["ttmmjjRow"+str(table_row)] = d.strftime("%d.%m.%y")
        form_data["hhmmRow"+str(table_row)] = ( start := time(hour=8) ).strftime("%H:%M" )  # beginning at 8am
        form_data["hhmmRow"+str(table_row)+"_2"] =( end := ( datetime.combine(d,start) + worktime ) ).time().strftime("%H:%M")
        form_data["hhmmRow"+str(table_row)+"_3"] ="00:00" #( (datetime.combine(d,start) + (worktime/2)) ).time().strftime("%H:%M")
        form_data["hhmmRow"+str(table_row)+"_4"] = time( hour=int(h), minute=int( (h % 1) * 60) ).strftime("%H:%M") #"0" + str(worktime) + ":00"
        work_hours_left -= h
        table_row += 1
    date_day += 1

#########################################

if args.verbose:
    print("\nForm Data:")
    pprint(form_data)

#########################################

with tempfile.TemporaryFile() as temp:

    # download online form and store it in a tempfile
    r = requests.get(r"https://www.pse.kit.edu/downloads/Formulare/KIT%20Arbeitszeitdokumentation%20MiLoG.pdf", allow_redirects=True)
    temp.write(r.content)
    temp.seek(0)    # move cursor back to the beginning of the file

    pdf_reader = PdfReader( temp ) #open(temp, 'rb') )
    pdf_writer = PdfWriter()

    fields = pdf_reader.get_form_text_fields()  # get the field names from the form in the pdf
    for field in fields:                    # fill out all the fields in the form
        if field in form_data:
            pdf_writer.update_page_form_field_values(pdf_reader.pages[0],{field: form_data[field]}) 

    pdf_writer.add_page(pdf_reader.pages[0])    # put form content and page in a pdf-writer object

#########################################

with open(args.output, 'wb') as output_file:    # write file
    pdf_writer.write(output_file)
