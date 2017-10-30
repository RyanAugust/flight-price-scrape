import json
import requests
from lxml import html
from collections import OrderedDict

def parse(source,destination,date):
    for i in range(5):
        try:
            url = "https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{0},to:{1},departure:{2}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.com".format(source,destination,date)
            response = requests.get(url)
            parser = html.fromstring(response.text)
            json_data_xpath = parser.xpath("//script[@id='cachedResultsJson']//text()")
            raw_json =json.loads(json_data_xpath[0])
            flight_data = json.loads(raw_json["content"])

            flight_info  = OrderedDict()
            lists=[]

            for i in flight_data['legs'].keys():
                exact_price = flight_data['legs'][i]['price']['totalPriceAsDecimal']

                departure_location_city = flight_data['legs'][i]['departureLocation']['airportCity']
                departure_location_airport_code = flight_data['legs'][i]['departureLocation']['airportCode']

                arrival_location_airport_code = flight_data['legs'][i]['arrivalLocation']['airportCode']
                arrival_location_city = flight_data['legs'][i]['arrivalLocation']['airportCity']
                airline_name = flight_data['legs'][i]['carrierSummary']['airlineName']

                no_of_stops = flight_data['legs'][i]["stops"]
                flight_duration = flight_data['legs'][i]['duration']
                flight_hour = int(flight_duration['hours'])
                flight_minutes = int(flight_duration['minutes'])
                if len(str(flight_minutes)) == 1:
                    flight_minutes = '0{}'.format(flight_minutes)
                flight_days = int(flight_duration['numOfDays'])
                flight_hour += (flight_days * 24)

                if no_of_stops==0:
                    stop = "Nonstop"
                else:
                    stop = str(no_of_stops)+' Stop'

                total_flight_duration = "{0}:{1}".format(flight_hour,flight_minutes)
                departure = departure_location_airport_code+", "+departure_location_city
                arrival = arrival_location_airport_code+", "+arrival_location_city
                carrier = flight_data['legs'][i]['timeline'][0]['carrier']
                plane = carrier['plane']
                airline_code = carrier['airlineCode']
                flight_number = carrier['flightNumber']
                flight_designation = '{airline_code}{flight_number}'.format(
                    flight_number=flight_number,airline_code=airline_code)
                formatted_price = "{0:.2f}".format(exact_price)

                if not airline_name:
                    airline_name = carrier['operatedBy']

                timings = []
                for timeline in  flight_data['legs'][i]['timeline']:
                    if 'departureAirport' in timeline.keys():
                        departure_airport = timeline['departureAirport']['longName']
                        departure_time = timeline['departureTime']['time']
                        departure_date = timeline['departureTime']['date']
                        arrival_airport = timeline['arrivalAirport']['longName']
                        arrival_time = timeline['arrivalTime']['time']
                        flight_timing = {
                                            'departure_airport':departure_airport,
                                            'departure_time':departure_time,
                                            'arrival_airport':arrival_airport,
                                            'arrival_time':arrival_time
                        }
                        timings.append(flight_timing)

                flight_info={'stops':stop,
                    'ticket price':formatted_price,
                    'departure':departure,
                    'arrival':arrival,
                    'flight_duration':total_flight_duration,
                    'airline':airline_name,
                    'plane':plane,
                    'timings':timings,
                    'departure_time':departure_time,
                    'arrival_time':arrival_time,
                    'flight_designation':flight_designation,
                    'departure_date':departure_date
                }
                lists.append(flight_info)
            sortedlist = sorted(lists, key=lambda k: k['ticket price'],reverse=False)
            return sortedlist

        except ValueError:
            print("Rerying...")
        return {"error":"failed to process the page",}