import datetime
import pandas as pd
from expedia_parse import parse
import json

def generate_permu(source, destination, daterange):
    date_format = '%m/%d/%Y'
    start_date = datetime.datetime.strptime(daterange[0], date_format)
    end_date = datetime.datetime.strptime(daterange[1], date_format)
    all_perms = [(source, destination, start_date), (source, destination, end_date)]
    new_date = start_date + datetime.timedelta(days=1)
    while new_date < end_date:
        all_perms.append((source, destination, new_date))
        new_date = new_date + datetime.timedelta(days=1)
    return all_perms


def gather_permutation_data(params):
    source, destination, date = params
    print("Fetching flight details {}-{}-{}".format(source, destination, date))
    scraped_data = parse(source,destination,date)
    print("Writing data to output file")
    with open('%s-%s-flight-results.json'%(source,destination),'w') as fp:
        json.dump(scraped_data,fp,indent = 4)

def to_mil_time(civ_time):
    add_hours = 0
    if 'pm' in civ_time:
        add_hours = 12
    civ_time = civ_time.strip('amp')
    parts = civ_time.split(':')
    hours = int(parts[0])+add_hours
    if hours == 12:
        hours = 0
    if hours == 24:
        hours = 12
    if len(str(hours)) == 1:
        hours = '0{}'.format(hours)
    mins = parts[1]
    return '{}:{}'.format(hours, mins)


def aggregate_entrys(scraped_data):
    count = 0
    for entry in scraped_data:
        if entry['stops'] != 'Nonstop':
            pass
        else:
            if count == 0:
                final = pd.DataFrame.from_dict(entry)
                count += 1
            else:
                df = pd.DataFrame.from_dict(entry)
                final = final.append(df)
    return final