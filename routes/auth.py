import secrets
import string
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from flask_mail import Message
from models import db, User
from flask_babel import gettext as _
from forms import RegistroForm, LoginForm, RequestResetForm
from utils import actualizar_progreso_mision
from app import mail 

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# --- FUNCIONES AUXILIARES ---
def generar_clave_temporal(longitud=8):
    """Genera una contraseña aleatoria (letras y números)"""
    caracteres = string.ascii_letters + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(longitud))

def send_temp_password_email(user, temp_pass):
    """Envía la clave temporal por correo"""
    try:
        msg = Message(_('Tu Nueva Contraseña - EcoPuntos UCA'),
                      recipients=[user.email])
        
        msg.body = f'Tu contraseña temporal es: {temp_pass}'
        
        msg.html = f'''
        <div style="font-family: 'Nunito', sans-serif; padding: 20px; border: 1px solid #10b981; border-radius: 10px; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #10b981; text-align: center;">EcoPuntos UCA 🌱</h2>
            <p style="color: #333;">Hola <strong>{user.nombre_completo}</strong>,</p>
            <p>Hemos recibido una solicitud para restablecer tu contraseña.</p>
            <p>Tu <strong>Clave Temporal</strong> de acceso es:</p>
            <div style="background-color: #f3f4f6; padding: 15px; text-align: center; margin: 20px 0; border-radius: 8px;">
                <h1 style="margin: 0; letter-spacing: 3px; color: #333;">{temp_pass}</h1>
            </div>
            <p>Copia esta clave y úsala para iniciar sesión. Te recomendamos cambiarla después.</p>
            <div style="text-align: center; margin-top: 20px;">
                <a href="{url_for('auth.login', _external=True)}" style="background-color: #10b981; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Ir al Login</a>
            </div>
        </div>
        '''
        mail.send(msg)
        return True
    except Exception as e:
        print(f"❌ ERROR SMTP AL ENVIAR: {e}")
        return False

# --- RUTAS ---

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
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
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
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
    logout_user()
    flash(_('Has cerrado sesión exitosamente.'), 'info')
    return redirect(url_for('auth.login'))

# --- LÓGICA CORREGIDA: CLAVE TEMPORAL ---

@auth_bp.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RequestResetForm()
    
    if form.validate_on_submit():
        print(f"\n🔎 [DEBUG] Buscando usuario con email: {form.email.data}") # CHIVATO
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            print(f"✅ [DEBUG] Usuario encontrado: {user.username}") # CHIVATO
            
            # 1. Generar clave temporal
            temp_pass = generar_clave_temporal()
            print(f"🔑 [DEBUG] Clave generada (copiar si falla correo): {temp_pass}") # CHIVATO
            
            # 2. Guardar en BD
            user.set_password(temp_pass)
            db.session.commit()
            print("💾 [DEBUG] Clave guardada en base de datos") # CHIVATO
            
            # 3. Enviar correo
            print("📧 [DEBUG] Intentando enviar correo...") # CHIVATO
            if send_temp_password_email(user, temp_pass):
                print("🚀 [DEBUG] Correo enviado exitosamente") # CHIVATO
                flash(_('Se ha enviado una clave temporal a tu correo. Revisa Spam.'), 'success')
            else:
                print("❌ [DEBUG] Falló el envío del correo") # CHIVATO
                flash(_('Error técnico enviando el correo. Contacta a soporte.'), 'danger')
        else:
            print("❌ [DEBUG] No existe usuario con ese correo") # CHIVATO
            flash(_('Si el correo existe, recibirás instrucciones.'), 'info')
            
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_request.html', title=_('Resetear Contraseña'), form=form)

