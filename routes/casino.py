from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, CasinoGame
from config import Config
from utils import jugar_ruleta, jugar_slots, jugar_dados
import json

casino_bp = Blueprint('casino', __name__, url_prefix='/casino')

@casino_bp.route('/')
@login_required
def index():
    """Página principal del casino"""
    # Estadísticas del usuario
    juegos = CasinoGame.query.filter_by(user_id=current_user.id)\
        .order_by(CasinoGame.fecha.desc())\
        .limit(10)\
        .all()
    
    total_apostado = db.session.query(db.func.sum(CasinoGame.apuesta))\
        .filter_by(user_id=current_user.id).scalar() or 0
    
    total_ganado = db.session.query(db.func.sum(CasinoGame.ganancia))\
        .filter_by(user_id=current_user.id).scalar() or 0
    
    return render_template('casino/casino.html',
                         juegos=juegos,
                         total_apostado=total_apostado,
                         total_ganado=total_ganado)


@casino_bp.route('/ruleta')
@login_required
def ruleta():
    """Juego de ruleta"""
    return render_template('casino/ruleta.html')


@casino_bp.route('/ruleta/jugar', methods=['POST'])
@login_required
def jugar_ruleta_post():
    """Procesar apuesta de ruleta"""
    data = request.get_json()
    
    apuesta = data.get('apuesta', 0)
    tipo_apuesta = data.get('tipo', 'numero')
    valor = data.get('valor')
    
    # Validaciones
    if apuesta < Config.CASINO_MIN_BET:
        return jsonify({'error': f'La apuesta mínima es {Config.CASINO_MIN_BET} puntos'}), 400
    
    max_apuesta = int(current_user.puntos_totales * Config.CASINO_MAX_BET_PERCENT)
    if apuesta > max_apuesta:
        return jsonify({'error': f'Solo puedes apostar hasta {max_apuesta} puntos (30% de tu saldo)'}), 400
    
    if apuesta > current_user.puntos_totales:
        return jsonify({'error': 'No tienes suficientes puntos'}), 400
    
    # Jugar
    resultado = jugar_ruleta(numero_apostado=valor, tipo_apuesta=tipo_apuesta)
    
    ganancia = 0
    if resultado['gano']:
        ganancia = apuesta * resultado['multiplicador']
    
    ganancia_neta = ganancia - apuesta
    
    # Actualizar puntos
    current_user.puntos_totales += ganancia_neta
    
    # Registrar juego
    juego = CasinoGame(
        user_id=current_user.id,
        tipo_juego='ruleta',
        apuesta=apuesta,
        resultado=str(resultado['numero']),
        ganancia=ganancia_neta,
        detalles=json.dumps(resultado)
    )
    
    db.session.add(juego)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'resultado': resultado,
        'ganancia': ganancia,
        'ganancia_neta': ganancia_neta,
        'puntos_actuales': current_user.puntos_totales
    })


@casino_bp.route('/slots')
@login_required
def slots():
    """Juego de slots"""
    return render_template('casino/slots.html')


@casino_bp.route('/slots/jugar', methods=['POST'])
@login_required
def jugar_slots_post():
    """Procesar apuesta de slots"""
    data = request.get_json()
    apuesta = data.get('apuesta', 0)
    
    # Validaciones
    if apuesta < Config.CASINO_MIN_BET:
        return jsonify({'error': f'La apuesta mínima es {Config.CASINO_MIN_BET} puntos'}), 400
    
    max_apuesta = int(current_user.puntos_totales * Config.CASINO_MAX_BET_PERCENT)
    if apuesta > max_apuesta:
        return jsonify({'error': f'Solo puedes apostar hasta {max_apuesta} puntos (30% de tu saldo)'}), 400
    
    if apuesta > current_user.puntos_totales:
        return jsonify({'error': 'No tienes suficientes puntos'}), 400
    
    # Jugar
    resultado = jugar_slots()
    
    ganancia = 0
    if resultado['gano']:
        ganancia = apuesta * resultado['multiplicador']
    
    ganancia_neta = ganancia - apuesta
    
    # Actualizar puntos
    current_user.puntos_totales += ganancia_neta
    
    # Registrar juego
    juego = CasinoGame(
        user_id=current_user.id,
        tipo_juego='slots',
        apuesta=apuesta,
        resultado=''.join(resultado['rodillos']),
        ganancia=ganancia_neta,
        detalles=json.dumps(resultado)
    )
    
    db.session.add(juego)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'resultado': resultado,
        'ganancia': ganancia,
        'ganancia_neta': ganancia_neta,
        'puntos_actuales': current_user.puntos_totales
    })


@casino_bp.route('/dados')
@login_required
def dados():
    """Juego de dados"""
    return render_template('casino/dados.html')


@casino_bp.route('/dados/jugar', methods=['POST'])
@login_required
def jugar_dados_post():
    """Procesar apuesta de dados"""
    data = request.get_json()
    
    apuesta = data.get('apuesta', 0)
    tipo_apuesta = data.get('tipo', 'suma')
    valor = data.get('valor', 7)
    
    # Validaciones
    if apuesta < Config.CASINO_MIN_BET:
        return jsonify({'error': f'La apuesta mínima es {Config.CASINO_MIN_BET} puntos'}), 400
    
    max_apuesta = int(current_user.puntos_totales * Config.CASINO_MAX_BET_PERCENT)
    if apuesta > max_apuesta:
        return jsonify({'error': f'Solo puedes apostar hasta {max_apuesta} puntos (30% de tu saldo)'}), 400
    
    if apuesta > current_user.puntos_totales:
        return jsonify({'error': 'No tienes suficientes puntos'}), 400
    
    # Jugar
    resultado = jugar_dados(tipo_apuesta=tipo_apuesta, valor_apostado=valor)
    
    ganancia = 0
    if resultado['gano']:
        ganancia = apuesta * resultado['multiplicador']
    
    ganancia_neta = ganancia - apuesta
    
    # Actualizar puntos
    current_user.puntos_totales += ganancia_neta
    
    # Registrar juego
    juego = CasinoGame(
        user_id=current_user.id,
        tipo_juego='dados',
        apuesta=apuesta,
        resultado=f"{resultado['dado1']}+{resultado['dado2']}={resultado['suma']}",
        ganancia=ganancia_neta,
        detalles=json.dumps(resultado)
    )
    
    db.session.add(juego)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'resultado': resultado,
        'ganancia': ganancia,
        'ganancia_neta': ganancia_neta,
        'puntos_actuales': current_user.puntos_totales
    })