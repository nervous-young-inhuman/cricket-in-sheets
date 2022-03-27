import requests
import json
from urllib.parse import urljoin
from functools import lru_cache
from .shhhhhh import CRICDATA_API_KEY as API_KEY

API_URL_PREFIX = "https://api.cricapi.com/v1/"
class CricketException(Exception):
    pass

def normalize_gmt_date(date):
    if not date:
        return
    # pat = re.compile(r'\+\d\d:\d\d(?::\d\d(?:\.\d\d\d\d\d\d)?)?$')
    # ignoring this now, for now assume the date lacks timezone and is utc
    # pat.search()
    return date + '+00:00'

def waterdown_match_fields(match_data):
    if not match_data:
        return

    keys = ('id', 'status', 'teams', 'name')
    return dict(
        **{key: match_data.get(key) for key in keys},
        date=normalize_gmt_date(match_data.get('dateTimeGMT')),
        winner=match_data.get('matchWinner')
    )


@lru_cache
def __cricdata():
    data = {}
    with open('./data/cricdata.json') as f:
         data = json.load(f)
    schedules = tuple(map(waterdown_match_fields, data['matchList']))
    series_id = data['info']['id']
    return dict(schedules=schedules, series_id=series_id)

def __request(*, path, method='get', params):
    def wrapper(fn, **kws):
        url = urljoin(API_URL_PREFIX, path)
        request_params = {
            **{
                param: kws[param]
                for param in params
                if param in kws
            },
            "apikey": API_KEY,
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
        }
        r = requests.request(method, url, params=request_params, headers=headers)
        if r.status_code != requests.codes.ok:
            return dict(data=None, error=f'{r.status_code}: {r.reason}')
        try:
            data = r.json()
        except json.JSONDecodeError:
            return dict(data=None, error=f'{r.status_code}: Failed to parse data as JSON.')
    
        if data.get('status') == 'success':
            try:
                processed_data = fn(data)
                return dict(data=processed_data, error=None)
            except CricketException as err:
                error, *_ = (*err.args, '{fn.__name__} calls it  an error')
                return dict(error=error, data=None)
            
        return dict(data=None, error=f'{r.status_code}: API says {data.status}')

    def deco(fn):
        return lambda **kws: wrapper(fn, **kws)
    
    return deco


def matches(*, no_cache=False):
    return __cricdata().get('schedules')


@__request(path='match_info', method='post', params=('id', 'offset'))
def __match(data):
    match_data = waterdown_match_fields(data.get('data'))
    if not match_data:
        raise CricketException('Match data empty.')
    return match_data

def match(id, *, offset=0):
    resp = __match(id=id, offset=offset)
    if resp.get('error'):
        logging.error(resp['error'])
    return resp.get('data')


SERIES_ID = __cricdata().get('series_id')
