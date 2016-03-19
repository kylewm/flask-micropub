[![Documentation Status](https://readthedocs.org/projects/flask-micropub/badge/?version=latest)](http://flask-micropub.readthedocs.org/en/latest/?badge=latest)

[![Build Status](https://travis-ci.org/kylewm/flask-micropub.svg?branch=master)](https://travis-ci.org/kylewm/flask-micropub)

# Flask-Micropub

A Flask extension to support IndieAuth and Micropub clients.

## Authentication

Authentication uses the
[IndieAuth](https://indiewebcamp.com/IndieAuth) flow to confirm a user
controls a particular URL, without requesting any sort of permissions
or access token. Annotate an endpoint with
`@micropub.authenticated_handler` and then call
`micropub.authenticate` to initiate the login.

## Authorization

Authorization uses the full
[Micropub](https://indiewebcamp.com/Micropub) flow to authenticate a
user and then request an access token with which to make micropub
requests. Annotate an endpoint with `@micropub.authorized_handler` and
then call `micropub.authorize` to initiate the login.

## CSRF

MicropubClient provides a simple mechanism to deter Cross-Site Request
Forgery. Based on
[this Flask snippet](http://flask.pocoo.org/snippets/3/), we generate
a random string, pass it to the indieauth service via the state
parameter, and then confirm we get the same random string back later.

This helps prevent malicious sites from sending users to your
indieauth endpoint against their will.

## Example

```python
from flask import Flask, request, url_for
from flask.ext.micropub import MicropubClient

app = Flask(__name__)
micropub = MicropubClient(app)


@app.route('/login')
def login():
    return micropub.authorize(
        me, scope=request.args.get('scope'))


@app.route('/micropub-callback')
@micropub.authorized_handler
def micropub_callback(resp):
    print('success!', resp.me, resp.access_token, resp.next_url, resp.error)

```

See example.py for a more thorough example. Protocol details at
https://indiewebcamp.com/IndieAuth and
https://indiewebcamp.com/Micropub
