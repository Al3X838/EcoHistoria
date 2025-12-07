import random
import json
from datetime import datetime, timedelta, date
from models import User, Transaction, Mision, UserMision, db, Material
from sqlalchemy import func, and_
from flask_wtf.csrf import generate_csrf
from config import Config

def inject_csrf_token():
    """Inyecta el token CSRF para usar en formularios Jinja2"""
    return dict(csrf_token=generate_csrf)

def calcular_impacto_ambiental(user_id):
    """Calcula el impacto ambiental total de un usuario"""
    # Importar Material internamente si es necesario, pero ya está en la cabecera
    
    transacciones = Transaction.query.filter_by(
        user_id=user_id,
        tipo='reciclaje'
    ).all()
    
    co2_total = 0
    agua_total = 0
    
    for trans in transacciones:
        # Parsear metadata para obtener material_id
        if trans.metadata_json:
            try:
                meta = json.loads(trans.metadata_json)
                material_id = meta.get('material_id')
                cantidad = meta.get('cantidad', 1)
                
                material = Material.query.get(material_id)
                if material:
                    co2_total += material.impacto_co2 * cantidad
                    agua_total += material.impacto_agua * cantidad
            except:
                pass
    
    # Calcular árboles equivalentes (1 árbol absorbe aprox 22kg CO2/año)
    arboles_equivalentes = round(co2_total / 22, 2)
    
    return {
        'co2_evitado': round(co2_total, 2),
        'agua_ahorrada': round(agua_total, 2),
        'arboles_salvados': arboles_equivalentes
    }


def obtener_ranking_estudiantes(limite=10):
    """Obtiene el ranking de estudiantes por puntos históricos"""
    # Esta función ya estaba correcta, ordenando por el campo historico
    return User.query.filter_by(is_admin=False)\
        .order_by(User.puntos_historicos.desc())\
        .limit(limite)\
        .all()


def obtener_ranking_facultades():
    """Obtiene el ranking de facultades por puntos históricos totales"""
    resultado = db.session.query(
        User.facultad,
        func.sum(User.puntos_historicos).label('puntos_historicos'),
        func.count(User.id).label('total_estudiantes')
    ).filter(
        User.is_admin == False,
        User.facultad != None # Ignorar usuarios sin facultad
    ).group_by(User.facultad)\
     .order_by(
         # CORRECCIÓN: Ordenar por el campo agregado (puntos_historicos)
         func.sum(User.puntos_historicos).desc()
     ).all()
    
    return [{'facultad': r[0], 'puntos': r[1], 'estudiantes': r[2]} for r in resultado]


def obtener_ranking_carreras():
    """Obtiene el ranking de carreras por puntos históricos totales"""
    resultado = db.session.query(
        User.carrera,
        User.facultad,
        func.sum(User.puntos_historicos).label('puntos_historicos'),
        func.count(User.id).label('total_estudiantes')
    ).filter(
        User.is_admin == False,
        User.carrera != None, # Ignorar usuarios sin carrera
        User.facultad != None
    ).group_by(User.carrera, User.facultad)\
     .order_by(
         # CORRECCIÓN: Ordenar por el campo agregado (puntos_historicos)
         func.sum(User.puntos_historicos).desc()
     ).limit(20)\
     .all()
    
    return [{'carrera': r[0], 'facultad': r[1], 'puntos': r[2], 'estudiantes': r[3]} for r in resultado]


def estadisticas_globales():
    """Obtiene estadísticas globales del sistema"""
    total_usuarios = User.query.filter_by(is_admin=False).count()
    # Usamos puntos_historicos para total_puntos global
    total_puntos = db.session.query(func.sum(User.puntos_historicos)).scalar() or 0
    total_transacciones = Transaction.query.count()
    
    # Calcular impacto total
    transacciones_reciclaje = Transaction.query.filter_by(tipo='reciclaje').all()
    
    co2_total = 0
    agua_total = 0
    
    for trans in transacciones_reciclaje:
        if trans.metadata_json:
            try:
                meta = json.loads(trans.metadata_json)
                material_id = meta.get('material_id')
                cantidad = meta.get('cantidad', 1)
                
                material = Material.query.get(material_id)
                if material:
                    co2_total += material.impacto_co2 * cantidad
                    agua_total += material.impacto_agua * cantidad
            except:
                pass
    
    return {
        'total_usuarios': total_usuarios,
        'total_puntos': total_puntos,
        'total_transacciones': total_transacciones,
        'co2_evitado': round(co2_total, 2),
        'agua_ahorrada': round(agua_total, 2),
        'arboles_salvados': round(co2_total / 22, 2)
    }


