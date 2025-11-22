from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Reward, UserReward, Transaction

rewards_bp = Blueprint('rewards', __name__, url_prefix='/rewards')

@rewards_bp.route('/')
@login_required
def index():
    """Catálogo de recompensas"""
    categoria = request.args.get('categoria', 'todas')
    
    query = Reward.query.filter_by(activo=True)
    
    if categoria != 'todas':
        query = query.filter_by(categoria=categoria)
    
    recompensas = query.all()
    
    categorias = db.session.query(Reward.categoria).distinct().all()
    categorias = [c[0] for c in categorias if c[0]]
    
    return render_template('rewards/rewards.html', 
                         recompensas=recompensas, 
                         categorias=categorias,
                         categoria_actual=categoria)


@rewards_bp.route('/canjear/<int:reward_id>', methods=['POST'])
@login_required
def canjear(reward_id):
    """Canjear una recompensa"""
    recompensa = Reward.query.get_or_404(reward_id)
    
    # Verificar si tiene suficientes puntos
    if current_user.puntos_totales < recompensa.puntos_costo:
        flash('No tienes suficientes puntos para canjear esta recompensa.', 'danger')
        return redirect(url_for('rewards.index'))
    
    # Verificar stock
    if recompensa.stock_disponible <= 0:
        flash('Esta recompensa no tiene stock disponible.', 'warning')
        return redirect(url_for('rewards.index'))
    
    # Restar puntos
    if current_user.restar_puntos(recompensa.puntos_costo, 'canje', f'Canje: {recompensa.nombre}'):
        # Crear registro de canje
        user_reward = UserReward(
            user_id=current_user.id,
            reward_id=recompensa.id,
            estado='pendiente'
        )
        
        # Reducir stock
        recompensa.stock_disponible -= 1
        
        db.session.add(user_reward)
        db.session.commit()
        
        flash(f'¡Felicitaciones! Has canjeado: {recompensa.nombre}. Recógela en el punto verde UCA. 🎁', 'success')
    else:
        flash('Error al procesar el canje.', 'danger')
    
    return redirect(url_for('rewards.index'))


@rewards_bp.route('/mis-recompensas')
@login_required
def mis_recompensas():
    """Recompensas canjeadas por el usuario"""
    canjes = UserReward.query.filter_by(user_id=current_user.id)\
        .order_by(UserReward.fecha_canje.desc())\
        .all()
    
    return render_template('rewards/my_rewards.html', canjes=canjes)