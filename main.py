from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request

from flask import Flask, render_template, request

import sqlite3
import os


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('main.html')


@app.route('/our-company')
def our_company():
    return render_template('our-company.html')


@app.route('/buy-tickets')
def buy_tickets():
    return render_template('buy-tickets.html')


if __name__ == '__main__':
    app.run(debug=True)
