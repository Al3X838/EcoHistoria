from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models import db, Material, Reward, User, Transaction
from utils import estadisticas_globales
from forms import AjustarPuntosForm # Asegúrate de importar el nuevo form
from models import User, Transaction # Asegúrate de importar User y Transaction
# routes/admin.py
from models import db, Material, Reward, User, Transaction, UserReward, EducationalContent  # <--- Agregamos UserReward y EducationalContent
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


# ==================== GESTIÓN DE MATERIALES ====================

@admin_bp.route('/materiales')
@login_required
@admin_required
def materiales():
    """Get all materials and check which have been used"""
    materiales = Material.query.all()
    
    # Identificar materiales que ya han sido usados en transacciones
    materiales_usados = set()
    transacciones_reciclaje = Transaction.query.filter_by(tipo='reciclaje').all()
    
    import json
    for trans in transacciones_reciclaje:
        if trans.metadata_json:
            try:
                data = json.loads(trans.metadata_json)
                if 'material_id' in data:
                    materiales_usados.add(data['material_id'])
            except:
                pass
                
    return render_template('admin/materials.html', 
                         materiales=materiales, 
                         materiales_usados=materiales_usados)


@admin_bp.route('/materiales/crear', methods=['POST'])
@login_required
@admin_required
def crear_material():
    """Crear nuevo material"""
    try:
        nuevo_material  = Material(
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


@admin_bp.route('/materiales/editar/<int:material_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_material(material_id):
    """Editar material existente (solo si no tiene entregas)"""
    material = Material.query.get_or_404(material_id)
    
    # Verificar si el material ha sido usado
    transacciones_reciclaje = Transaction.query.filter_by(tipo='reciclaje').all()
    usado = False
    import json
    for trans in transacciones_reciclaje:
        if trans.metadata_json:
            try:
                data = json.loads(trans.metadata_json)
                if 'material_id' in data and data['material_id'] == material.id:
                    usado = True
                    break
            except:
                pass
    
    if usado:
        flash('No se puede editar este material porque ya existen entregas asociadas.', 'danger')
        return redirect(url_for('admin.materiales'))
        
    if request.method == 'POST':
        try:
            material.nombre = request.form.get('nombre')
            material.categoria = request.form.get('categoria')
            material.puntos_valor = int(request.form.get('puntos'))
            material.unidad_medida = request.form.get('unidad')
            material.impacto_co2 = float(request.form.get('co2'))
            material.impacto_agua = float(request.form.get('agua'))
            
            db.session.commit()
            flash(f'Material "{material.nombre}" actualizado exitosamente.', 'success')
            return redirect(url_for('admin.materiales'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar material: {str(e)}', 'danger')
            
    return render_template('admin/edit_material.html', material=material)


@admin_bp.route('/materiales/eliminar/<int:material_id>', methods=['POST'])
@login_required
@admin_required
def eliminar_material(material_id):
    """Eliminar material si no ha sido usado en transacciones"""
    material = Material.query.get_or_404(material_id)
    
    # Verificar si el material ha sido usado
    transacciones_reciclaje = Transaction.query.filter_by(tipo='reciclaje').all()
    import json
    for trans in transacciones_reciclaje:
        if trans.metadata_json:
            try:
                data = json.loads(trans.metadata_json)
                if 'material_id' in data and data['material_id'] == material.id:
                    flash(f'No se puede eliminar "{material.nombre}" porque ya existen entregas asociadas.', 'danger')
                    return redirect(url_for('admin.materiales'))
            except:
                pass
    
    try:
        nombre = material.nombre
        db.session.delete(material)
        db.session.commit()
        flash(f'Material "{nombre}" eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar material: {str(e)}', 'danger')
    
    return redirect(url_for('admin.materiales'))


# ==================== GESTIÓN DE RECOMPENSAS ====================

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


@admin_bp.route('/recompensas/editar/<int:recompensa_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_recompensa(recompensa_id):
    """Editar recompensa existente"""
    recompensa = Reward.query.get_or_404(recompensa_id)
        
    if request.method == 'POST':
        try:
            recompensa.nombre = request.form.get('nombre')
            recompensa.descripcion = request.form.get('descripcion')
            recompensa.categoria = request.form.get('categoria')
            recompensa.puntos_costo = int(request.form.get('puntos'))
            recompensa.stock_disponible = int(request.form.get('stock'))
            
            db.session.commit()
            flash(f'Recompensa "{recompensa.nombre}" actualizada exitosamente.', 'success')
            return redirect(url_for('admin.recompensas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar recompensa: {str(e)}', 'danger')
            
    return render_template('admin/edit_reward.html', recompensa=recompensa)


@admin_bp.route('/recompensas/eliminar/<int:recompensa_id>', methods=['POST'])
@login_required
@admin_required
def eliminar_recompensa(recompensa_id):
    """Eliminar recompensa si no ha sido canjeada"""
    recompensa = Reward.query.get_or_404(recompensa_id)
    
    # Verificar si tiene canjes asociados
    if recompensa.canjes.count() > 0:
        flash(f'No se puede eliminar "{recompensa.nombre}" porque ya ha sido canjeada.', 'danger')
        return redirect(url_for('admin.recompensas'))
    
    try:
        nombre = recompensa.nombre
        db.session.delete(recompensa)
        db.session.commit()
        flash(f'Recompensa "{nombre}" eliminada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar recompensa: {str(e)}', 'danger')
    
    return redirect(url_for('admin.recompensas'))


# ==================== GESTIÓN DE USUARIOS ====================

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

# ==================== GESTIÓN DE CUPONES (RF022) ====================

@admin_bp.route('/cupones', methods=['GET'])
@login_required
@admin_required
def cupones():
    """
    RF022: Listado y validación de cupones de canje.
    Permite buscar por código o nombre de usuario.
    """
    search_query = request.args.get('q', '').strip()
    
    # Query base optimizada con Joins
    query = UserReward.query.join(User).join(Reward).order_by(UserReward.fecha_canje.desc())
    
    if search_query:
        # Búsqueda flexible: Código, Usuario o Nombre
        query = query.filter(
            (UserReward.codigo.ilike(f'%{search_query}%')) | 
            (User.username.ilike(f'%{search_query}%')) |
            (User.nombre_completo.ilike(f'%{search_query}%'))
        )
    
    # Limitamos a 50 para no saturar la vista si hay muchos
    cupones = query.limit(50).all()
    
    return render_template('admin/coupons.html', cupones=cupones, search_query=search_query)

@admin_bp.route('/cupones/validar/<int:id>', methods=['POST'])
@login_required
@admin_required
def validar_cupon(id):
    """
    Marcar un cupón como 'entregado'
    """
    canje = UserReward.query.get_or_404(id)
    
    if canje.estado == 'entregado':
        flash('Este cupón ya fue entregado anteriormente.', 'warning')
    else:
        canje.estado = 'entregado'
        db.session.commit()
        flash(f'Cupón {canje.codigo} validado y marcado como ENTREGADO.', 'success')
        
    return redirect(url_for('admin.cupones'))


# ==================== GESTIÓN DE CONTENIDO EDUCATIVO ====================

@admin_bp.route('/educational-content', methods=['GET', 'POST'])
@login_required
@admin_required
def educational_content():
    """Gestión de contenido educativo"""
    if request.method == 'POST':
        try:
            nuevo_contenido = EducationalContent(
                titulo=request.form.get('titulo'),
                descripcion=request.form.get('descripcion'),
                link=request.form.get('link'),
                activo=True
            )
            db.session.add(nuevo_contenido)
            db.session.commit()
            flash(f'Contenido "{nuevo_contenido.titulo}" creado exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear contenido: {str(e)}', 'danger')
        return redirect(url_for('admin.educational_content'))

    contenidos = EducationalContent.query.order_by(EducationalContent.fecha_creacion.desc()).all()
    return render_template('admin/educational_content.html', contenidos=contenidos)


@admin_bp.route('/educational-content/editar/<int:id>', methods=['POST'])
@login_required
@admin_required
def editar_educational_content(id):
    """Editar contenido educativo"""
    contenido = EducationalContent.query.get_or_404(id)
    try:
        contenido.titulo = request.form.get('titulo')
        contenido.descripcion = request.form.get('descripcion')
        contenido.link = request.form.get('link')
        
        db.session.commit()
        flash(f'Contenido "{contenido.titulo}" actualizado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar contenido: {str(e)}', 'danger')
        
    return redirect(url_for('admin.educational_content'))


@admin_bp.route('/educational-content/toggle/<int:id>', methods=['POST'])
@login_required
@admin_required
def toggle_educational_content(id):
    """Activar/desactivar contenido educativo"""
    contenido = EducationalContent.query.get_or_404(id)
    contenido.activo = not contenido.activo
    db.session.commit()
    
    estado = 'activado' if contenido.activo else 'desactivado'
    flash(f'Contenido "{contenido.titulo}" ha sido {estado}.', 'success')
    return redirect(url_for('admin.educational_content'))


@admin_bp.route('/educational-content/eliminar/<int:id>', methods=['POST'])
@login_required
@admin_required
def eliminar_educational_content(id):
    """Eliminar contenido educativo"""
    contenido = EducationalContent.query.get_or_404(id)
    try:
        titulo = contenido.titulo
        db.session.delete(contenido)
        db.session.commit()
        flash(f'Contenido "{titulo}" eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar contenido: {str(e)}', 'danger')
    
    return redirect(url_for('admin.educational_content'))