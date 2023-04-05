#!/usr/bin/env python3
import os
from PyPDF2 import PdfFileReader, PdfFileWriter
from datetime import date, timedelta, datetime, time
from deutschland import feiertage
from pprint import pprint
from deutschland.feiertage.api import default_api
Zeitraum = {'year':2023,'month':4}
path_pdf = r'KIT Arbeitszeitdokumentation MiLoG.pdf'
out_PDF = 'Arbeitszeitdokumentation-%2d-%2d.pdf'%(Zeitraum['month'], Zeitraum['year'])
hours = 20
pdf_reader = PdfFileReader(open(path_pdf, 'rb'))
job = "job"
fields = pdf_reader.getFormTextFields()
pdf_writer = PdfFileWriter()
holidays = 0
pay = 12
personal_nr = "007"
name = "Faula"
oe = ""
form_data = {
'Std': hours,
'Urlaub anteilig': holidays,
'Summe': hours, 
'monatliche SollArbeitszeit': hours, 
'Übertrag vom Vormonat': 0, 
'Übertrag in den Folgemonat': 0, 
'Ich bestätige die Richtigkeit der Angaben':(date(year=Zeitraum['year'],month=(Zeitraum['month']),day=1)+timedelta(days=31)).replace(day=1), 
'undefined': '', #Datum, Unterschrift Dienstvorgesetzte/r
'Stundensatz': "%.2f"%(pay)+'€', 
'abc': Zeitraum['month'] , #Monat
'abdd': Zeitraum['year'], #Jahr
'GF': name, #Name, Vorname
'Personalnummer': personal_nr, 
'OE': oe
}
with feiertage.ApiClient() as api_client:
    try:
        # Get Feiertage 
        api_instance = default_api.DefaultApi(api_client)
        feiertage = api_instance.get_feiertage(jahr=str(Zeitraum["year"]), nur_land="BW",nur_daten=1).values()
    except feiertage.ApiException as e:
        print("Exception when calling DefaultApi->get_feiertage: %s\n" % e)
def addDates(form_data=form_data,hours=hours,feiertage=feiertage):
    day=workday = 1
    while (hours >0) & (day<31):
        if (d:=date(year=Zeitraum['year'],month=Zeitraum['month'],day=day)).weekday() <=5:
            if not d in feiertage:
                to_work = timedelta(hours=(h:=min(hours,8)))
                form_data['Tätigkeit Stichwort ProjektRow'+str(workday)] = job
                form_data["ttmmjjRow"+str(workday)] =d.strftime("(%d.%m.%y)")
                form_data["hhmmRow"+str(workday)] = (start:=time(hour=8)).strftime("(%H:%M)")
                form_data["hhmmRow"+str(workday)+"_2"] =(end:=(datetime.combine(d,start)+to_work+timedelta(hours=1))).time().strftime("(%H:%M)")
                form_data["hhmmRow"+str(workday)+"_3"] =((datetime.combine(d,start)+(to_work/2))).time().strftime("(%H:%M)")
                form_data["hhmmRow"+str(workday)+"_4"] = "(0"+str(h)+":00)"
                workday+=1
                hours +=- h
        day+=1
    return
addDates()

for field in fields:
    if field in form_data:
        pdf_writer.updatePageFormFieldValues(pdf_reader.getPage(0),{field: form_data[field]}) 

for page_num in range(pdf_reader.getNumPages()):
    pdf_writer.addPage(pdf_reader.getPage(page_num))

output_file_path = out_PDF
with open(output_file_path, 'wb') as output_file:
    pdf_writer.write(output_file)

output_file.close()
