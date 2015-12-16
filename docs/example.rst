Example Usage
=============

.. code:: python

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

See example.py for a more thorough example. Protocol details at
https://indiewebcamp.com/IndieAuth and https://indiewebcamp.com/Micropub
