from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models import db, Material, Reward, User, Transaction
from utils import estadisticas_globales
from forms import AjustarPuntosForm # Asegúrate de importar el nuevo form
from models import User, Transaction # Asegúrate de importar User y Transaction

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator para verificar que el usuario es admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acceso denegado. Solo para administradores.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Dashboard de administrador"""
    stats = estadisticas_globales()
    
    # Usuarios recientes
    usuarios_recientes = User.query.filter_by(is_admin=False)\
        .order_by(User.fecha_registro.desc())\
        .limit(10)\
        .all()
    
    # Transacciones recientes
    transacciones_recientes = Transaction.query\
        .order_by(Transaction.fecha.desc())\
        .limit(15)\
        .all()
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         usuarios_recientes=usuarios_recientes,
                         transacciones_recientes=transacciones_recientes)


@admin_bp.route('/materiales')
@login_required
@admin_required
def materiales():
    """Gestión de materiales"""
    materiales = Material.query.all()
    return render_template('admin/materials.html', materiales=materiales)


@admin_bp.route('/materiales/toggle/<int:material_id>')
@login_required
@admin_required
def toggle_material(material_id):
    """Activar/desactivar material"""
    material = Material.query.get_or_404(material_id)
    material.activo = not material.activo
    db.session.commit()
    
    estado = 'activado' if material.activo else 'desactivado'
    flash(f'Material {material.nombre} {estado}.', 'success')
    return redirect(url_for('admin.materiales'))


@admin_bp.route('/materiales/crear', methods=['POST'])
@login_required
@admin_required
def crear_material():
    """Crear nuevo material"""
    try:
        nuevo_material = Material(
            nombre=request.form.get('nombre'),
            categoria=request.form.get('categoria'),
            puntos_valor=int(request.form.get('puntos')),
            unidad_medida=request.form.get('unidad'),
            impacto_co2=float(request.form.get('co2')),
            impacto_agua=float(request.form.get('agua')),
            activo=True
        )
        
        db.session.add(nuevo_material)
        db.session.commit()
        
        flash(f'Material "{nuevo_material.nombre}" creado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear material: {str(e)}', 'danger')
    
    return redirect(url_for('admin.materiales'))


@admin_bp.route('/recompensas')
@login_required
@admin_required
def recompensas():
    """Gestión de recompensas"""
    recompensas = Reward.query.all()
    return render_template('admin/rewards.html', recompensas=recompensas)


@admin_bp.route('/recompensas/crear', methods=['POST'])
@login_required
@admin_required
def crear_recompensa():
    """Crear nueva recompensa"""
    try:
        nueva_recompensa = Reward(
            nombre=request.form.get('nombre'),
            descripcion=request.form.get('descripcion'),
            categoria=request.form.get('categoria'),
            puntos_costo=int(request.form.get('puntos')),
            stock_disponible=int(request.form.get('stock')),
            activo=True
        )
        
        db.session.add(nueva_recompensa)
        db.session.commit()
        
        flash(f'Recompensa "{nueva_recompensa.nombre}" creada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear recompensa: {str(e)}', 'danger')
    
    return redirect(url_for('admin.recompensas'))


@admin_bp.route('/recompensas/toggle/<int:recompensa_id>')
@login_required
@admin_required
def toggle_recompensa(recompensa_id):
    """Activar/desactivar recompensa"""
    recompensa = Reward.query.get_or_404(recompensa_id)
    recompensa.activo = not recompensa.activo
    db.session.commit()
    
    estado = 'activada' if recompensa.activo else 'desactivada'
    flash(f'Recompensa {recompensa.nombre} {estado}.', 'success')
    return redirect(url_for('admin.recompensas'))


@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    """Gestión de usuarios (Lista)"""
    # Listamos todos los usuarios no administradores
    usuarios = User.query.filter_by(is_admin=False).order_by(User.id.desc()).all()
    return render_template('admin/users.html', usuarios=usuarios)

@admin_bp.route('/usuario/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def ver_usuario(user_id):
    """
    Ver detalle de usuario y Gestionar Cuenta (RF023 Ajustar Puntos)
    """
    user = User.query.get_or_404(user_id)
    form = AjustarPuntosForm()

    # Lógica RF023: Ajustar Puntos
    if form.validate_on_submit():
        cantidad = form.puntos.data
        justificacion = form.justificacion.data
        
        # Usamos el método existente agregar_puntos que ya maneja transacciones
        # Si la cantidad es negativa, restará puntos automáticamente.
        user.agregar_puntos(
            cantidad, 
            'ajuste_admin', 
            f"Ajuste manual Admin: {justificacion}"
        )
        
        db.session.commit()
        flash(f'Se han ajustado {cantidad} puntos al usuario {user.username}.', 'success')
        return redirect(url_for('admin.ver_usuario', user_id=user.id))

    # Obtener historial reciente del usuario para contexto
    transacciones = Transaction.query.filter_by(user_id=user.id)\
        .order_by(Transaction.fecha.desc()).limit(10).all()

    return render_template('admin/user_detail.html', 
                         user=user, 
                         form=form, 
                         transacciones=transacciones)

@admin_bp.route('/usuario/toggle/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_usuario(user_id):
    """
    RF024: Desactivar/Activar Cuenta
    """
    user = User.query.get_or_404(user_id)
    
    # No permitir desactivarse a sí mismo si fuera el caso
    if user.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta.', 'danger')
        return redirect(url_for('admin.usuarios'))

    user.activo = not user.activo
    db.session.commit()
    
    estado = 'activada' if user.activo else 'desactivada'
    flash(f'La cuenta de {user.username} ha sido {estado}.', 'success')
    
    return redirect(url_for('admin.ver_usuario', user_id=user.id))