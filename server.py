from flask import Flask, request, abort
from datetime import timedelta, date
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import string
import random
import json

letters = string.ascii_letters
short_urls = []


class ShortURL(object):
    def __init__(self, original_url, short_link, expire_date):
        self.original_url = original_url
        self.short_link = short_link
        self.expire_date = expire_date


class CreateURLEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ShortURL):
            return {'short_link': 'http://127.0.0.1:5000/getURL/'+obj.short_link,
                    'original_url': obj.original_url, 'expire_date': str(obj.expire_date)}
        return json.JSONEncoder.default(self, obj)


class GetURLEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ShortURL):
            return {'original_url': obj.original_url, 'expire_date': str(obj.expire_date)}
        return json.JSONEncoder.default(self, obj)


def generate_short_url(original_url):
    random_string = ''.join(random.choice(letters) for i in range(15))
    expire_date = date.today() + timedelta(days=30)
    short_url = ShortURL(original_url=original_url, short_link=random_string, expire_date=expire_date)
    short_urls.append(short_url)
    return short_url


app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)


@app.route('/getURL/<url_hash>', methods=['GET'])
def get_URL(url_hash):
    element = [x for x in short_urls if x.short_link == url_hash]
    if len(element) == 0:
        abort(400)
    return json.dumps(element[0], cls=GetURLEncoder)


@app.route('/createURL', methods=['POST'])
@limiter.limit('10/hour')
def create_URL():
    if not request.json or not 'original_url' in request.json:
        abort(400)
    short_url = generate_short_url(request.json['original_url'])
    return json.dumps(short_url, cls=CreateURLEncoder)


if __name__ == '__main__':
    app.run(debug=True)
