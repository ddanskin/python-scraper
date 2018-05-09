import json
import requests
from lxml import html
from collections import OrderedDict
import argparse

def expedia_lambda_handler(event):
    for i in range(5):
        try:
            page_link = build_expedia_url(event)
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' +
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 ' +
            'Safari/537.36'}
            response = requests.get(page_link, headers=headers, verify=False)
            parser = html.fromstring(response.text)
            json_data_xpath = parser.xpath("//script[@id='cachedResultsJson']//text()")
            raw_json =json.loads(json_data_xpath[0] if json_data_xpath else '')
            data = json.loads(raw_json["content"])
            parsed_flight_data = parse_flight_data(data)
            return parsed_flight_data
        except ValueError:
            print ("Retrying...")
            return {"error": "failed to process the page",}

def build_expedia_url(event):
    url = ("https://www.expedia.com/Flights-Search?flight-type=on&starDate={2}&" +
    "endDate={3}&_xpid=11905|1&mode=search&trip=roundtrip&leg1=from:{0}," +
    "to:{1},departure:{2}TANYT&leg2=from:{1},to:{1},departure:{3}TANYT&" +
    "passengers=children:0,adults:1,seniors:0,infantinlap:Y")
    source = event.source
    destination = event.destination
    depart_date = event.depart_date
    return_date = event.return_date
    print(source,destination,depart_date,return_date)
    return url.format(source,destination,depart_date,return_date)

def parse_flight_data(flight_data):
    flight_info  = OrderedDict()
    lists=[]

    for i in flight_data['legs'].keys():
        total_distance =  flight_data['legs'][i].get("formattedDistance",'')
        exact_price = flight_data['legs'][i].get('price',{}).get('totalPriceAsDecimal','')
        departure_location_airport = flight_data['legs'][i].get('departureLocation',{}).get('airportLongName','')
        departure_location_city = flight_data['legs'][i].get('departureLocation',{}).get('airportCity','')
        departure_location_airport_code = flight_data['legs'][i].get('departureLocation',{}).get('airportCode','')
        arrival_location_airport = flight_data['legs'][i].get('arrivalLocation',{}).get('airportLongName','')
        arrival_location_airport_code = flight_data['legs'][i].get('arrivalLocation',{}).get('airportCode','')
        arrival_location_city = flight_data['legs'][i].get('arrivalLocation',{}).get('airportCity','')
        airline_name = flight_data['legs'][i].get('carrierSummary',{}).get('airlineName','')
        number_of_stops = flight_data['legs'][i].get("stops","")
        flight_duration = flight_data['legs'][i].get('duration',{})
        flight_hour = flight_duration.get('hours','')
        flight_minutes = flight_duration.get('minutes','')
        flight_days = flight_duration.get('numOfDays','')

        if number_of_stops==0:
            stop = "Nonstop"
        else:
            stop = str(number_of_stops)+' Stop'
            total_flight_duration = "{0} days {1} hours {2} minutes".format(flight_days,flight_hour,flight_minutes)
            departure = departure_location_airport+", "+departure_location_city
            arrival = arrival_location_airport+", "+arrival_location_city
            carrier = flight_data['legs'][i].get('timeline',[])[0].get('carrier',{})
            plane = carrier.get('plane','')
            plane_code = carrier.get('planeCode','')
            formatted_price = "{0:.2f}".format(exact_price)

            if not airline_name:
                airline_name = carrier.get('operatedBy','')

            timings = []
            for timeline in flight_data['legs'][i].get('timeline',{}):
                if 'departureAirport' in timeline.keys():
                    departure_airport = timeline['departureAirport'].get('longName','')
                    departure_time = timeline['departureTime'].get('time','')
                    arrival_airport = timeline.get('arrivalAirport',{}).get('longName','')
                    arrival_time = timeline.get('arrivalTime',{}).get('time','')
                    flight_timing = {
                            'departure_airport':departure_airport,
                            'departure_time':departure_time,
                            'arrival_airport':arrival_airport,
                            'arrival_time':arrival_time
                            }
                    timings.append(flight_timing)
                    flight_info={
                            'stops': stop,
                            'ticket price': formatted_price,
                            'departure': departure,
                            'arrival': arrival,
                            'flight duration': total_flight_duration,
                            'airline': airline_name,
                            'plane': plane,
                            'timings': timings,
                            'plane code': plane_code
                            }
                    lists.append(flight_info)
                    sortedlist = sorted(lists, key=lambda k: k['ticket price'],reverse=False)
                    return sortedlist

if __name__=="__main__":
        args = argparse.ArgumentParser()
        args.add_argument('source',help = 'Source airport code')
        args.add_argument('destination',help = 'Destination airport code')
        args.add_argument('depart_date',help = 'MM/DD/YYYY')
        args.add_argument('return_date',help = 'MM/DD/YYYY')

        event = args.parse_args()
        print ("Fetching flight data")
        scraped_flight_data = expedia_lambda_handler(event)
        print ("Writing data to output file")
        with open('%s_%s_results.json'%(event.source,event.destination),'w') as fp:
                json.dump(scraped_flight_data,fp,indent = 4)
