
from flask import Flask, request, url_for
from flask.ext.micropub import Micropub


app = Flask(__name__)
micropub = Micropub(app)


@app.route('/micropub-callback')
@micropub.authorized_handler
def micropub_callback(me, token, next_url, error):
    return """
    <!DOCTYPE html>
    <html>
    <body>
    <ul>
    <li>me: {}</li>
    <li>token: {}</li>
    <li>next: {}</li>
    <li>error: {}</li>
    </ul>
    </body>
    </html>
    """.format(me, token, next_url, error)


@app.route('/')
def index():
    me = request.args.get('me')
    if me:
        return micropub.authorize(
            me, url_for('micropub_callback', _external=True))
    return """
    <!DOCTYPE html>
    <html>
    <body>
    <form action="" method="GET">
    <input type="text" name="me" placeholder="your domain.com"/>
    <button type="submit">Authorize</button>
    </form>
    </body>
    </html>
    """


if __name__ == '__main__':
    app.run(debug=True)
