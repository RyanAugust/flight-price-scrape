import datetime
import sqlite3

from expedia_parse import parse
import utils
import settings
import os

home = os.path.expanduser('~')

## Inputs

source_ap = settings.source_ap
destination_ap = settings.destination_ap
today = datetime.datetime.now()
start_date = today + datetime.timedelta(days=1)
end_date = today + datetime.timedelta(days=settings.max_range)
daterange_date_fmt = '%m/%d/%Y'
daterange = (datetime.datetime.strftime(start_date, daterange_date_fmt),
             datetime.datetime.strftime(end_date, daterange_date_fmt))

all_perms = utils.generate_permu(source_ap, destination_ap, daterange)
all_perms = all_perms + utils.generate_permu(destination_ap, source_ap, daterange)
scraped_data = []
for i, trip_params in enumerate(all_perms):
	source, destination, date = trip_params[0], trip_params[1], trip_params[2]
	search_date = datetime.datetime.strftime(date, '%m/%d/%Y')
	scraped_data = scraped_data + parse(source, destination, search_date)
	print('{0}| {1}-{2} on {3} | length: {4}'.format(i, source, destination, search_date ,len(scraped_data)))

final = utils.aggregate_entrys(scraped_data)
del final['timings']
final['time_pulled'] = datetime.datetime.strftime(today, '%m/%d/%Y %H:%M')
final['departure_time'] = final['departure_time'].map(utils.to_mil_time)
final['arrival_time'] = final['arrival_time'].map(utils.to_mil_time)


db_file = '{home}/flights/flight_data.sqlite'.format(home=home)
conn = sqlite3.connect(db_file)
final.to_sql('flight_data', conn, if_exists='append')
print('Success')