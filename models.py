from datetime import datetime, timezone
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer

db = SQLAlchemy()

def get_current_time():
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    """Modelo de Usuario"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(150), nullable=False)
    facultad = db.Column(db.String(100))
    carrera = db.Column(db.String(100))
    role = db.Column(db.String(20), default='estudiante') # Opciones: 'estudiante', 'funcionario', 'admin'
    puntos_totales = db.Column(db.Integer, default=0)
    puntos_historicos = db.Column(db.Integer, default=0)
    nivel = db.Column(db.String(50), default='Semilla Verde')
    racha_actual = db.Column(db.Integer, default=0)
    ultima_actividad = db.Column(db.DateTime, default=get_current_time)
    fecha_registro = db.Column(db.DateTime, default=get_current_time)
    is_admin = db.Column(db.Boolean, default=False)
    activo = db.Column(db.Boolean, default=True)


    
    # Relaciones
    transacciones = db.relationship('Transaction', backref='usuario', lazy='dynamic')
    recompensas = db.relationship('UserReward', backref='usuario', lazy='dynamic')
    logros = db.relationship('UserAchievement', backref='usuario', lazy='dynamic')
    juegos_casino = db.relationship('CasinoGame', backref='jugador', lazy='dynamic')
    quizzes_completados = db.relationship('UserQuiz', backref='estudiante', lazy='dynamic')
    misiones = db.relationship('UserMision', backref='usuario', lazy='dynamic')

    @property
    def is_staff(self):
        """Permite acceso a funcionarios y admins"""
        return self.role in ['funcionario', 'admin']
    
    @property
    def is_admin_property(self):
        return self.role == 'admin' or self.is_admin
    
    @property
    def is_active(self):
        return self.activo
    
    def set_password(self, password):
        """Hashear contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar contraseña"""
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_sec)
            user_id = data.get('user_id')
        except:
            return None
        return User.query.get(user_id)
    
    def actualizar_nivel(self):
        """Actualizar nivel según puntos"""
        from config import Config
        for nivel, puntos_min in sorted(Config.NIVELES.items(), key=lambda x: x[1], reverse=True):
            if self.puntos_totales >= puntos_min:
                self.nivel = nivel
                break
    
    def actualizar_racha(self):
        """Actualizar racha de días consecutivos"""
        hoy = get_current_time().date()
        ultima = self.ultima_actividad.date() if self.ultima_actividad else None
        
        if ultima:
            diferencia = (hoy - ultima).days
            if diferencia == 0:
                # Misma fecha, no hacer nada
                return
            elif diferencia == 1:
                # Día consecutivo
                self.racha_actual += 1
            else:
                # Se rompió la racha
                self.racha_actual = 1
        else:
            self.racha_actual = 1
        
        self.ultima_actividad = get_current_time()
    
    def agregar_puntos(self, cantidad, tipo, descripcion):
        """Agregar puntos y registrar transacción"""
        self.puntos_totales += cantidad
        self.actualizar_nivel()
        self.actualizar_racha()
        if cantidad > 0:
            self.puntos_historicos += cantidad
        transaccion = Transaction(
            user_id=self.id,
            tipo=tipo,
            puntos=cantidad,
            descripcion=descripcion
        )
        db.session.add(transaccion)
    
    def restar_puntos(self, cantidad, tipo, descripcion):
        """Restar puntos y registrar transacción"""
        if self.puntos_totales >= cantidad:
            self.puntos_totales -= cantidad
            transaccion = Transaction(
                user_id=self.id,
                tipo=tipo,
                puntos=-cantidad,
                descripcion=descripcion
            )
            db.session.add(transaccion)
            return True
        return False
    
    def __repr__(self):
        return f'<User {self.username}>'


class Material(db.Model):
    """Modelo de Material Reciclable"""
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50))
    puntos_valor = db.Column(db.Integer, nullable=False)
    unidad_medida = db.Column(db.String(20), default='unidad')
    impacto_co2 = db.Column(db.Float, default=0.0)  # kg de CO2
    impacto_agua = db.Column(db.Float, default=0.0)  # litros
    activo = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Material {self.nombre}>'


class Transaction(db.Model):
    """Modelo de Transacción"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # reciclaje, quiz, evento, canje, casino
    puntos = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, default=get_current_time)
    metadata_json = db.Column(db.Text)  # JSON para datos adicionales
    
    def __repr__(self):
        return f'<Transaction {self.tipo} - {self.puntos} pts>'


