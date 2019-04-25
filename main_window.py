from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug import secure_filename
from flask import Flask, redirect, render_template, session, jsonify
from flask import request, flash, url_for, make_response
from forms import LoginForm, RegisterForm, AddGameForm, AddPublisherForm
from forms import FilterPriceForm, FilterGenreForm, AddGenreForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from PIL import Image
import os
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        user = User.query.filter_by(id=user_id).first()
        answer = {'User': {'user_id': user.id, 'user_name': user.username, 'user_email': user.email}}
        return {'user': answer}

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_id):
        args = parser.parse_args()
        abort_if_user_not_found(user_id)
        if not any(args[key] for key in ['user_name', 'password', 'email']):
            return jsonify({'error': 'Empty request'})
        if args.user_name is None and args.password is None and args.email is None:
            return jsonify({'error': 'Bad request'})
        user = User.query.filter_by(id=user_id).first()
        if args.user_name is not None:
            user.username = args.user_name
        if args.password is not None:
            user.password_hash = generate_password_hash(args.password)
        if args.email is not None:
            user.email = args.email
        db.session.commit()
        return jsonify({'success': 'OK'})


class UsersList(Resource):
    def get(self):
        user = User.query.all()
        answer = []
        for i in user:
            answer.append({"User": {'user_id': i.id, 'user_name': i.username, 'user_email': i.email}})
        return answer

    def post(self):
        args = parser.parse_args()
        if not args:
            return jsonify({'error': 'Empty request'})
        if not all(args[key] for key in ['user_name', 'password', 'email']):
            return jsonify({'error': 'Bad request'})
        try:
            user = User(username=args.user_name,
                        password_hash=generate_password_hash(args.password),
                        email=args.email)
            db.session.add(user)
            db.session.commit()
        except:
            return jsonify({'error': 'User already exists'})
        return jsonify({'success': 'OK'})


class Game(Resource):
    def get(self, game_id):
        abort_if_game_not_found(game_id)
        i = Game.query.filter_by(game_id=game_id).first()
        answer = {
            "Game": {'game_id': i.game_id, 'game_name': i.game_name, 'genre': i.genre,
                     'discription': i.description,
                     'system_requirement': i.system_req, 'price': i.price, 'languages': i.languages,
                     'game_year': i.game_year, 'count_in_storage': i.count}}
        return answer

    def delete(self, game_id):
        abort_if_game_not_found(game_id)
        game = Game.query.filter_by(game_id=game_id).first()
        db.session.delete(game)
        db.session.commit()
        return jsonify({'success': 'OK'})


class GameList(Resource):
    def get(self):
        game = Game.query.all()
        answer = []
        for i in game:
            answer.append({
                "Game": {'game_id': i.game_id, 'game_name': i.game_name, 'genre': i.genre, 'discription': i.description,
                         'system_requirement': i.system_req, 'price': i.price, 'languages': i.languages,
                         'game_year': i.game_year, 'count_in_storage': i.count}})
        return answer


api = Api(app)
api.add_resource(UsersList, '/users')
api.add_resource(User, '/users/<int:user_id>')
api.add_resource(GameList, '/games')
api.add_resource(Game, '/game/<int:game_id>')

parser = reqparse.RequestParser()
parser.add_argument('user_id', required=False, type=int)
parser.add_argument('user_name', required=False)
parser.add_argument('password', required=False)
parser.add_argument('email', required=False)


def abort_if_user_not_found(user_id):
    if not User.query.filter_by(id=user_id).first():
        abort(404, message="User {} not found".format(user_id))


def abort_if_game_not_found(game_id):
    if not Game.query.filter_by(game_id=game_id).first():
        abort(404, message="User {} not found".format(game_id))


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
    publisher = db.Column(db.String(80), unique=False)

    def __repr__(self):
        return '<Game {} {} {} {} {} {} {} {}>'.format(
            self.game_id, self.game_name, self.genre, self.description, self.system_req, self.price, self.game_year,
            self.languages, self.image, self.count, self.publisher)


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


class Publisher(db.Model):
    """Таблица издателей"""
    pub_id = db.Column(db.Integer, primary_key=True)
    pub_name = db.Column(db.String(128), unique=True, nullable=False)
    address = db.Column(db.TEXT, unique=False, nullable=False)
    telephone = db.Column(db.String(128), nullable=False)
    site = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return '<Purchase {} {} {} {}>'.format(
            self.pub_name, self.address, self.telephone, self.site)


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
            flash('Имя пользователя или пароль не верны', 'error')
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
    publishers = [(i.pub_name, i.pub_name) for i in Publisher.query.all()]
    form.genre.choices = genres
    form.publisher.choices = publishers
    if form.validate_on_submit():
        if form.image.data is not None:
            filename = secure_filename(form.image.data.filename)
            server_file = 'static/img/game_images/' + filename
            form.image.data.save(server_file)
            game_image = Image.open(server_file)
            game_image = game_image.resize((300, 159), Image.ANTIALIAS)
            game_image.save(server_file)
        else:
            filename = 'unknown_game.jpg'
        game = Game(game_name=form.game_name.data,
                    genre=form.genre.data,
                    description=form.description.data,
                    system_req=form.system_req.data,
                    price=form.price.data,
                    languages=', '.join(form.languages.data),
                    game_year=form.game_year.data,
                    image=filename,
                    count=form.count.data,
                    publisher=form.publisher.data)
        if Game.query.filter_by(game_name=game.game_name).first():
            flash('Игра с таким названием уже существует', 'warning')
        else:
            db.session.add(game)
            db.session.commit()
            return redirect('/index')
    return render_template("add_game.html", title='Добавление игры', form=form, username=session['username'])


