from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from flask_login import login_required, current_user
from models import Transaction, UserAchievement, Achievement, UserMision, db
from utils import calcular_impacto_ambiental, obtener_ranking_estudiantes, estadisticas_globales, asignar_misiones
from config import Config
from datetime import date, timedelta
from forms import RegistroForm, LoginForm, RequestResetForm, ResetPasswordForm, ChangePasswordForm
from flask_babel import gettext as _

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página de inicio"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal del estudiante"""
    # Actualizar racha y asignar misiones
    current_user.actualizar_racha()
    asignar_misiones(current_user)
    
    # Obtener misiones activas
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    misiones_activas = UserMision.query.filter(
        UserMision.user_id == current_user.id,
        UserMision.completada == False,
        UserMision.fecha_asignacion >= start_of_week
    ).order_by(UserMision.fecha_asignacion.desc()).all()
    
    # Calcular progreso al siguiente nivel
    niveles = Config.NIVELES
    nivel_actual = current_user.nivel
    puntos_actuales = current_user.puntos_totales
    
    # Encontrar siguiente nivel
    siguiente_nivel = None
    puntos_siguiente = None
    for nivel, puntos_min in sorted(niveles.items(), key=lambda x: x[1]):
        if puntos_min > puntos_actuales:
            siguiente_nivel = nivel
            puntos_siguiente = puntos_min
            break
    
    # Si ya es Eco Maestro
    if not siguiente_nivel:
        siguiente_nivel = "Eco Maestro"
        puntos_siguiente = puntos_actuales
    
    # Calcular porcentaje de progreso
    nivel_keys = list(niveles.keys())
    if nivel_actual in nivel_keys:
        idx_actual = nivel_keys.index(nivel_actual)
        puntos_nivel_actual = niveles[nivel_actual]
        
        if idx_actual < len(nivel_keys) - 1:
            puntos_siguiente_nivel = niveles[nivel_keys[idx_actual + 1]]
            rango = puntos_siguiente_nivel - puntos_nivel_actual
            progreso = ((puntos_actuales - puntos_nivel_actual) / rango) * 100
        else:
            progreso = 100
    else:
        progreso = 0
    
    # Obtener últimas transacciones
    ultimas_transacciones = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.fecha.desc())\
        .limit(5)\
        .all()
    
    # Obtener logros recientes
    logros_recientes = UserAchievement.query.filter_by(user_id=current_user.id)\
        .order_by(UserAchievement.fecha_obtencion.desc())\
        .limit(3)\
        .all()
    
    # Calcular impacto ambiental
    impacto = calcular_impacto_ambiental(current_user.id)
    
    # Obtener ranking
    ranking = obtener_ranking_estudiantes(10)
    posicion_usuario = next((i+1 for i, u in enumerate(ranking) if u.id == current_user.id), None)
    
    return render_template('index.html',
                         progreso=min(progreso, 100),
                         siguiente_nivel=siguiente_nivel,
                         puntos_siguiente=puntos_siguiente,
                         ultimas_transacciones=ultimas_transacciones,
                         logros_recientes=logros_recientes,
                         impacto=impacto,
                         ranking=ranking[:5],
                         posicion_usuario=posicion_usuario,
                         misiones_activas=misiones_activas)


@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # --- 1. LÓGICA DE CAMBIO DE CONTRASEÑA ---
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash(_('La contraseña actual es incorrecta.'), 'danger')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash(_('¡Tu contraseña ha sido actualizada exitosamente!'), 'success')
            return redirect(url_for('main.profile'))

    # --- 2. LÓGICA DE DATOS DEL PERFIL ---
    transacciones = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.fecha.desc()).all()
    
    logros_obtenidos = UserAchievement.query.filter_by(user_id=current_user.id).all()
    logros_ids = [l.achievement_id for l in logros_obtenidos]
    todos_logros = Achievement.query.all()
    
    try:
        impacto = calcular_impacto_ambiental(current_user.id)
    except Exception:
        impacto = {'co2': 0, 'agua': 0, 'energia': 0}
    
    total_reciclajes = Transaction.query.filter_by(user_id=current_user.id, tipo='reciclaje').count()
    total_quizzes = Transaction.query.filter_by(user_id=current_user.id, tipo='quiz').count()
    total_canjes = Transaction.query.filter_by(user_id=current_user.id, tipo='canje').count()
    
    return render_template('profile/profile.html', 
                           title=_('Mi Perfil'), 
                           form=form,
                           transacciones=transacciones,
                           todos_logros=todos_logros,
                           logros_obtenidos=logros_ids,
                           impacto=impacto,
                           total_reciclajes=total_reciclajes,
                           total_quizzes=total_quizzes,
                           total_canjes=total_canjes)
    

@main_bp.route('/rankings')
@login_required
def rankings():
    """Página de rankings"""
    from utils import obtener_ranking_facultades, obtener_ranking_carreras
    
    ranking_estudiantes = obtener_ranking_estudiantes(20)
    ranking_facultades = obtener_ranking_facultades()
    ranking_carreras = obtener_ranking_carreras()
    stats = estadisticas_globales()
    
    return render_template('rankings/rankings.html',
                         ranking_estudiantes=ranking_estudiantes,
                         ranking_facultades=ranking_facultades,
                         ranking_carreras=ranking_carreras,
                         stats=stats)

@main_bp.route('/language/<lang>')
def set_language(lang=None):
    """Establece el idioma de la sesión."""
    if lang in Config.LANGUAGES:
        session['language'] = lang
    # Redirigir a la página anterior o al dashboard
    return redirect(request.referrer or url_for('main.dashboard'))


@main_bp.route('/logro/<int:logro_id>')
def logro_detalle(logro_id):
    """Página de detalle de un logro"""
    logro = Achievement.query.get_or_404(logro_id)
    return render_template('profile/logro_detalle.html', logro=logro)