class Reward(db.Model):
    """Modelo de Recompensa"""
    __tablename__ = 'rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.String(50))
    puntos_costo = db.Column(db.Integer, nullable=False)
    stock_disponible = db.Column(db.Integer, default=0)
    imagen_url = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)
    
    # Relación
    canjes = db.relationship('UserReward', backref='recompensa', lazy='dynamic')
    
    def __repr__(self):
        return f'<Reward {self.nombre}>'


class UserReward(db.Model):
    """Modelo de Canje de Recompensa"""
    __tablename__ = 'user_rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey('rewards.id'), nullable=False)
    fecha_canje = db.Column(db.DateTime, default=get_current_time)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, entregado, cancelado
    codigo = db.Column(db.String(20), unique=True, nullable=True)
    def __repr__(self):
        return f'<UserReward user={self.user_id} reward={self.reward_id}>'


class Achievement(db.Model):
    """Modelo de Logro"""
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    icono = db.Column(db.String(10))  # Emoji
    criterio = db.Column(db.String(100))
    puntos_requeridos = db.Column(db.Integer, default=0)
    categoria = db.Column(db.String(50))
    
    # Relación
    usuarios_logro = db.relationship('UserAchievement', backref='logro', lazy='dynamic')
    
    def __repr__(self):
        return f'<Achievement {self.nombre}>'


class UserAchievement(db.Model):
    """Modelo de Logro de Usuario"""
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    fecha_obtencion = db.Column(db.DateTime, default=get_current_time)
    progreso = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<UserAchievement user={self.user_id} achievement={self.achievement_id}>'


class CasinoGame(db.Model):
    """Modelo de Juego de Casino"""
    __tablename__ = 'casino_games'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tipo_juego = db.Column(db.String(20), nullable=False)  # ruleta, slots, dados
    apuesta = db.Column(db.Integer, nullable=False)
    resultado = db.Column(db.String(50))
    ganancia = db.Column(db.Integer, default=0)
    detalles = db.Column(db.Text)  # JSON
    fecha = db.Column(db.DateTime, default=get_current_time)
    
    def __repr__(self):
        return f'<CasinoGame {self.tipo_juego} - {self.ganancia} pts>'


class Quiz(db.Model):
    """Modelo de Quiz"""
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(50))
    puntos_recompensa = db.Column(db.Integer, default=15)
    activo = db.Column(db.Boolean, default=True)
    
    # Relación
    preguntas = db.relationship('QuizQuestion', backref='quiz', lazy='dynamic')
    completados = db.relationship('UserQuiz', backref='quiz', lazy='dynamic')
    
    def __repr__(self):
        return f'<Quiz {self.titulo}>'


class QuizQuestion(db.Model):
    """Modelo de Pregunta de Quiz"""
    __tablename__ = 'quiz_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    pregunta = db.Column(db.Text, nullable=False)
    opciones = db.Column(db.Text, nullable=False)  # JSON: ["opción1", "opción2", ...]
    respuesta_correcta = db.Column(db.Integer, nullable=False)  # índice de la respuesta
    explicacion = db.Column(db.Text)
    
    def __repr__(self):
        return f'<QuizQuestion quiz={self.quiz_id}>'


class UserQuiz(db.Model):
    """Modelo de Quiz Completado por Usuario"""
    __tablename__ = 'user_quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    respuestas = db.Column(db.Text)  # JSON
    puntos_obtenidos = db.Column(db.Integer, default=0)
    fecha_completado = db.Column(db.DateTime, default=get_current_time)
    
    def __repr__(self):
        return f'<UserQuiz user={self.user_id} quiz={self.quiz_id}>'


class Mision(db.Model):
    """Modelo de Misión"""
    __tablename__ = 'misiones'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    tipo = db.Column(db.String(50), nullable=False) # ej: reciclaje, quiz, login
    objetivo = db.Column(db.Integer, default=1)
    recompensa_puntos = db.Column(db.Integer, nullable=False)
    frecuencia = db.Column(db.String(20), nullable=False) # diaria, semanal
    activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Mision {self.nombre}>'


class UserMision(db.Model):
    """Modelo de Progreso de Misión de Usuario"""
    __tablename__ = 'user_misiones'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mision_id = db.Column(db.Integer, db.ForeignKey('misiones.id'), nullable=False)
    progreso = db.Column(db.Integer, default=0)
    completada = db.Column(db.Boolean, default=False)
    fecha_asignacion = db.Column(db.DateTime, default=get_current_time)
    
    mision = db.relationship('Mision')

    def __repr__(self):
        return f'<UserMision user={self.user_id} mision={self.mision_id}>'


class EducationalContent(db.Model):
    """Modelo de Contenido Educativo"""
    __tablename__ = 'educational_content'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=get_current_time)
    activo = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<EducationalContent {self.titulo}>'