@app.route('/game_info/<int:game_id>')
def game_info(game_id):
    """ Страница для отображения основной информации об игре """
    game = Game.query.filter_by(game_id=game_id).first()
    if 'username' in session:
        return render_template('game_info.html', game=game, username=session['username'],
                               title='Информация об игре ' + game.game_name)
    return render_template('game_info.html', game=game,
                           title='Информация об игре ' + game.game_name)


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


@app.route('/edit_game/<int:game_id>', methods=['GET', 'POST'])
def edit_game(game_id):
    form = AddGameForm()
    if 'username' not in session:
        return redirect('/index')
    game = Game.query.filter_by(game_id=game_id).first()
    genres = [(i.genre_name, i.genre_name) for i in Genre.query.all()]
    form.genre.choices = genres
    publishers = [(i.pub_name, i.pub_name) for i in Publisher.query.all()]
    form.publisher.choices = publishers
    if form.validate_on_submit():
        if form.image.data is not None:
            filename = secure_filename(form.image.data.filename)
            server_file = 'static/img/game_images/' + filename
            form.image.data.save(server_file)
            game_image = Image.open(server_file)
            game_image = game_image.resize((300, 159), Image.ANTIALIAS)
            game_image.save(server_file)
        else:
            filename = 'unknown_game.jpg'
        game.game_name = form.game_name.data
        game.genre = form.genre.data
        game.description = form.description.data
        game.system_req = form.system_req.data
        game.price = form.price.data
        game.languages = ', '.join(form.languages.data)
        game.game_year = form.game_year.data
        game.count = form.count.data
        game.image = filename
        game.publisher = form.publisher.data
        db.session.commit()
        return redirect('/admin_games')
    '''Устанавливаем дефолтные значения полей'''
    form.genre.data = game.genre
    form.game_name.data = game.game_name
    form.description.data = game.description
    form.system_req.data = game.system_req
    form.price.data = game.price
    form.game_year.data = game.game_year
    form.count.data = game.count
    form.languages.data = game.languages.split(',')
    form.publisher.data = game.publisher
    return render_template("edit_game.html", title='Редактирование игры', form=form, username=session['username'],
                           image=game.image)


@app.route('/logout')
def logout():
    """ Функция выхода из учетной записи """
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/index')


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


@app.route('/delete_genre/<int:genre_id>', methods=['GET', 'POST'])
def delete_genre(genre_id):
    """ Удаление жанра администратором """
    if 'username' not in session:
        return redirect('/index')
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


@app.route('/add_publisher', methods=['GET', 'POST'])
def add_publisher():
    form = AddPublisherForm()
    publishers = Publisher.query.all()
    if form.validate_on_submit():
        flash('Издатель успешно добавлен')
        pub = Publisher(pub_name=form.pub_name.data,
                        address=form.address.data,
                        telephone=form.telephone.data,
                        site=form.site.data)
        db.session.add(pub)
        db.session.commit()
        return redirect('/add_publisher')
    return render_template('add_publisher.html', title='Добавление издателя', form=form, username=session['username'],
                           publishers=publishers)


@app.route('/edit_publisher/<int:pub_id>', methods=['GET', 'POST'])
def edit_publisher(pub_id):
    form = AddPublisherForm()
    if 'username' not in session:
        return redirect('/index')
    pub = Publisher.query.filter_by(pub_id=pub_id).first()
    if form.validate_on_submit():
        pub.pub_name = form.pub_name.data
        pub.address = form.address.data
        pub.telephone = form.telephone.data
        pub.site = form.site.data
        db.session.commit()
        flash('Измениния прошли успешно!')
        return redirect('/edit_publisher/' + str(pub.pub_id))
    '''Устанавливаем дефолтные значения полей'''
    form.pub_name.data = pub.pub_name
    form.address.data = pub.address
    form.telephone.data = pub.telephone
    form.site.data = pub.site
    return render_template("edit_publisher.html", title='Редактирование издателя', form=form,
                           username=session['username'])


@app.route('/delete_pub/<int:pub_id>', methods=['GET', 'POST'])
def delete_pub(pub_id):
    """ Удаление покупки пользователем, товар возвращается в магазин """
    if 'username' not in session:
        return redirect('/index')
    pub = Publisher.query.filter_by(pub_id=pub_id).first()
    db.session.delete(pub)
    db.session.commit()
    return redirect('/add_publisher')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
