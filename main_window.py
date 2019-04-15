from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug import secure_filename
from wtforms.validators import DataRequired
from flask import Flask, redirect, render_template, session, jsonify
from flask import request, flash, url_for, make_response
from forms import LoginForm, RegisterForm, AddGameForm, ChangeCountForm
from forms import FilterPriceForm, FilterGenreForm, AddGenreForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import datetime
from PIL import Image
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    """Таблица пользователей"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), unique=False)
    email = db.Column(db.String(128), unique=True)
    is_admin = db.Column(db.Integer, default=0)
    avatar = db.Column(db.TEXT, unique=False, default='default')

    def __repr__(self):
        return '<User {} {} {} {} {} {}>'.format(
            self.id, self.username, self.password_hash, self.email, self.is_admin, self.avatar)


class Game(db.Model):
    """Таблица игр"""
    game_id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(128), unique=True, nullable=False)
    genre = db.Column(db.String(80), unique=False)
    description = db.Column(db.TEXT, unique=False)
    system_req = db.Column(db.TEXT, default=0)
    price = db.Column(db.INTEGER, unique=False)
    languages = db.Column(db.TEXT, unique=False)
    game_year = db.Column(db.INTEGER, unique=False)
    image = db.Column(db.TEXT, unique=False, default='unknown_game.jpg')
    count = db.Column(db.INTEGER, unique=False)

    def __repr__(self):
        return '<Game {} {} {} {} {} {} {} {}>'.format(
            self.game_id, self.game_name, self.genre, self.description, self.system_req, self.price, self.game_year,
            self.languages, self.image, self.count)


class Genre(db.Model):
    """Таблица жанров игр"""
    genre_id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String(128), unique=True, nullable=False)

    def __repr__(self):
        return '<Genre {} {}>'.format(self.genre_id, self.genre_name)


class Purchase(db.Model):
    """Таблица покупок пользователей"""
    pur_id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, unique=False, nullable=False)
    game_id = db.Column(db.Integer, unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('Purchase', lazy=True))

    def __repr__(self):
        return '<Purchase {} {} {}>'.format(
            self.pur_id, self.count, self.game_id)


@app.route('/')
@app.route('/index')
def index():
    """Основая страница для обычного пользователя или для администратора
    Пароль и логин администратора: admin:superadmin
    Также имеются 2 пользователя: user:123 и user2:123 """
    db.create_all()
    if 'username' not in session:
        games = Game.query.all()
        return render_template('index.html', games=games, title='FlaskGameStore')
    if session['username'] == 'admin':
        return render_template('index_admin.html', username=session['username'], title='Управление сайтом')
    games = Game.query.filter(Game.count != 0).all()
    return render_template('index.html', username=session['username'], games=games, title='FlaskGameStore')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Страница для авторизации пользователя """
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=user_name).first()
        if user and check_password_hash(user.password_hash, password):
            session['username'] = user_name
            session['user_id'] = user.id
            return redirect('/index')
        else:
            flash('Имя пользователя или пароль не верны', 'warning')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    """ Страница для регистрации пользователя """
    form = RegisterForm()
    if form.validate_on_submit():
        user_name = form.user_name.data
        user = User(username=user_name,
                    password_hash=generate_password_hash(form.password_hash.data),
                    email=form.email.data)
        if user_name in [i.username for i in User.query.all()]:
            flash('Пользователь с таким ником уже существует', 'warning')
        elif any(user.email == item.email for item in User.query.all()):
            flash('Пользователь с таким e-mail-ом уже существует', 'warning')
        else:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template("register.html", title='Регистрация пользователя', form=form)


@app.route('/admin_games')
def admin_games():
    """ Страница просмотра и редактирования игр администратором """
    if 'username' not in session:
        return redirect('/login')
    games = Game.query.all()
    if session['username'] == 'admin':
        return render_template('admin_games.html', username=session['username'], title='Редактирование игр',
                               games=games)
    return render_template('index.html', username=session['username'], games=games, title='FlaskGameStore')