def obtener_nombre_carrera(codigo_carrera):
    """
    Traduce el código de carrera (ej: 'ing_inf') a su nombre real 
    (ej: 'Ingeniería Informática') buscando en Config.
    """
    if not codigo_carrera:
        return "Sin Carrera"
    for facultad, carreras in Config.UCA_DEPARTAMENTOS.items():
        for cod, nombre in carreras:
            if cod == codigo_carrera:
                return nombre
    return codigo_carrera.replace('_', ' ').title()


# --- Funciones de Misiones ---

def asignar_misiones(user):
    """Asigna misiones diarias y semanales a un usuario si no las tiene."""
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())

    # Verificar misiones diarias
    mision_diaria_existente = UserMision.query.filter(
        UserMision.user_id == user.id,
        UserMision.mision.has(frecuencia='diaria'),
        func.date(UserMision.fecha_asignacion) == today
    ).first()

    if not mision_diaria_existente:
        # Asignar una nueva misión diaria aleatoria
        misiones_diarias = Mision.query.filter_by(frecuencia='diaria', activo=True).all()
        if misiones_diarias:
            nueva_mision = random.choice(misiones_diarias)
            um = UserMision(user_id=user.id, mision_id=nueva_mision.id)
            db.session.add(um)

    # Verificar misiones semanales
    mision_semanal_existente = UserMision.query.filter(
        UserMision.user_id == user.id,
        UserMision.mision.has(frecuencia='semanal'),
        func.date(UserMision.fecha_asignacion) >= start_of_week
    ).first()

    if not mision_semanal_existente:
        # Asignar una nueva misión semanal aleatoria
        misiones_semanales = Mision.query.filter_by(frecuencia='semanal', activo=True).all()
        if misiones_semanales:
            nueva_mision = random.choice(misiones_semanales)
            um = UserMision(user_id=user.id, mision_id=nueva_mision.id)
            db.session.add(um)
    
    db.session.commit()


def actualizar_progreso_mision(user, tipo_accion, cantidad=1):
    """
    Actualiza el progreso de las misiones activas de un usuario.
    tipo_accion: 'reciclaje', 'quiz', 'login', etc.
    """
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())

    misiones_activas = UserMision.query.join(Mision).filter(
        UserMision.user_id == user.id,
        UserMision.completada == False,
        Mision.tipo == tipo_accion,
        # Filtrar para misiones de hoy o de esta semana
        ((Mision.frecuencia == 'diaria') & (func.date(UserMision.fecha_asignacion) == today)) |
        ((Mision.frecuencia == 'semanal') & (func.date(UserMision.fecha_asignacion) >= start_of_week))
    ).all()

    misiones_completadas = []
    for um in misiones_activas:
        um.progreso += cantidad
        if um.progreso >= um.mision.objetivo:
            um.completada = True
            user.agregar_puntos(
                cantidad=um.mision.recompensa_puntos,
                tipo='mision',
                descripcion=f"Recompensa por misión: {um.mision.nombre}"
            )
            misiones_completadas.append(um.mision)
    
    db.session.commit()
    return misiones_completadas


# --- Funciones de Casino (Legacy) ---

def jugar_ruleta(numero_apostado=None, tipo_apuesta='numero'):
    """
    Simula un juego de ruleta
    tipo_apuesta: 'numero', 'par', 'impar', 'alto', 'bajo', 'docena'
    """
    numero_ganador = random.randint(0, 36)
    
    resultado = {
        'numero': numero_ganador,
        'color': 'verde' if numero_ganador == 0 else ('rojo' if numero_ganador % 2 == 1 else 'negro'),
        'gano': False,
        'multiplicador': 0
    }
    
    if tipo_apuesta == 'numero' and numero_apostado == numero_ganador:
        resultado['gano'] = True
        resultado['multiplicador'] = 35
    elif tipo_apuesta == 'par' and numero_ganador != 0 and numero_ganador % 2 == 0:
        resultado['gano'] = True
        resultado['multiplicador'] = 2
    elif tipo_apuesta == 'impar' and numero_ganador != 0 and numero_ganador % 2 == 1:
        resultado['gano'] = True
        resultado['multiplicador'] = 2
    elif tipo_apuesta == 'alto' and numero_ganador >= 19:
        resultado['gano'] = True
        resultado['multiplicador'] = 2
    elif tipo_apuesta == 'bajo' and 1 <= numero_ganador <= 18:
        resultado['gano'] = True
        resultado['multiplicador'] = 2
    elif tipo_apuesta == 'docena':
        docena = (numero_ganador - 1) // 12 if numero_ganador > 0 else -1
        if docena == numero_apostado:
            resultado['gano'] = True
            resultado['multiplicador'] = 3
    
    return resultado


