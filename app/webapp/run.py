#!/usr/bin/env python

import os
from digo import app

# Used for the session
app.secret_key = os.urandom(24)

# Used for HTML cache in development
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.jinja_env.autoescape = False

app.config["JSON_SORT_KEYS"] = False

UPLOAD_FOLDER = '/upload_tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug = True)
