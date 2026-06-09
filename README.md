# Assets

A minimal file server with token-based access control and request logging. Each file is identified by a token that independently permits GET (download) and POST (upload), both, or neither. All requests are logged with timestamp, IP, user agent, and referrer.

## Setup

Dependencies: Python 3, Flask, Gunicorn

Run the setup script with your chosen install path:

```sh
bash setup.sh /path/to/install
```

This will:
- Create a Python virtual environment and install Flask and Gunicorn
- Register and start an `assets.service` systemd unit

The service sets the following environment variables:

| variable | value |
|---|---|
| `DATABASE_PATH` | `<install_path>/assets.db` |
| `INDEX_PATH` | `<install_path>/index.html` |

The server binds to `127.0.0.1:7000`. To expose it publicly, place a reverse proxy (e.g. nginx) in front of it.

## Database

The database is created automatically on first run with two tables: `assets` and `logs`.

### assets

| column | type | description |
|---|---|---|
| `serial` | integer | primary key |
| `path` | text | absolute path to the file |
| `token` | text | unique access token |
| `attach` | boolean | serve as attachment |
| `upload` | boolean | allow POST |
| `download` | boolean | allow GET |
| `description` | text | optional note |

Add a file manually:

```sql
INSERT INTO assets (path, token, attach, upload, download, description)
VALUES ('/path/to/file.pdf', 'my-token', 0, 0, 1, 'some file');
```

### logs

Records every request: token, method, HTTP status, time, IP address, user agent, referrer.

## Endpoints

| method | path | behavior |
|---|---|---|
| GET | `/` | serves `index.html` |
| GET | `/<token>` | downloads the file if `download = 1` |
| POST | `/<token>` | saves uploaded file to `path` if `upload = 1` |

Returns 403 if the method is not permitted for the token, 404 if the token doesn't exist or the file is missing, 400 if a POST is made without a `file` field.

## GUI

`index.html` provides a minimal browser interface for download and upload. It is self-contained and has no dependencies.
