from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from models import db, User
from flask_babel import gettext as _
from forms import RegistroForm, LoginForm, RequestResetForm, ResetPasswordForm
from utils import actualizar_progreso_mision
from flask_mail import Message 
from app import mail # Importar la instancia global 'mail'

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def send_password_reset_email(user):
    token = user.get_reset_token()
    reset_url = url_for('auth.reset_token', token=token, _external=True)
    
    msg = Message(_('Recuperación de Contraseña - UCA Puntos Verdes'), 
                  recipients=[user.email])
    
    # 1. Cuerpo HTML (El diseño bonito)
    msg.html = render_template('auth/reset_password.html', 
                               user=user, 
                               reset_url=reset_url)
    
    # 2. Cuerpo Texto Plano (Respaldo por si el correo del usuario no carga HTML)
    msg.body = f"""Hola {user.nombre_completo},
    
Para resetear tu contraseña, visita el siguiente enlace:
{reset_url}

Si no realizaste esta solicitud, ignora este correo.
"""
    
    try:
        mail.send(msg)
        print(f"\n[EMAIL SENT] To: {user.email}\n") 
    except Exception as e:
        print(f"\n[EMAIL ERROR] No se pudo enviar el correo: {e}\n")

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de usuario"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistroForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            nombre_completo=form.nombre_completo.data,
            facultad=form.facultad.data,
            carrera=form.carrera.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(_('¡Bienvenido %(nombre)s! Tu cuenta ha sido creada. 🌱', nombre=user.nombre_completo), 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuario"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.activo:
                flash(_('Tu cuenta está desactivada. Contacta al administrador.'), 'warning')
                return redirect(url_for('auth.login'))
            login_user(user)
            # Actualizar misiones de tipo 'login'
            misiones_completadas = actualizar_progreso_mision(user, 'login')
            for mision in misiones_completadas:
                flash(_('¡Misión cumplida: %(nombre)s! Recompensa: %(puntos)s puntos.', 
                        nombre=mision.nombre, puntos=mision.recompensa_puntos), 'success')
            
            next_page = request.args.get('next')
            flash(_('¡Bienvenido de vuelta, %(nombre)s! 🌿', nombre=user.nombre_completo), 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash(_('Usuario o contraseña incorrectos. Intenta de nuevo.'), 'danger')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    """Logout de usuario"""
    logout_user()
    flash(_('Has cerrado sesión exitosamente.'), 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        # Siempre mostramos el mensaje por seguridad, exista o no el usuario
        flash(_('Se ha enviado un correo con las instrucciones para resetear tu contraseña.'), 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_request.html', title=_('Resetear Contraseña'), form=form)

@auth_bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    user = User.verify_reset_token(token)
    if user is None:
        flash(_('El token es inválido o ha expirado.'), 'warning')
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Tu contraseña ha sido actualizada. Ya puedes iniciar sesión.'), 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_token.html', title=_('Resetear Contraseña'), form=form)