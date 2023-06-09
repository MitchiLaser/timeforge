import requests
import json
from datetime import date
import sys, os

def get_feiertage():
    try:
        r:str = requests.get(r"https://feiertage-api.de/api/?nur_land=BW&nur_daten=1")
    except Exception as e:
        print(f"Exception when calling Feiertage API -> get_feiertage: {e}\n")
        sys.exit(os.EX_UNAVAILABLE)
    feiertage:dict = json.loads(r.content)
    
    feiertage_datum_str = list(feiertage.values())
    feiertage_datum_str_split = [val.split('-') for val in feiertage_datum_str]
    feiertage_datum = [date(int(y),int(m),int(d)) for y,m,d in feiertage_datum_str_split]

    return feiertage_datum