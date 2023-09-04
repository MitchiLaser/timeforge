#!/usr/bin/env python3
# -*- encoding: utf8 -*-

import random
import requests
import os
import sys
import typing
from datetime import date, datetime, time


# store all the table data in an internal data structure

# a class to store every row in the table (=every single working day) in an internal data structure
class Day:
    def __init__(self, job, date, start_time, end_time, pause, work_hours):
        self.job = job                           # Job description
        self.date = date                          # the date of the day
        self.start_time = self.time_from_h(start_time)  # working start time
        self.end_time = self.time_from_h(end_time)    # working end time
        self.work_hours = self.time_from_h(work_hours)  # total working hours per day
        self.pause = self.time_from_h(pause)       # total pause hours per day

    def __lt__(self, other):
        return self.date < other.date

    def time_from_h(self, hours):
        return time(hour=int(hours), minute=int(hours * 60 % 60))

# a class to store the whole content of the table (=a month) internally


class Month_Dataset:
    def __init__(self, year, month, total_work_hours, job, feiertage):
        # values which define the working times
        self.min_timeblock = 2     # the minimal amount of working time per day
        self.max_timeblock = 4     # the maximum of working time at once (there might be longer blocks but then they have brakes in between
        self.min_pause = 2     # minimal amount of pause time if the working time is greater than self.max_timeblock
        self.max_pause = 3     # maximal amount of pause per day
        self.min_start_time = 8     # earliest time to start the day
        self.max_start_time = 23 - 2 * self.max_timeblock - self.max_pause  # latest time to end the day    # TODO: Comment why this is calculated that way

        self.feiertage = feiertage

        self.month = month
        self.year = year
        self.total_work_hours = total_work_hours
        self.days = []
        # TODO: put this function call return value directly into the function call one line below
        self.timeblocks = self.make_timeblocks(self.total_work_hours)
        self.generate_content(job)  # fill the table with content

    def make_timeblocks(self, work_hours_left):
        # Create an array with random time blocks which in sum fill the whole working time for a month
        timeblock_array = []
        while work_hours_left > 0:
            # TODO: Check weather the call of the random function is done properly
            timeblock_length = random.randint(self.min_timeblock, self.max_timeblock)
            if work_hours_left - timeblock_length < 0:
                timeblock_length = work_hours_left

            timeblock_array.append(timeblock_length)
            work_hours_left -= timeblock_length
        return timeblock_array

    def add_work(self, job, date, start_time, end_time, pause, work_hours):
        self.days.append(Day(job, date, start_time, end_time, pause, work_hours))

    def year_is_leap_year(year) -> bool:
        if ((year % 4 == 0 and year % 100 != 0) or year % 400 == 0):
            return True
        return False

    def days_of_month(self, month: int, year: int) -> int:
        if month == 2 and self.year_is_leap_year(year):
            return 29
        number_of_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return number_of_days_in_month[month-1]

    def generate_content(self, job):

        def suggest_day_of_month():
            while True:
                day = random.randint(1, self.days_of_month(self.month, self.year))  # random day from the 1st to the last day of the month
                d = date(self.year, self.month, day)
                if d.weekday() <= 4 and not d in self.feiertage:
                    return d

        # brakes will be added randomly. At 20h of total working time per day two hours of work have to be done to fit everything into the table
        if self.total_work_hours < 20:
            p_2blocks = 0.3
        else:
            p_2blocks = 1

        dates = []

        timeblocks_left = len(self.timeblocks)
        while timeblocks_left > 0:
            d = suggest_day_of_month()
            if not d in dates:
                dates.append(d)
                timeblocks_left -= 1
                work_time = self.timeblocks.pop()  # get latest entry of timeblock list
                start_time = random.randint(self.min_start_time, self.max_start_time)    # generate random time to start the day
                pause = 0

                # add a random break and a second working block
                if p_2blocks >= random.uniform(0, 1) and timeblocks_left > 0:
                    timeblocks_left -= 1
                    pause = random.randint(self.min_pause, self.max_pause)
                    work_time += self.timeblocks.pop()

                end_time = start_time + work_time + pause
                self.add_work(job, d, start_time, end_time, pause, work_time)
