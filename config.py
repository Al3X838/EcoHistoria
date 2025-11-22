import os

class Config:
    """Configuración de la aplicación Flask"""
    
    # Clave secreta para sesiones y CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # basedir = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///uca_verde.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de casino
    CASINO_MIN_BET = 10
    CASINO_MAX_BET_PERCENT = 0.30  # 30% del saldo
    
    # Configuración de niveles
    NIVELES = {
        'Semilla Verde': 0,
        'Brote Ecológico': 101,
        'Alumno Verde': 301,
        'Guardián Ambiental': 601,
        'Líder Sostenible': 1001,
        'Eco Maestro': 1501
    }
    
    # Configuración de paginación
    ITEMS_PER_PAGE = 25
    
    # Idiomas soportados
    LANGUAGES = ['es', 'en']
