from flask import Flask, render_template, request, g, redirect, flash, url_for
import sqlite3
import os
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from UserLogin import UserLogin

# конфигурация
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = '123121231231231231231223'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    """Устрановление соединения с БД"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Создание БД если она не была созданна"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """Соединение с БД, если оно еще не было установленно"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


# глобальная переменная для вызываемая перед выполнением запроса
dbase = None


@app.before_request
def before_request():
    """Установления соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    """Закрываем соединение с БД если оно было устанавленно"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/")
def index():
    return render_template("main.html", menu=dbase.getMenu())


@app.route('/profile')
def our_company():
    return render_template('profile.html', menu=dbase.getMenu())


@app.route('/buy-tickets')
@login_required
def buy_tickets():
    return render_template('buy-tickets.html', menu=dbase.getMenu())


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userLogin = UserLogin().create(user)
            login_user(userLogin)
            return redirect(url_for('profile'))

        flash("Неверная пара логин/пароль", "error")

    return render_template('login.html', menu=dbase.getMenu())


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form["name"]) > 4 and len(request.form["email"]) > 4 \
            and len(request.form["psw"]) > 4 and request.form["psw"] == request.form["psw2"]:
            hash = generate_password_hash(request.form["psw"])
            res = dbase.addUser(request.form["name"], request.form["email"], hash)
            if res:
                flash("Вы успешно зарегистрированны", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")

    return render_template('register.html', menu=dbase.getMenu())


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из акаунта", "success")
    return redirect(url_for('login'))


@app.route("/profile1")
@login_required
def profile():
    return f"""<p><a href="{url_for("logout")}">Выйти из профиля</a>
                <p>user info:{current_user.get_id()}"""


if __name__ == '__main__':
    app.run(debug=True)
