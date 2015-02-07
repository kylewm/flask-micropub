from flask import Flask, request, url_for
from flask.ext.micropub import MicropubClient


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my super secret key'
micropub = MicropubClient(app)


@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
      <body>
        <form action="/authenticate" method="GET">
          <input type="text" name="me" placeholder="your domain.com"/>
          <button type="submit">Authenticate</button>
        </form>
        <form action="/authorize" method="GET">
          <input type="text" name="me" placeholder="your domain.com"/>
          <select name="scope">
            <option>read</option>
            <option>post</option>
            <option>comment</option>
          </select>
          <button type="submit">Authorize</button>
        </form>
      </body>
    </html>
    """


@app.route('/authenticate')
def authenticate():
    return micropub.authenticate(
        request.args.get('me'), next_url=url_for('index'))


@app.route('/authorize')
def authorize():
    return micropub.authorize(
        request.args.get('me'), next_url=url_for('index'),
        scope=request.args.get('scope'))


@app.route('/indieauth-callback')
@micropub.authenticated_handler
def indieauth_callback(resp):
    return """
    <!DOCTYPE html>
    <html>
      <body>
        Authenticated:
        <ul>
          <li>me: {}</li>
          <li>next: {}</li>
          <li>error: {}</li>
        </ul>
      </body>
    </html>
    """.format(resp.me, resp.next_url, resp.error)


@app.route('/micropub-callback')
@micropub.authorized_handler
def micropub_callback(resp):
    return """
    <!DOCTYPE html>
    <html>
      <body>
        Authorized:
        <ul>
          <li>me: {}</li>
          <li>endpoint: {}</li>
          <li>token: {}</li>
          <li>next: {}</li>
          <li>error: {}</li>
        </ul>
      </body>
    </html>
    """.format(resp.me, resp.micropub_endpoint, resp.access_token,
               resp.next_url, resp.error)


if __name__ == '__main__':
    app.run(debug=True)
