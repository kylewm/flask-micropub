from flask import Flask, request, url_for
from flask.ext.micropub import MicropubClient


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my super secret key'
micropub = MicropubClient(app)


@app.route('/micropub-callback')
@micropub.authorized_handler
def micropub_callback(resp):
    return """
    <!DOCTYPE html>
    <html>
      <body>
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


@app.route('/')
def index():
    me = request.args.get('me')
    if me:
        return micropub.authorize(
            me, redirect_url=url_for('micropub_callback', _external=True),
            scope=request.args.get('scope'))
    return """
    <!DOCTYPE html>
    <html>
      <body>
        <form action="" method="GET">
          <input type="text" name="me" placeholder="your domain.com"/>
          <select name="scope">
            <option>read</option>
            <option>write</option>
            <option>comment</option>
          </select>
          <button type="submit">Authorize</button>
        </form>
      </body>
    </html>
    """


if __name__ == '__main__':
    app.run(debug=True)
