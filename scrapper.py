from bs4 import BeautifulSoup
import requests

def getall(asin):
    out = {}
    HEADERS = ({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36','Accept-Language': 'en-US en;q=0.5'})
    rq = requests.get(f'https://www.amazon.in/dp/{asin}', headers = HEADERS)
    amazon = BeautifulSoup(rq.content, "lxml")
    #--name--
    try:
        name = amazon.find("span", attrs = {"id":"productTitle"})
        text = ""
        for i in name.string.split("\n"):
            if i != '':
                text = i
        out['name'] = text
    except AttributeError:
        out['name'] = "NA"
    #--price--
    try:
        price = amazon.find("span", attrs = {"id":"priceblock_ourprice"})
        out['price'] = price.string.split('.')[0]
    except AttributeError:
        price = amazon.find("span", attrs = {"id":"priceblock_dealprice"})
        out['price'] = price.string.split('.')[0]
    #--image--
    try:
        img = amazon.find("img", attrs = {"id":"landingImage"})
        out['image'] = img['src']
    except AttributeError:
        out['image'] = "NA"
    #--rating--
    try:
        rating = amazon.find("span", attrs = {"class":"a-icon-alt"})
        out['rating'] = rating.string.split(' ')[0]
    except AttributeError:
        out['rating'] = "NA"
    #--ratingno--
    try:
        ratingno = amazon.find("span", attrs = {"id":"acrCustomerReviewText"})
        out['ratingno'] = ratingno.string
    except AttributeError:
        out['ratingno'] = "NA"
    #--availability--
    try:
        avail = amazon.find("div", attrs = {"id":"availability"})
        avail = avail.find("span")
        text = ""
        for i in avail.string.split("\n"):
            if i != '':
                text = i
        out['availability'] = text
    except AttributeError:
        out['availability'] = "NA"
    #--output dict--
    return out

def getprice(asin):
    pout = ""
    HEADERS = ({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36','Accept-Language': 'en-US en;q=0.5'})
    rq = requests.get(f'https://www.amazon.in/dp/{asin}', headers = HEADERS)
    amazon = BeautifulSoup(rq.content, "lxml")
    try:
        price = amazon.find("span", attrs = {"id":"priceblock_ourprice"})
        pout = price.string.split('.')[0]
    except AttributeError:
        price = amazon.find("span", attrs = {"id":"priceblock_dealprice"})
        pout = price.string.split('.')[0]
    return pout

def getrating(asin):
    rout = {}
    HEADERS = ({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36','Accept-Language': 'en-US en;q=0.5'})
    rq = requests.get(f'https://www.amazon.in/dp/{asin}', headers = HEADERS)
    amazon = BeautifulSoup(rq.content, "lxml")
    try:
        rating = amazon.find("span", attrs = {"class":"a-icon-alt"})
        rout['rating'] = rating.string.split(' ')[0]
    except AttributeError:
        rout['rating'] = "NA"
    try:
        ratingno = amazon.find("span", attrs = {"id":"acrCustomerReviewText"})
        rout['ratingno'] = ratingno.string
    except AttributeError:
        rout['ratingno'] = "NA"
    return rout

def getavail(asin):
    aout = ""
    HEADERS = ({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36','Accept-Language': 'en-US en;q=0.5'})
    rq = requests.get(f'https://www.amazon.in/dp/{asin}', headers = HEADERS)
    amazon = BeautifulSoup(rq.content, "lxml")
    try:
        avail = amazon.find("div", attrs = {"id":"availability"})
        avail = avail.find("span")
        text = ""
        for i in avail.string.split("\n"):
            if i != '':
                text = i
        aout = text
    except AttributeError:
        aout = "NA"
    return aout