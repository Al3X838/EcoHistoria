from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models import db, Material, Reward, User, Transaction
from utils import estadisticas_globales

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
    """Gestión de usuarios"""
    usuarios = User.query.filter_by(is_admin=False).all()
    return render_template('admin/users.html', usuarios=usuarios)