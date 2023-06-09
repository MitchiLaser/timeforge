from datetime import date, time
from numpy.random import randint, rand

class Day:
    def __init__(self, job, date, start_time, end_time, pause, work_hours):
        self.job = job
        self.date = date
        self.start_time = self.time_from_h(start_time)
        self.end_time = self.time_from_h(end_time)
        self.work_hours = self.time_from_h(work_hours)
        self.pause = self.time_from_h(pause)

    def __lt__(self, other):
        return self.date < other.date
    
    def time_from_h(self, hours):
        return time(hour= int(hours), minute= int(hours * 60 % 60))

class Month:
    def __init__(self, year, month, total_work_hours, job):
        # Werte für Zufallslängen in h
        self.min_timeblock = 2
        self.max_timeblock = 4
        self.min_pause = 2
        self.max_pause = 3
        self.min_start_time = 8
        self.max_start_time = 23 - 2 * self.max_timeblock - self.max_pause

        self._month = month
        self.total_work_hours = total_work_hours
        self.days = []
        timeblocks = self.make_timeblocks(self.total_work_hours)
        self.make_days(year, self._month, timeblocks, job)
    
    def add_work(self, job, date, start_time, end_time, pause, work_hours):
        self.days.append(Day(job, date, start_time, end_time, pause, work_hours))

    def make_timeblocks(self, work_hours_left):
        '''Erstellt Array von int Zeitblöcken, sodass sie in Summe die Monatsarbeitszeit ergeben '''
        def random_timeblock(min, max):
            return randint(min, max+1)
        
        timeblock_array = []
        while work_hours_left > 0:
            timeblock_length = random_timeblock(self.min_timeblock, self.max_timeblock)
            if work_hours_left - timeblock_length < 0:
                timeblock_length = work_hours_left
            
            timeblock_array.append(timeblock_length)
            work_hours_left -= timeblock_length
        return timeblock_array

    def make_days(self, year, month, timeblocks, job):
        '''Erstellt Einträge für den gesamten Monat'''
        def make_workday_date(year, month):
            import sys, os
            from deutschland import feiertage
            from deutschland.feiertage.api import default_api
            with feiertage.ApiClient() as api_client:
                api_instance = default_api.DefaultApi(api_client)
                nur_land = "BW" # only check for the federal state of Baden-Württemberg
                nur_daten = 1   # dismiss additional information about the day

                try:
                    feiertage_api_response = api_instance.get_feiertage(str(2000), nur_land=nur_land, nur_daten=nur_daten)
                except feiertage.ApiException as e:
                    print("Exception when calling Feiertage API -> get_feiertage: %s\n"%e)
                    sys.exit(os.EX_UNAVAILABLE)
            
            while True:
                day = randint(1,29)
                d = date(year, month, day)
                if d.weekday() <= 4 and not d in feiertage_api_response:
                    return d
        
        def random_start_time(min, max):
            return randint(min, max+1)

        def random_pause(min, max):
            return randint(min, max+1)
        
        timeblocks_left = len(timeblocks)
        
        # Pause wird Zufällig eingefügt. Ab 20h müssen 2 Blöcke pro Tag gemacht werden um genug Arbeitszeit unterzubringen
        if self.total_work_hours < 20:
            p_2blocks = 0.3
        else:
            p_2blocks = 1

        dates = []
        while timeblocks_left > 0:
            d = make_workday_date(year, month)
            if d not in dates:
                dates.append(d)
                timeblocks_left -= 1
                work_time = timeblocks.pop()
                start_time = random_start_time(self.min_start_time, self.max_start_time)
                pause = 0
                
                # fügt zufällig eine Pause und einen 2. Arbeitsblock ein
                if p_2blocks >= rand() and timeblocks_left > 0:
                    timeblocks_left -= 1
                    pause = random_pause(self.min_pause, self.max_pause)
                    work_time += timeblocks.pop()
                
                end_time = start_time + work_time + pause
                self.add_work(job, d, start_time, end_time, pause, work_time)