def jugar_slots():
    """Simula un juego de slots con 3 rodillos"""
    simbolos = ['🌱', '🌿', '🍃', '♻️', '🌍', '💚', '🌳', '🌲']
    
    rodillos = [
        random.choice(simbolos),
        random.choice(simbolos),
        random.choice(simbolos)
    ]
    
    resultado = {
        'rodillos': rodillos,
        'gano': False,
        'multiplicador': 0
    }
    
    # Jackpot: 3 símbolos de reciclaje
    if rodillos[0] == '♻️' and rodillos[1] == '♻️' and rodillos[2] == '♻️':
        resultado['gano'] = True
        resultado['multiplicador'] = 50
    # 3 iguales
    elif rodillos[0] == rodillos[1] == rodillos[2]:
        resultado['gano'] = True
        resultado['multiplicador'] = 10
    # 2 iguales
    elif rodillos[0] == rodillos[1] or rodillos[1] == rodillos[2] or rodillos[0] == rodillos[2]:
        resultado['gano'] = True
        resultado['multiplicador'] = 3
    
    return resultado


def jugar_dados(tipo_apuesta='suma', valor_apostado=7):
    """
    Simula un juego de dados
    tipo_apuesta: 'suma', 'par', 'impar', 'mayor7', 'menor7', 'dobles'
    """
    dado1 = random.randint(1, 6)
    dado2 = random.randint(1, 6)
    suma = dado1 + dado2
    
    resultado = {
        'dado1': dado1,
        'dado2': dado2,
        'suma': suma,
        'gano': False,
        'multiplicador': 0
    }
    
    if tipo_apuesta == 'suma' and suma == valor_apostado:
        resultado['gano'] = True
        # Multiplicadores según probabilidad
        multiplicadores_suma = {2: 30, 3: 15, 4: 10, 5: 8, 6: 6, 7: 5, 8: 6, 9: 8, 10: 10, 11: 15, 12: 30}
        resultado['multiplicador'] = multiplicadores_suma.get(suma, 5)
    elif tipo_apuesta == 'par' and suma % 2 == 0:
        resultado['gano'] = True
        resultado['multiplicador'] = 2
    elif tipo_apuesta == 'impar' and suma % 2 == 1:
        resultado['gano'] = True
        resultado['multiplicador'] = 2
    elif tipo_apuesta == 'mayor7' and suma > 7:
        resultado['gano'] = True
        resultado['multiplicador'] = 2
    elif tipo_apuesta == 'menor7' and suma < 7:
        resultado['gano'] = True
        resultado['multiplicador'] = 2
    elif tipo_apuesta == 'dobles' and dado1 == dado2:
        resultado['gano'] = True
        resultado['multiplicador'] = 8
    
    return resultado


def verificar_logros(user):
    """Verifica y otorga logros al usuario"""
    from models import Achievement, UserAchievement
    
    logros_obtenidos = []
    
    # Verificar cada logro
    logros = Achievement.query.all()
    for logro in logros:
        # Verificar si ya tiene el logro
        ya_tiene = UserAchievement.query.filter_by(
            user_id=user.id,
            achievement_id=logro.id
        ).first()
        
        if not ya_tiene:
            cumple = False
            
            # Verificar criterios
            # Verificar criterios
            if logro.criterio == 'reciclaje_1':
                total_reciclajes = Transaction.query.filter_by(
                    user_id=user.id,
                    tipo='reciclaje'
                ).count()
                cumple = total_reciclajes >= 1
            
            elif logro.criterio == 'racha_7':
                cumple = user.racha_actual >= 7
            
            elif logro.criterio == 'reciclaje_100':
                total = Transaction.query.filter_by(
                    user_id=user.id,
                    tipo='reciclaje'
                ).count()
                cumple = total >= 100

            elif logro.criterio == 'quiz_perfect_5':
                # Contar quizzes con puntaje perfecto (asumiendo que se guarda en metadata o historial)
                # Por ahora, simplificaremos verificando total de quizzes > 5 ya que no tenemos el puntaje exacto en Transaction fácilmente accesible sin parsear JSON
                # TODO: Mejorar esto parseando metadata_json de transacciones tipo 'quiz'
                total_quizzes = Transaction.query.filter_by(
                    user_id=user.id,
                    tipo='quiz'
                ).count()
                cumple = total_quizzes >= 5
            
            if cumple:
                nuevo_logro = UserAchievement(
                    user_id=user.id,
                    achievement_id=logro.id,
                    progreso=100
                )
                db.session.add(nuevo_logro)
                logros_obtenidos.append(logro)
    
    return logros_obtenidos