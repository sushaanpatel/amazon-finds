from scraper_api import ScraperAPIClient
import requests
import random

client = ScraperAPIClient("436adc828f9976294474601d9e26c625")
    
def getall(asin):
    out = {}
    rq = client.get(url = f'https://www.amazon.in/dp/{asin}', autoparse = True).json()
    # text = ""
    # text1 = ""
    # for i in range(len(rq['image'])):
    #     if i == 0:
    #         text = rq['image'][i]
    #     else:
    #         text = text + rq['image'][i] + ","
    # x = rq['small_description'].split('\n')
    # for i in range(len(x)):
    #     if i == 0:
    #         text1 = x[i]
    #     else:
    #         text1 = text1 + x[i] + ","
    out['name'] = rq['name']
    out['price'] = rq['pricing'].split('.')[0]
    out['image'] = text
    out['descrip'] = rq['small_description'].split('\n')
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

# print(getall('B095PYTSV8'))