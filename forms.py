from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import IntegerField, SelectField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Email
from flask_wtf.file import FileField, FileRequired, FileAllowed


class LoginForm(FlaskForm):
    """Форма авторизации"""
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    """Форма регистрации"""
    user_name = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Email адрес', validators=[DataRequired(), Email()])
    password_hash = PasswordField('Пароль', validators=[DataRequired()])
    confirm = PasswordField('Повторите пароль', validators=[DataRequired()])
    accept_tos = BooleanField('Я принимаю лицензионное соглашение', validators=[DataRequired()])
    submit = SubmitField('Создать учетную запись')


class AddGameForm(FlaskForm):
    """Форма добавление игры администратором"""
    game_name = StringField('Название игры', validators=[DataRequired()])
    genre = SelectField('Основной жанр', validators=[DataRequired()], default=4, coerce=str)
    description = TextAreaField('Описание игры', validators=[DataRequired()])
    system_req = TextAreaField('Системные требования', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    languages = SelectMultipleField('Поддерживаемые языки (Выбор через кнопку Ctrl)', choices=[
        ('Итальянский', 'Итальянский'),
        ('Немецкий', 'Немецкий'),
        ('Английский', 'Английский'),
        ('Русский', 'Русский'),
        ('Японский', 'Японский'),
        ('Французский', 'Французский')
    ], validators=[DataRequired()], coerce=str)
    game_year = IntegerField('Год выпуска', validators=[DataRequired()])
    image = FileField('Изображение игры', validators=[FileRequired(), FileAllowed(['jpg', 'png'])])
    count = IntegerField('Количество товара', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')


class FilterPriceForm(FlaskForm):
    """Форма фильтрации игр по цене"""
    start_price = IntegerField('Минимальная цена', validators=[DataRequired()], default=1)
    end_price = IntegerField('Максимальная цена', validators=[DataRequired()], default=2000)
    submit = SubmitField('Поиск')


class FilterGenreForm(FlaskForm):
    """Форма фильтрации игр по жанру"""
    filter_genre = SelectField('Основной жанр', validators=[DataRequired()], default='Экшен', coerce=str)
    submit = SubmitField('Поиск')


class AddGenreForm(FlaskForm):
    """Форма добавления жанра"""
    new_genre = StringField('Название жанра', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')


class ChangeCountForm(FlaskForm):
    """Форма добавления жанра"""
    new_count = StringField('Количество товара', validators=[DataRequired()], default=10)
    submit = SubmitField('Подтвердить')
