from flask import Blueprint, jsonify, url_for, request
from flask_login import current_user, login_required
from models import Achievement, UserAchievement

share_bp = Blueprint('share', __name__, url_prefix='/share')

@share_bp.route('/achievement/<int:achievement_id>', methods=['POST'])
@login_required
def share_achievement(achievement_id):
    # Verificar que el usuario ha desbloqueado el logro
    user_achievement = UserAchievement.query.filter_by(
        user_id=current_user.id,
        achievement_id=achievement_id
    ).first()

    if not user_achievement:
        return jsonify({'error': 'Logro no encontrado o no desbloqueado.'}), 404

    achievement = Achievement.query.get(achievement_id)
    if not achievement:
        return jsonify({'error': 'Logro no encontrado.'}), 404

    share_text = f"¡He desbloqueado el logro '{achievement.nombre}' en UCA Puntos Verdes! {achievement.descripcion}"
    share_url = url_for('main.profile', _external=True)

    twitter_url = f"https://twitter.com/intent/tweet?text={share_text}&url={share_url}"
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={share_url}"
    whatsapp_url = f"https://api.whatsapp.com/send?text={share_text} {share_url}"

    return jsonify({
        'twitter': twitter_url,
        'facebook': facebook_url,
        'whatsapp': whatsapp_url
    })
