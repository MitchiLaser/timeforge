#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import argparse, argcomplete

parser = argparse.ArgumentParser(
    prog='TimeForge',
    description = 'Create fake but realistic looking working time documentation for your student job at KIT',
    epilog='For further information take a look at the Repository for this program: https://github.com/MitchiLaser/timeforge')

parser.add_argument('-n', '--name', type=str, required=True,
                   help='Name of the working person')

parser.add_argument('-m', '--month', type=str, required=True,
                    help='The month in which the job was done')

parser.add_argument('-y', '--year', type=int, required=True,
                    help='the year in which the work was done')

parser.add_argument('-t', '--time', type=float, required=True,
                    help='the amount of working time in a month') 

parser.add_argument('-p', '--personell', type=int, required=True,
                    help='personell number (please do not put it in quotation marks')

parser.add_argument('-o', '--organisation', type=str, required=True,
                    help='Name of the KIT organisational unit')

parser.add_argument('-g', '--negligible', action='store_true',
                    help='the \'geringfügig beschäftigt\' (GF) field in the form, default: False')

parser.add_argument('-u', action='store_true',
                    help='the UB field in the form, default: False') # figure out what EB stands for

parser.add_argument('-v', '--verbose', action='store_true',
                    help='more detailed information printing for debugging purpose')

argcomplete.autocomplete(parser)
args = parser.parse_args()

if args.verbose:
    from prettytable import PrettyTable
    tab = PrettyTable()
    tab.field_names = ["Parameter", "Value"]
    tab.add_row(["Name", args.name])
    tab.add_row(["Month", args.month])
    tab.add_row(["Year", args.year])
    tab.add_row(["Working Time", args.time])
    tab.add_row(["Personell number", args.personell])
    tab.add_row(["Organisation unit", args.organisation])
    tab.add_row(["GF", args.negligible])
    tab.add_row(["UB", args.u])
    tab.add_row(["Verbose", args.verbose])

    print(tab)
