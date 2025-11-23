from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange, Length
from models import User
from flask_babel import lazy_gettext as _l

class RegistroForm(FlaskForm):
    """Formulario de Registro"""
    username = StringField(_l('Usuario'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    nombre_completo = StringField(_l('Nombre Completo'), validators=[DataRequired()])
    facultad = SelectField(_l('Facultad'), choices=[
        ('', _l('Seleccionar Facultad')),
        ('Ingeniería', _l('Ingeniería')),
        ('Ciencias Empresariales', _l('Ciencias Empresariales')),
        ('Ciencias Sociales', _l('Ciencias Sociales')),
        ('Arquitectura', _l('Arquitectura')),
        ('Derecho', _l('Derecho')),
        ('Medicina', _l('Medicina')),
    ], validators=[DataRequired()])
    carrera = StringField(_l('Carrera'), validators=[DataRequired()])
    password = PasswordField(_l('Contraseña'), validators=[DataRequired()])
    password2 = PasswordField(_l('Confirmar Contraseña'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Registrarse'))
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(_l('El nombre de usuario ya está en uso.'))
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(_l('El email ya está registrado.'))


class LoginForm(FlaskForm):
    """Formulario de Login"""
    username = StringField(_l('Usuario'), validators=[DataRequired()])
    password = PasswordField(_l('Contraseña'), validators=[DataRequired()])
    submit = SubmitField(_l('Iniciar Sesión'))


class RequestResetForm(FlaskForm):
    """Formulario para solicitar reseteo de contraseña"""
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Solicitar Reseteo de Contraseña'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(_l('No hay una cuenta con ese email. Debes registrarte primero.'))


class ResetPasswordForm(FlaskForm):
    """Formulario para resetear la contraseña"""
    password = PasswordField(_l('Nueva Contraseña'), validators=[DataRequired()])
    password2 = PasswordField(_l('Confirmar Nueva Contraseña'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Resetear Contraseña'))


class ReciclajeForm(FlaskForm):
    """Formulario de Reciclaje"""
    material_id = SelectField(_l('Material'), coerce=int, validators=[DataRequired()])
    cantidad = IntegerField(_l('Cantidad'), validators=[DataRequired(), NumberRange(min=1, max=100)])
    submit = SubmitField(_l('Registrar Reciclaje'))


class CanjeForm(FlaskForm):
    """Formulario de Canje de Recompensa"""
    submit = SubmitField(_l('Canjear'))


class ApuestaForm(FlaskForm):
    """Formulario de Apuesta Casino"""
    cantidad = IntegerField(_l('Cantidad de Puntos'), validators=[DataRequired(), NumberRange(min=10)])
    submit = SubmitField(_l('Apostar'))

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(_l('Contraseña Actual'), validators=[DataRequired()])
    new_password = PasswordField(_l('Nueva Contraseña'), validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(_l('Confirmar Nueva Contraseña'), validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField(_l('Actualizar Contraseña'))