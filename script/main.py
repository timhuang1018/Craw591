#!/usr/bin/env python3

import time
import json

import requests
from bs4 import BeautifulSoup

from logger import logger
from constants import (
    API_URL, ROOT_URL, CONDITIONS, WEB_URL_FORMAT_STR, HEADERS,
    PARSE_INTERVAL_IN_SECONDS, MAP_URL_FORMAT_STR
)

cache = set()
url = "https://house-api.herokuapp.com/house"
header = {
    "token": "crawl591coronavirusisfromwuhan",
    "Content-type": "application/json",
    "charset": "utf-8"
}


class CrawlControl:
    def __init__(self):
        self.is_crawler_looping = True


crawler1 = CrawlControl()


def get_houses(session):
    logger.info('requests 591 API...')
    if CONDITIONS['regionid'] == 3:
        CONDITIONS['section'] = "34,37,38"
    else:
        CONDITIONS.pop('section', None)

    response = session.get(API_URL, params=CONDITIONS)

    try:
        data = response.json()['data']
    except KeyError:
        logger.debug("response.json()['data']: {}".format(response.json()['data']))
        logger.error("Cannnot get data from response.json['data']")
    except Exception:
        logger.debug("response: {}".format(response.text))
        raise
    else:
        houses = data.get('data', [])
        logger.info("receive {} datas".format(len(houses)))
        # if data number less than 30 means this regionid's data is use up, fetch next one
        # link to check region id mapping
        # https://github.com/g0v/tw-rental-house-data/blob/master/crawler/crawler/spiders/all_591_cities.py
        if len(houses) < 30:
            CONDITIONS['firstRow'] = 0
            CONDITIONS['regionid'] += 2
        # not sure if it crawling will actually stop ... (fix)
        if CONDITIONS['regionid'] >= 5:
            crawler1.is_crawler_looping = False
            logger.info("crawling stop + {}".format(crawler1.is_crawler_looping))

        for house in houses:
            yield house


def log_house_info(house):
    # print(house)
    logger.info(
        "名稱：{}-{}-{}".format(
            house['region_name'],
            house['section_name'],
            house['fulladdress'],
        )
    )
    # logger.info("網址：{}".format(WEB_URL_FORMAT_STR.format(house['post_id'])))
    # logger.info("租金：{} {}".format(house['price'], house['unit']))
    # logger.info("坪數：{} 坪".format(house['area']))
    # logger.info("格局：{}".format(house['layout']))
    # logger.info("更新時間：{}".format(time.ctime(house['refreshtime'])))
    # logger.info("\n")


def search_houses(session):
    houses = get_houses(session)
    for house in houses:
        if house['post_id'] in cache:
            continue

        log_house_info(house)
        save_house(house)
        cache.update([house['post_id']])


#   "houseId":1,
#   "userId":2,
#   "postId":0,
#   "regionId":0,
#   "regionName":"string",
#   "sectionId":0,
#   "streetId":0,
#   "type":0,
#   "kind":0,
#   "floor":0,
#   "allFloor":0,
#   "room":0,
#   "area":0.0,
#   "price":0,
#   "cover":"string",
#   "updateTime":1578233035,
#   "closed":0,
#   "condition":"string",
#   "sectionName":"string",
#   "fullAddress":"string",
#   "streetName":"string",
#   "alleyName":"string",
#   "caseName":"string",
#   "layout":"string",
#   "caseId":0,
#   "iconClass":"string",
#   "kindName":"string",
#   "corordinateX":0.0,
#   "corordinateY":0.0
# }


def save_house(house):
    raw = {
        "houseId": house['id'],
        "userId": house['user_id'],
        "type": house['type'],
        "kind": house['kind'],
        "postId": house['post_id'],
        "regionId": house['regionid'],
        "regionName": house['regionname'],
        "sectionName": house['sectionname'],
        "sectionId": house['sectionid'],
        "streetId": house['streetid'],
        "streetName": house['street_name'],
        "alleyName": house['alley_name'],
        "caseName": house['cases_name'],
        "caseId": house['cases_id'],
        "layout": house['layout'],
        "room": house['room'],
        "area": house['area'],
        "floor": house['floor'],
        "allFloor": house['allfloor'],
        "updateTime": house['updatetime'],
        "condition": house['condition'],
        "cover": house['cover'],
        # "refreshTime":house['refreshtime'],
        "closed": house['closed'],
        "kindName": house['kind_name'],
        "iconClass": house['icon_class'],
        "fullAddress": house['fulladdress']
    }
    target = MAP_URL_FORMAT_STR.format(raw['houseId'])
    res = requests.get(target, headers=header)
    get_price = house['price']
    is_string = isinstance(get_price, str)
    # print(is_string)
    if is_string:
        raw['price'] = int(get_price.replace(',', ""))
    else:
        raw['price'] = get_price

    html = res.content
    soup = BeautifulSoup(html, "html.parser")
    raw["coordinateX"] = soup.find(id="lng").get('value') if soup.find(id="lng") else ""
    raw["coordinateY"] = soup.find(id="lat").get('value') if soup.find(id="lat") else ""
    # print(soup.find(id="lng").get('value'))
    # print(soup.find(id="lat").get('value'))
    json_body = json.dumps(raw)
    # print(json_body)
    # time.sleep(3)
    response = requests.post(url, data=json_body, headers=header)
    print(response.text)
    # print(response.status_code)


def set_csrf_token(session):
    r = session.get(ROOT_URL)
    soup = BeautifulSoup(r.text, 'html.parser')
    for tag in soup.select('meta'):
        if tag.get('name', None) == 'csrf-token':
            csrf_token = tag.get('content')
            session.headers = HEADERS
            session.headers['X-CSRF-TOKEN'] = csrf_token
    else:
        print('No csrf-token found')


def main():
    session = requests.Session()

    while crawler1.is_crawler_looping:
        set_csrf_token(session)
        search_houses(session)
        # time.sleep(PARSE_INTERVAL_IN_SECONDS)
        time.sleep(4)
        CONDITIONS['firstRow'] += 30
        print(CONDITIONS['firstRow'])


if __name__ == "__main__":
    main()