@app.route('/add_game', methods=['GET', 'POST'])
def add_game():
    """ Страница предназначенная для добавления игр в магазин администратором """
    if 'username' not in session:
        return redirect('/login')
    if session['username'] != 'admin':
        return redirect('/index')
    form = AddGameForm()
    genres = [(i.genre_name, i.genre_name) for i in Genre.query.all()]
    form.genre.choices = genres
    if form.validate_on_submit():
        filename = secure_filename(form.image.data.filename)
        server_file = 'static/img/game_images/' + filename
        form.image.data.save(server_file)
        game_image = Image.open(server_file)
        game_image = game_image.resize((300, 159), Image.ANTIALIAS)
        game_image.save(server_file)
        game = Game(game_name=form.game_name.data,
                    genre=form.genre.data,
                    description=form.description.data,
                    system_req=form.system_req.data,
                    price=form.price.data,
                    languages=', '.join(form.languages.data),
                    game_year=form.game_year.data,
                    image=filename,
                    count=form.count.data)
        if Game.query.filter_by(game_name=game.game_name).first():
            flash('Игра с таким названием уже существует', 'warning')
        else:
            db.session.add(game)
            db.session.commit()
            return redirect('/index')
    return render_template("add_game.html", title='Добавление игры', form=form, username=session['username'])


@app.route('/logout')
def logout():
    """ Функция выхода из учетной записи """
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/index')


@app.route('/game_info/<int:game_id>')
def game_info(game_id):
    """ Страница для отображения основной информации об игре """
    game = Game.query.filter_by(game_id=game_id).first()
    if 'username' in session:
        return render_template('game_info.html', game=game, username=session['username'],
                               title='Информация об игре ' + game.game_name)
    return render_template('game_info.html', game=game,
                           title='Информация об игре ' + game.game_name)


@app.route('/sort_by_price_up')
def sort_by_price_up():
    games = Game.query.order_by(Game.price).all()
    if 'username' not in session:
        return render_template('index.html', games=games, title='FlaskGameStore')
    return render_template('index.html', username=session['username'], games=games, title='FlaskGameStore')


@app.route('/sort_by_price_down')
def sort_by_price_down():
    games = Game.query.order_by(desc(Game.price)).all()
    if 'username' not in session:
        return render_template('index.html', games=games, title='FlaskGameStore')
    return render_template('index.html', username=session['username'], games=games, title='FlaskGameStore')


@app.route('/sort_by_year_down')
def sort_by_year_down():
    games = Game.query.order_by(desc(Game.game_year)).all()
    if 'username' not in session:
        return render_template('index.html', games=games, title='FlaskGameStore')
    return render_template('index.html', username=session['username'], games=games, title='FlaskGameStore')


@app.route('/sort_by_year_up')
def sort_by_year_up():
    games = Game.query.order_by(Game.game_year).all()
    if 'username' not in session:
        return render_template('index.html', games=games, title='FlaskGameStore')
    return render_template('index.html', username=session['username'], games=games, title='FlaskGameStore')


@app.route('/filter_by_genre', methods=['GET', 'POST'])
def filter_by_genre():
    form = FilterGenreForm()
    genres = [(i.genre_name, i.genre_name) for i in Genre.query.all()]
    form.filter_genre.choices = genres
    if form.validate_on_submit():
        games = Game.query.filter_by(genre=form.filter_genre.data).all()
        if 'username' not in session:
            return render_template('index.html', games=games, title='FlaskGameStore')
        return render_template('index.html', username=session['username'], games=games, title='FlaskGameStore')
    if 'username' not in session:
        return render_template('filter_by_genre.html', form=form, title='Фильтрация по цене')
    return render_template('filter_by_genre.html', username=session['username'], form=form, title='Фильтрация по жанру')


@app.route('/filter_by_price', methods=['GET', 'POST'])
def filter_by_price():
    form = FilterPriceForm()
    if form.validate_on_submit():
        if int(form.end_price.data) < int(form.start_price.data):
            flash('Неправильно заданы настройки цен', 'warning')
        else:
            games = Game.query.filter(Game.price >= form.start_price.data, Game.price <= form.end_price.data).all()
            if 'username' not in session:
                return render_template('index.html', games=games, title='FlaskGameStore')
            return render_template('index.html', username=session['username'], games=games, title='FlaskGameStore')
    if 'username' not in session:
        return render_template('filter_by_price.html', form=form, title='Фильтрация по цене')
    return render_template('filter_by_price.html', username=session['username'], form=form, title='Фильтрация по цене')


