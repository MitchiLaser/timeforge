from datetime import date
from numpy.random import randint, rand

class Day:
        def __init__(self, job, date, begin, end, worktime, pause):
            self.job = job
            self.date = date
            self.begin = begin
            self.end = end
            self.worktime = worktime
            self.pause = pause

class Month:
    def __init__(self, month, days = []):
        self._month = month
        self.days = days
    
    def add_work(self, job, date, begin, end, worktime):
        self.days.append(Day(job, date, begin, end, worktime))

def make_Timetable(args):
    month = Month(args.month)
    work_hours = args.time
    timeblocks = make_timeblocks(work_hours)
    
    '''
    Ohne Pause:
    - len(timeblocks) viele Tage generieren
    - Tage nicht an Wochenden oder Feiertagen
    - geht nur für >= 40h

    Mit Pausen
    - mit Wkeit pro Tag
    - Für Arbeitszeit > 40h wkeit auf 100% dann sicher bis 80h
    '''
    days_needed = len(timeblocks)
    days = make_days(args.year, args.month, timeblocks)

def make_timeblocks(work_hours_left):
    '''Generiert 2,3 oder 4h lange Zeitblöcke für die gesamte Arbeitszeit im Monat. Gibt diese als int array zurück'''
    def random_timeblock():
        '''Generiert einen Zeitblock zwischen 2 und 4h'''
        return randint(2, 4)
    
    timeblock_array = []
    while work_hours_left > 0:
        timeblock_length = random_timeblock()
        if work_hours_left - timeblock_length < 0:
            timeblock_length = work_hours_left
        
        timeblock_array.append(timeblock_length)
        work_hours_left -= timeblock_length

def make_days(year, month, timeblocks):
    def make_workday_date():
        while True:
            day = randint(1,28)
            d = date(year, month, day)
            if d.weekday() <= 4 and not d in feiertage_api_response:
                return d
    
    def random_start_time():
        '''Zufällige Startzeit zwischen 8 und 11h'''
        return randint(8,11)

    timeblocks_left = len(timeblocks)
    
    # Pause wird Zufällig eingefügt. Ab 20h müssen 2 Blöcke pro Tag gemacht werden um genug Arbeitszeit unterzubringen
    if timeblocks_left < 20:
        p_2blocks = 0.3
    else:
        p_2blocks = 1

    while timeblocks_left > 0:
        d = make_workday_date()
        if d not in days:
            #if p_2blocks <= rand:
            #    timeblocks_left -= 2
            work_time = timeblocks.pop()
            start_time = random_start_time()
            end_time = start_time + work_time
            pause = 0

            timeblocks_left -= 1
    return days

if True:
    import sys, os
    from deutschland import feiertage
    from deutschland.feiertage.api import default_api
    from pypdf import PdfReader, PdfWriter

#########################################

with feiertage.ApiClient() as api_client:
    api_instance = default_api.DefaultApi(api_client)
    nur_land = "BW" # only check for the federal state of Baden-Württemberg
    nur_daten = 1   # dismiss additional information about the day

    try:
        feiertage_api_response = api_instance.get_feiertage(str(2000), nur_land=nur_land, nur_daten=nur_daten)
    except feiertage.ApiException as e:
        print("Exception when calling Feiertage API -> get_feiertage: %s\n"%e)
        sys.exit(os.EX_UNAVAILABLE)

#Test
import numpy as np
