from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Material, Transaction, UserReward
from forms import StaffRecycleForm
from utils import actualizar_progreso_mision
import json

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

def staff_required(f):
    """Permite acceso a Funcionarios y Admins"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_staff:
            flash('⛔ Acceso denegado: Se requieren permisos de Funcionario.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@staff_bp.route('/')
@login_required
@staff_required
def dashboard():
    return render_template('staff/dashboard.html')

# CU-04: Registrar Entrega
@staff_bp.route('/entregas', methods=['GET', 'POST'])
@login_required
@staff_required
def registrar_entrega():
    form = StaffRecycleForm()
    # Cargar materiales activos
    form.material_id.choices = [(m.id, f"{m.nombre} ({m.puntos_valor} pts)") for m in Material.query.filter_by(activo=True).all()]

    if form.validate_on_submit():
        identificador = form.identificador.data.strip()
        # Buscar por username o email
        estudiante = User.query.filter((User.username == identificador) | (User.email == identificador)).first()

        if not estudiante:
            flash(f'❌ No se encontró al usuario "{identificador}".', 'danger')
        else:
            material = Material.query.get(form.material_id.data)
            cantidad = form.cantidad.data
            puntos_ganados = material.puntos_valor * cantidad
            
            # 1. Asignar puntos
            estudiante.agregar_puntos(
                puntos_ganados,
                'reciclaje',
                f"Entrega en centro de acopio (Atendido por: {current_user.username})"
            )
            
            # 2. Guardar metadata técnica en la transacción
            ultima_trans = Transaction.query.filter_by(user_id=estudiante.id).order_by(Transaction.id.desc()).first()
            if ultima_trans:
                ultima_trans.metadata_json = json.dumps({
                    'material_id': material.id,
                    'cantidad': cantidad,
                    'staff_id': current_user.id
                })
            
            # 3. Actualizar misiones del estudiante
            actualizar_progreso_mision(estudiante, 'reciclaje', cantidad)
            
            db.session.commit()
            flash(f'✅ Entrega registrada: {cantidad} {material.nombre} para {estudiante.nombre_completo} (+{puntos_ganados} pts).', 'success')
            return redirect(url_for('staff.registrar_entrega'))

    return render_template('staff/recycling.html', form=form)

# CU-15: Validar Cupón
@staff_bp.route('/canjes', methods=['GET', 'POST'])
@login_required
@staff_required
def validar_canjes():
    search_query = request.args.get('q', '').strip()
    cupones = []
    
    if search_query:
        # Buscar coincidencias parciales en código o usuario
        cupones = UserReward.query.join(User).filter(
            (UserReward.codigo.ilike(f'%{search_query}%')) |
            (User.username.ilike(f'%{search_query}%'))
        ).order_by(UserReward.fecha_canje.desc()).all()
    
    return render_template('staff/coupons.html', cupones=cupones, search_query=search_query)

@staff_bp.route('/canjes/entregar/<int:id>', methods=['POST'])
@login_required
@staff_required
def marcar_entregado(id):
    canje = UserReward.query.get_or_404(id)
    
    if canje.estado == 'entregado':
        flash('⚠️ Este premio ya fue entregado anteriormente.', 'warning')
    else:
        canje.estado = 'entregado'
        db.session.commit()
        flash(f'✅ Premio entregado exitosamente a {canje.usuario.nombre_completo}.', 'success')
        
    return redirect(url_for('staff.validar_canjes', q=canje.codigo))