@app.route('/filter_down')
def filter_down():
    """Сброс всех фильтров и сортировок"""
    games = Game.query.all()
    if 'username' not in session:
        return render_template('index.html', games=games, title='FlaskGameStore')
    return render_template('index.html', username=session['username'], games=games, title='FlaskGameStore')


@app.route('/add_genre', methods=['GET', 'POST'])
def add_genre():
    """ Страница редактирования списка жанров администратором """
    form = AddGenreForm()
    if 'username' not in session:
        return redirect('/index')
    if session['username'] != 'admin':
        return redirect('/index')
    if form.validate_on_submit():
        genre = Genre(genre_name=form.new_genre.data)
        if Genre.query.filter_by(genre_name=genre.genre_name).first():
            flash('Жанр с таким названием уже существует', 'warning')
        else:
            db.session.add(genre)
            db.session.commit()
    genres = Genre.query.all()
    return render_template('add_genre.html', username=session['username'], form=form, title='Добавление жанра',
                           genres=genres)


@app.route('/delete_game/<int:game_id>', methods=['GET', 'POST'])
def delete_game(game_id):
    """ Удаление игры администратором """
    if 'username' not in session:
        return redirect('/index')
    game = Game.query.filter_by(game_id=game_id).first()
    if session['username'] == 'admin' and game:
        os.remove('static/img/game_images/' + game.image)
        db.session.delete(game)
        db.session.commit()
    return redirect('/admin_games')


@app.route('/delete_genre/<int:genre_id>', methods=['GET', 'POST'])
def delete_genre(genre_id):
    """ Удаление жанра администратором """
    if 'username' not in session:
        return redirect('/index')
    print(1)
    genre = Genre.query.filter_by(genre_id=genre_id).first()
    if session['username'] == 'admin' and genre:
        db.session.delete(genre)
        db.session.commit()
    return redirect('/add_genre')


@app.route('/buy_game/<int:game_id>', methods=['GET', 'POST'])
def buy_game(game_id):
    """ Добавление игры в список покупок """
    if 'username' not in session:
        return redirect('/login')
    pur = Purchase(count=1,
                   game_id=game_id,
                   user_id=session['user_id'])
    db.session.add(pur)
    Game.query.filter_by(game_id=game_id).first().count -= 1
    db.session.commit()
    return redirect('/index')


@app.route('/user_pur', methods=['GET', 'POST'])
def user_pur():
    """ Список покупок """
    if 'username' not in session:
        return redirect('/index')
    items = Purchase.query.filter_by(user_id=session['user_id']).all()
    games = []
    ids = []
    summary = 0
    for item in items:
        games.append([Game.query.filter_by(game_id=item.game_id).first(), item])
        ids.append(str(item.pur_id))
        summary += Game.query.filter_by(game_id=item.game_id).first().price
    ids = ';'.join(ids)
    return render_template('purchase.html', username=session['username'], title='Мои покупки',
                           items=games, ids=ids, check=summary)


@app.route('/change_count/<int:game_id>', methods=['GET', 'POST'])
def change_count(game_id):
    """ Страница изменения кол-ва товара """
    form = ChangeCountForm()
    if 'username' not in session:
        return redirect('/index')
    if session['username'] != 'admin':
        return redirect('/index')
    game = Game.query.filter_by(game_id=game_id).first()
    if form.validate_on_submit():
        game.count = form.new_count.data
        db.session.commit()
    return render_template('change_count.html', username=session['username'], title='Редактирование кол-ва товара',
                           form=form, game=game)


@app.route('/delete_pur/<int:pur_id>/<int:game_id>', methods=['GET', 'POST'])
def delete_pur(pur_id, game_id):
    """ Удаление покупки пользователем, товар возвращается в магазин """
    if 'username' not in session:
        return redirect('/index')
    pur = Purchase.query.filter_by(pur_id=pur_id).first()
    game = Game.query.filter_by(game_id=game_id).first()
    game.count += 1
    db.session.delete(pur)
    db.session.commit()
    return redirect('/user_pur')


@app.route('/buy_purs/<ids>', methods=['GET', 'POST'])
def but_purs(ids):
    """ Окончательная покупка товара пользователем"""
    if 'username' not in session:
        return redirect('/index')
    ids = ids.split(';')
    for i in ids:
        pur = Purchase.query.filter_by(pur_id=i).first()
        db.session.delete(pur)
        db.session.commit()
    return redirect('/user_pur')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
