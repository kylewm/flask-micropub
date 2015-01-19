# Flask-Micropub

A Flask extension to support IndieAuth and Micropub clients.


```python
from flask import Flask, request, url_for
from flask.ext.micropub import Micropub

app = Flask(__name__)
micropub = Micropub(app)


@app.route('/login')
def login():
    return micropub.authorize(
        me, redirect_url=url_for('micropub_callback', _external=True),
            scope=request.args.get('scope'))


@app.route('/micropub-callback')
@micropub.authorized_handler
def micropub_callback(resp):
    print('success!', resp.me, resp.access_token, resp.next_url, resp.error)

```

See details at https://indiewebcamp.com/IndieAuth and https://indiewebcamp.com/Micropub
