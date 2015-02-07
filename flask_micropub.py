# -*- coding: utf-8 -*-
"""
    Flask-Micropub
    ==============

    This extension adds the ability to login to a Flask-based website
    using [IndieAuth](https://indiewebcamp.com/IndieAuth), and to request
    an [Micropub](https://indiewebcamp.com/Micropub) access token.
"""

import requests
import bs4
import flask
import functools
import uuid

import sys
if sys.version < '3':
    from urlparse import parse_qs
    from urllib import urlencode
else:
    from urllib.parse import urlencode, parse_qs


class MicropubClient:
    """Flask-Micropub provides support for IndieAuth/Micropub
    authentication and authorization.

    Args:
      app (flask.Flask, optional): the flask application to extend.
      client_id (string, optional): the IndieAuth client id, will be displayed
        when the user is asked to authorize this client.
    """
    def __init__(self, app=None, client_id=None):
        self.app = app
        self.client_id = client_id
        if app is not None:
            self.init_app(app, client_id)

    def init_app(self, app, client_id=None):
        """Initialize the Micropub extension if it was not given app
        in the constructor.

        Args:
          app (flask.Flask): the flask application to extend.
          client_id (string, optional): the IndieAuth client id, will be
            displayed when the user is asked to authorize this client. If not
            provided, the app name will be used.
        """
        if not self.client_id:
            if client_id:
                self.client_id = client_id
            else:
                self.client_id = app.name

    def authenticate(self, me, next_url=None):
        """Authenticate a user via IndieAuth.

        Args:
          me (string): the authing user's URL. if it does not begin with
            https?://, http:// will be prepended.
          next_url (string, optional): passed through the whole auth process,
            useful if you want to redirect back to a starting page when auth
            is complete.
            scopes. 'read' by default.

        Returns:
          a redirect to the user's specified authorization url, or
          https://indieauth.com/auth if none is provided.
        """
        redirect_url = flask.url_for(
            self.flask_endpoint_for_function(self._authenticated_handler),
            _external=True)
        return self._start_indieauth(me, redirect_url, next_url, None)

    def authorize(self, me, next_url=None, scope='read'):
        """Authorize a user via Micropub.

        Args:
          me (string): the authing user's URL. if it does not begin with
            https?://, http:// will be prepended.
          next_url (string, optional): passed through the whole auth process,
            useful if you want to redirect back to a starting page when auth
            is complete.
          scope (string, optional): a space-separated string of micropub
            scopes. 'read' by default.

        Returns:
          a redirect to the user's specified authorization
          https://indieauth.com/auth if none is provided.
        """
        redirect_url = flask.url_for(
            self.flask_endpoint_for_function(self._authorized_handler),
            _external=True)
        return self._start_indieauth(me, redirect_url, next_url, scope)

    def _start_indieauth(self, me, redirect_url, next_url, scope):
        """Helper for both authentication and authorization. Kicks off
        IndieAuth by fetching the authorization endpoint from the user's
        homepage and redirecting to it.

        Args:
          me (string): the authing user's URL. if it does not begin with
            https?://, http:// will be prepended.
          redirect_url: the callback URL that we pass to the auth endpoint.
          next_url (string, optional): passed through the whole auth process,
            useful if you want to redirect back to a starting page when auth
            is complete.
          scope (string): a space-separated string of micropub scopes.

        Returns:
          a redirect to the user's specified authorization
          https://indieauth.com/auth if none is provided.
        """

        if not me.startswith('http://') and not me.startswith('https://'):
            me = 'http://' + me
        auth_url, token_url, micropub_url = self._discover_endpoints(me)
        if not auth_url:
            auth_url = 'https://indieauth.com/auth'

        csrf_token = uuid.uuid4().hex
        flask.session['_micropub_csrf_token'] = csrf_token
        # save the endpoints so we don't have to scrape the target page again
        # right awway
        flask.session['_micropub_endpoints'] = (
            auth_url, token_url, micropub_url)

        auth_params = {
            'me': me,
            'client_id': self.client_id,
            'redirect_uri': redirect_url,
            'state': '{}|{}'.format(csrf_token, next_url or ''),
        }
        if scope:
            auth_params['scope'] = scope

        auth_url = auth_url + '?' + urlencode(auth_params)
        flask.current_app.logger.debug('redirecting to %s', auth_url)

        return flask.redirect(auth_url)

    def authenticated_handler(self, f):
        """Decorates the authentication callback endpoint. The endpoint should
        take one argument, a flask.ext.micropub.AuthResponse.
        """
        @functools.wraps(f)
        def decorated():
            resp = self._handle_authorize_response()
            return f(resp)
        self._authenticated_handler = decorated
        return decorated

    def authorized_handler(self, f):
        """Decorates the authorization callback endpoint. The endpoint should
        take one argument, a flask.ext.micropub.AuthResponse.
        """
        @functools.wraps(f)
        def decorated():
            resp = self._handle_authorize_response()
            return f(resp)
        self._authorized_handler = decorated
        return decorated

    def _handle_authenticate_response(self):
        code = flask.request.args.get('code')
        state = flask.request.args.get('state')
        redirect_uri = flask.url_for(flask.request.endpoint, _external=True)

        if state and '|' in state:
            csrf_token, next_url = state.split('|', 1)
        else:
            csrf_token = next_url = None

        if not csrf_token:
            return AuthResponse(
                next_url=next_url, error='no CSRF token in response')

        if csrf_token != flask.session.get('_micropub_csrf_token'):
            return AuthResponse(
                next_url=next_url, error='mismatched CSRF token')

        if '_micropub_endpoints' in flask.session:
            auth_url = flask.session['_micropub_endpoints'][0]
        else:
            auth_url = self._discover_endpoints(
                flask.request.args.get('me'))[0]

        if not auth_url:
            return AuthResponse(
                next_url=next_url, error='no authorization endpoint')

        # validate the authorization code
        auth_data = {
            'code': code,
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'state': state,
        }
        flask.current_app.logger.debug(
            'Flask-Micropub: checking code against auth url: %s, data: %s',
            auth_url, auth_data)
        response = requests.post(auth_url, data=auth_data)
        flask.current_app.logger.debug(
            'Flask-Micropub: auth response: %d - %s', response.status_code,
            response.text)

        rdata = parse_qs(response.text)
        if response.status_code != 200:
            error_vals = rdata.get('error')
            error_descs = rdata.get('error_description')
            return AuthResponse(
                next_url=next_url,
                error='authorization failed. {}: {}'.format(
                    error_vals[0] if error_vals else 'Unknown Error',
                    error_descs[0] if error_descs else 'Unknown Error'))

        if 'me' not in rdata:
            return AuthResponse(
                next_url=next_url,
                error='missing "me" in response')

        confirmed_me = rdata.get('me')[0]
        return AuthResponse(me=confirmed_me, next_url=next_url)

    def _handle_authorize_response(self):
        authenticate_response = self._handle_authenticate_response()
        code = flask.request.args.get('code')
        state = flask.request.args.get('state')
        redirect_uri = flask.url_for(flask.request.endpoint, _external=True)

        if authenticate_response.error:
            return authenticate_response

        if '_micropub_endpoints' in flask.session:
            _, token_url, micropub_url = flask.session['_micropub_endpoints']
        else:
            _, token_url, micropub_url = self._discover_endpoints(
                flask.request.args.get('me'))

        if not token_url or not micropub_url:
            # successfully auth'ed user, no micropub endpoint
            return AuthResponse(
                me=authenticate_response.me,
                next_url=authenticate_response.next_url,
                error='no micropub endpoint found.')

        # request an access token
        token_data = {
            'code': code,
            'me': authenticate_response.me,
            'redirect_uri': redirect_uri,
            'client_id': self.client_id,
            'state': state,
        }
        flask.current_app.logger.debug(
            'Flask-Micropub: requesting access token from: %s, data: %s',
            token_url, token_data)
        token_response = requests.post(token_url, data=token_data)
        flask.current_app.logger.debug(
            'Flask-Micropub: token response: %d - %s',
            token_response.status_code, token_response.text)

        if token_response.status_code != 200:
            return AuthResponse(
                me=authenticate_response.me,
                next_url=authenticate_response.next_url,
                error='bad response from token endpoint: {}'
                .format(token_response))

        tdata = parse_qs(token_response.text)
        if 'access_token' not in tdata:
            return AuthResponse(
                me=authenticate_response.me,
                next_url=authenticate_response.next_url,
                error='response from token endpoint missing access_token: {}'
                .format(tdata))

        # success!
        access_token = tdata.get('access_token')[0]
        return AuthResponse(
            me=authenticate_response.me,
            micropub_endpoint=micropub_url,
            access_token=access_token,
            next_url=authenticate_response.next_url)

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

    @staticmethod
    def flask_endpoint_for_function(func):
        for endpt, view_func in flask.current_app.view_functions.items():
            if func == view_func:
                return endpt


class AuthResponse:
    """Authorization response, passed to the authorized_handler endpoint.

    Attributes:
      me (string): The authenticated user's URL. This will be non-None if and
        only if the user was successfully authenticated.
      micropub_endpoint (string): The endpoint to POST micropub requests to.
      access_token (string): The authorized user's micropub access token.
      next_url (string): The optional URL that was passed to authorize.
      error (string): describes the error encountered if any. It is possible
        that the authentication step will succeed but the access token step
        will fail, in which case me will be non-None, and error will describe
        this condition.
    """
    def __init__(self, me=None, micropub_endpoint=None,
                 access_token=None, next_url=None, error=None):
        self.me = me
        self.micropub_endpoint = micropub_endpoint
        self.access_token = access_token
        self.next_url = next_url
        self.error = error
