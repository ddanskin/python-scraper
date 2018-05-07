from bs4 import BeautifulSoup
from user_agent import generate_user_agent
import requests

TEST_EVENT = {
    'source': 'NYC',
    'destination': 'PAR',
    'departure_date': '2018-05-21',
    'return_date': '2018-05-30'}

# event is a dictionary containing: source, destination, departure_date, return_date
def kayak_lambda_handler(event):
    headers = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}
    proxies = {'https':'http://82.209.233.94', 
            'http':'http://81.22.54.60'}
    page_link = build_kayak_url(event)
    try:
        page_response = requests.get(page_link, timeout=5, headers=headers)
        import pdb; pdb.set_trace()
        if page_response.status_code == 200:
            page_content = BeautifulSoup(page_response.content, "html.parser")
            prices = page_content.find_all(class_='price')
            save_to = 'location_prices.txt'
            save_data(event['destination'], prices, save_to)
        else:
            print(page_response.status_code)
    except requests.Timeout as e:
        print("Timeout error: ", e)

def build_kayak_url(event):
    kayak_url = 'https://www.kayak.com/flights/{0}-{1}/{2}/{3}?sort=price_a'
    source = event['source']
    destination = event['destination']
    departure_date = event['departure_date']
    return_date = event['return_date']
    return kayak_url.format(source, destination, departure_date, return_date)

def save_data(row_id, data, result_file):
    str1 = row_id
    str2 = " ".join(data)
    str1 += " " + str2    
    f = open(result_file, 'a')
    f.write('\n' + str1);
    f.close()
