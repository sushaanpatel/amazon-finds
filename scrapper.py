import os
import dotenv
from scraper_api import ScraperAPIClient
import requests

dotenv.load_dotenv()
api = os.environ.get('APIKEY')
client = ScraperAPIClient(api)
    
def getall(asin):
    out = {}
    rq = client.get(url = f'https://www.amazon.in/dp/{asin}', autoparse = True).json()
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
    out['name'] = rq['name']
    out['price'] = rq['pricing'].split('.')[0]
    out['image'] = text
    out['descrip'] = text1
    out['rating'] = str(rq['average_rating'])
    out['availability'] = rq['availability_status'].split(',')[0]
    return out

def updatedb(asin):
    out = {}
    rq = client.get(url = f'https://www.amazon.in/dp/{asin}', autoparse = True).json()
    out['price'] = rq['pricing'].split('.')[0]
    out['rating'] = str(rq['average_rating'])
    out['availability'] = rq['availability_status'].split(',')[0]
    return out