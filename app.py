import sqlite3
import flask
import datetime

app = flask.Flask(__name__)
app.config['DATABASE_PATH'] = '/home/michael/assets/assets.db'
app.config['INDEX_PATH'] = '/home/michael/assets/index.html'

def initialize():
    with sqlite3.connect(app.config['DATABASE_PATH']) as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS assets (
                serial      INTEGER PRIMARY KEY,
                path        TEXT    NOT NULL,
                token       TEXT    NOT NULL UNIQUE,
                attach      BOOLEAN NOT NULL DEFAULT 0,
                upload      BOOLEAN NOT NULL DEFAULT 0,
                download    BOOLEAN NOT NULL DEFAULT 1,
                description TEXT
            );
            CREATE TABLE IF NOT EXISTS logs (
                serial      INTEGER PRIMARY KEY,
                token       TEXT,
                method      TEXT,
                status      INTEGER,
                time        TEXT,
                address     TEXT,
                agent       TEXT,
                referrer    TEXT,
                FOREIGN KEY(token) REFERENCES assets(token)
            );
        ''')


def record(token, method, status):
    with sqlite3.connect(app.config['DATABASE_PATH']) as conn:
        conn.execute('INSERT INTO logs (token, method, status, time, address, agent, referrer) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (
                token,
                method,
                status,
                datetime.datetime.now().isoformat(),
                flask.request.headers.get('X-Real-IP', flask.request.remote_addr),
                flask.request.headers.get('User-Agent', ''),
                flask.request.headers.get('Referer', ''),
            )
        )


@app.route('/')
def index():
    return flask.send_file(app.config['INDEX_PATH'])


@app.route('/<string:token>', methods=['GET', 'POST'])
def serve(token):
    method = flask.request.method

    with sqlite3.connect(app.config['DATABASE_PATH']) as conn:
        row = conn.execute('SELECT path, attach, upload, download FROM assets WHERE token = ?', (token,)).fetchone()

    if row is None:
        record(token, method, 404)
        flask.abort(404)
    else:
        path, attach, upload, download = row

    if method == 'GET' and download:
        try:
            file = flask.send_file(path, as_attachment=attach)
            record(token, method, 200)
            return file
        except FileNotFoundError:
            record(token, method, 404)
            flask.abort(404)
    elif method == 'POST' and upload:
        try:
            file = flask.request.files['file']
            file.save(path)
            record(token, method, 204)
            return '', 204
        except KeyError:
            record(token, method, 400)
            flask.abort(400)
    else:
        record(token, method, 403)
        flask.abort(403)

initialize()

if __name__ == '__main__':
    app.run(debug=True)
