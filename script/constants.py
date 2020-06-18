ROOT_URL = "https://rent.591.com.tw"
API_URL = "https://rent.591.com.tw/home/search/rsList"
MAP_URL_FORMAT_STR = ROOT_URL + "/map-houseRound.html?type=1&post_id={}&s=j_edit_maps&version=1"

HEADERS = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "en-US,en;q=0.9",
    'connection': "keep-alive",
    'dnt': "1",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
}

CONDITIONS = {
    'is_new_list': '1',
    'type': '1',
    'kind': '1',
    'searchtype': '1',
    'regionid': 1,
    'rentprice': '13000,40000',
    # 'patternMore': '2',
    # 'option': 'cold',
    'hasimg': '1',
    'not_cover': '1'
    , 'firstRow': 0
}

WEB_URL_FORMAT_STR = "https://rent.591.com.tw/rent-detail-{}.html"

PARSE_INTERVAL_IN_SECONDS = 1800
