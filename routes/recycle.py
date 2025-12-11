from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Material, Transaction, Quiz, QuizQuestion, UserQuiz
from forms import ReciclajeForm
import json
from utils import verificar_logros, actualizar_progreso_mision
from flask_babel import gettext as _

recycle_bp = Blueprint('recycle', __name__, url_prefix='/recycle')

@recycle_bp.route('/', methods=['GET'])
@login_required
def index():
    """Página principal de reciclaje"""
    # MODIFICADO: Se eliminó la lógica del formulario (POST) para que el usuario no pueda registrar.
    
    # Cargar materiales activos
    materiales = Material.query.filter_by(activo=True).all()
    
    # Historial reciente
    historial = Transaction.query.filter_by(user_id=current_user.id, tipo='reciclaje')\
        .order_by(Transaction.fecha.desc())\
        .limit(10)\
        .all()
    
    # Renderizamos sin el formulario
    return render_template('recycle/recycle.html', materiales=materiales, historial=historial)


@recycle_bp.route('/history')
@login_required
def history():
    """Historial completo de reciclaje"""
    page = request.args.get('page', 1, type=int)
    
    transacciones = Transaction.query.filter_by(user_id=current_user.id, tipo='reciclaje')\
        .order_by(Transaction.fecha.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('recycle/history.html', transacciones=transacciones)


@recycle_bp.route('/tasks')
@login_required
def tasks():
    """Tareas y actividades para ganar puntos"""
    quizzes = Quiz.query.filter_by(activo=True).all()
    quizzes_completados = [uq.quiz_id for uq in UserQuiz.query.filter_by(user_id=current_user.id).all()]
    
    return render_template('tasks/tasks.html', quizzes=quizzes, completados=quizzes_completados)


@recycle_bp.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def quiz(quiz_id):
    """Realizar un quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)
    
    ya_completado = UserQuiz.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
    if ya_completado:
        flash('Ya has completado este quiz.', 'warning')
        return redirect(url_for('recycle.tasks'))
    
    preguntas = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()
    
    if request.method == 'POST':
        respuestas_usuario = []
        correctas = 0
        
        for i, pregunta in enumerate(preguntas):
            respuesta = request.form.get(f'pregunta_{pregunta.id}', type=int)
            respuestas_usuario.append(respuesta)
            
            if respuesta == pregunta.respuesta_correcta:
                correctas += 1
        
        puntos = quiz.puntos_recompensa if correctas == len(preguntas) else 0
        
        user_quiz = UserQuiz(
            user_id=current_user.id,
            quiz_id=quiz_id,
            respuestas=json.dumps(respuestas_usuario),
            puntos_obtenidos=puntos
        )
        db.session.add(user_quiz)
        
        if puntos > 0:
            current_user.agregar_puntos(puntos, 'quiz', f'Quiz completado: {quiz.titulo}')

            # Actualizar misiones de tipo 'quiz'
            misiones_completadas = actualizar_progreso_mision(current_user, 'quiz')
            for mision in misiones_completadas:
                 flash(_('¡Misión cumplida: %(nombre)s! Recompensa: %(puntos)s puntos.',
                            nombre=mision.nombre, puntos=mision.recompensa_puntos), 'success')

            # Verificar logros
            logros = verificar_logros(current_user)

            db.session.commit()
            
            flash(f'¡Perfecto! Has ganado {puntos} puntos. 🎓', 'success')
        else:
            db.session.commit()
            flash(f'Has obtenido {correctas}/{len(preguntas)} respuestas correctas. Intenta de nuevo más tarde.', 'warning')
        
        return redirect(url_for('recycle.tasks'))
    
    for pregunta in preguntas:
        pregunta.opciones_lista = json.loads(pregunta.opciones)
    
    return render_template('tasks/quiz.html', quiz=quiz, preguntas=preguntas)


@recycle_bp.route('/eventos')
@login_required
def eventos():
    """Eventos y voluntariados"""
    return render_template('tasks/events.html')


@recycle_bp.route('/evento/registrar/<tipo>')
@login_required
def registrar_evento(tipo):
    """Registrar participación en evento"""
    eventos_puntos = {
        'limpieza_playa': (80, 'Limpieza de playa'),
        'reforestacion': (100, 'Reforestación'),
        'taller_ambiental': (50, 'Taller ambiental'),
        'charla_sostenibilidad': (30, 'Charla de sostenibilidad')
    }
    
    if tipo in eventos_puntos:
        puntos, nombre = eventos_puntos[tipo]
        current_user.agregar_puntos(puntos, 'evento', f'Participación en: {nombre}')

        # Actualizar misiones de tipo 'evento'
        misiones_completadas = actualizar_progreso_mision(current_user, 'evento')
        for mision in misiones_completadas:
             flash(_('¡Misión cumplida: %(nombre)s! Recompensa: %(puntos)s puntos.',
                        nombre=mision.nombre, puntos=mision.recompensa_puntos), 'success')

        db.session.commit()
        
        flash(f'¡Gracias por participar en {nombre}! Has ganado {puntos} puntos. 🌍', 'success')
    else:
        flash('Evento no válido.', 'danger')
    
    return redirect(url_for('recycle.eventos'))