import os
import dotenv
from scraper_api import ScraperAPIClient
import requests

dotenv.load_dotenv()
api = os.environ.get('APIKEY')
client = ScraperAPIClient(api)
    
def getall(asin):
    out = {}
    rq = client.get(url = f'https://www.amazon.in/dp/{asin}', autoparse = True, country_code='in').json()
    c = 0
    nametext = ''
    if len(rq['name']) > 107:
        while c < 107:
            nametext = nametext + rq['name'][c]
            c += 1
        nametext = nametext + "..."
    else:
        nametext = rq['name']
    text = ""
    a = rq['images']
    for i in a:
        if text == "":
            text = i
        else:
            text = text + f",{i}"
    text1 = ""
    b = rq['small_description'].split('\n')
    del b[0]
    if len(b) > 5:
        count = len(b) - 1
        while count > 5:
            del b[count]
            count = count - 1
        del b[5]
    for y in b:
        if text1 == "":
            text1 = y
        else:
            text1 = text1 + f"~{y}"
    out['display_name'] = nametext
    out['name'] = rq['name']
    out['price'] = rq['pricing'].split('.')[0].encode("ascii", "ignore")
    out['image'] = text
    out['descrip'] = text1
    out['rating'] = str(rq['average_rating'])
    out['availability'] = rq['availability_status'].split(',')[0]
    return out

def updatedb(asin):
    out = {}
    rq = client.get(url = f'https://www.amazon.in/dp/{asin}', autoparse = True, country_code='in').json()
    out['price'] = rq['pricing'].split('.')[0].encode("ascii", "ignore").decode('UTF-8')
    out['rating'] = str(rq['average_rating'])
    out['availability'] = rq['availability_status'].split(',')[0]
    return out