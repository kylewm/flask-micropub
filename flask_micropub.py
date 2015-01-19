"""This extension adds the ability to login to a Flask-based website
using [IndieAuth](https://indiewebcamp.com/IndieAuth), and to request
an [Micropub](https://indiewebcamp.com/Micropub) access token.
"""

import requests
import bs4
import flask
import functools

import sys
if sys.version > '3':
    from urllib.parse import urlencode, parse_qs
else:
    from urlparse import parse_qs
    from urllib import urlencode


class Micropub:
    def __init__(self, app):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.client_id = app.name

    def authorize(self, me, redirect_uri, next=None, scope='read'):
        if not me.startswith('http://') and not me.startswith('https://'):
            me = 'http://' + me
        auth_url, token_url, micropub_url = self._discover_endpoints(me)
        if not auth_url:
            auth_url = 'https://indieauth.com/auth'

        auth_params = {
            'me': me,
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'scope': scope,
        }

        if next:
            auth_params['state'] = next

        return flask.redirect(
            auth_url + '?' + urlencode(auth_params))

    def authorized_handler(self, f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            data = self._handle_response()
            return f(*(data + args), **kwargs)
        return decorated

    def _handle_response(self):
        redirect_uri = flask.url_for(flask.request.endpoint, _external=True)
        confirmed_me = None
        access_token = None
        state = flask.request.args.get('state')
        next_url = state
        auth_url, token_url, micropub_url = self._discover_endpoints(
            flask.request.args.get('me'))

        if not auth_url:
            return (confirmed_me, access_token, next_url,
                    'no authorization endpoint')

        code = flask.request.args.get('code')
        client_id = ''

        # validate the authorization code
        response = requests.post(auth_url, data={
            'code': code,
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'state': state,
        })

        rdata = parse_qs(response.text)
        if response.status_code != 200:
            return (confirmed_me, access_token, next_url,
                    'authorization failed. {}: {}'.format(
                        rdata.get('error'), rdata.get('error_description')))

        if 'me' not in rdata:
            return (confirmed_me, access_token, next_url,
                    'missing "me" in response')

        confirmed_me = rdata.get('me')[0]

        # request an access token
        token_response = requests.post(token_url, data={
            'code': code,
            'me': confirmed_me,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'state': state,
        })

        if token_response.status_code != 200:
            return (confirmed_me, access_token, next_url,
                    'bad response from token endpoint: {}'
                    .format(token_response))

        tdata = parse_qs(token_response.text)
        if 'access_token' not in tdata:
            return (confirmed_me, access_token, next_url,
                    'response from token endpoint missing access_token: {}'
                    .format(tdata))

        access_token = tdata.get('access_token')[0]
        return confirmed_me, access_token, next_url, None

    def _discover_endpoints(self, me):
        me_response = requests.get(me)
        if me_response.status_code != 200:
            return None, None, None

        soup = bs4.BeautifulSoup(me_response.text)
        auth_endpoint = soup.find('link', {'rel': 'authorization_endpoint'})
        token_endpoint = soup.find('link', {'rel': 'token_endpoint'})
        micropub_endpoint = soup.find('link', {'rel': 'micropub'})

        return (auth_endpoint and auth_endpoint['href'],
                token_endpoint and token_endpoint['href'],
                micropub_endpoint and micropub_endpoint['href'])
