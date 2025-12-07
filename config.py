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
    
 
    ITEMS_PER_PAGE = 25
    LANGUAGES = ['es', 'en']


    
    UCA_DEPARTAMENTOS = {
        'Ciencias y Tecnología': [
            ('ing_informatica', 'Ingeniería Informática'),
            ('ing_civil', 'Ingeniería Civil'),
            ('ing_industrial', 'Ingeniería Industrial'),
            ('ing_electronica', 'Ingeniería Electrónica'),
            ('arq', 'Arquitectura'),
            ('analisis', 'Análisis de Sistemas'),
            ('diseno_ind', 'Industrial'),
            ('diseno', 'Diseño Gráfico')
        ],
        'Ciencias Jurídicas y Diplomáticas': [
            ('derecho', 'Derecho'),
            ('notariado', 'Notariado'),
            ('rel_inter', 'Relaciones Internacionales')
        ],
        'Ciencias Contables y Administrativas': [
            ('admin', 'Administración de Empresas'),
            ('contabilidad', 'Contabilidad'),
            ('marketing', 'Marketing'),
            ('comercio', 'Comercio Internacional')
        ],
        'Ciencias de la Salud': [
            ('medicina', 'Medicina'),
            ('enfermeria', 'Enfermería'),
            ('nutricion', 'Nutrición'),
            ('odontologia', 'Odontología')
        ],
        'No Estudiante': [
            ('docentes', 'Docentes'),
            ('personal_adm', 'Personal Administrativo')
        ],
        'Filosofía y Ciencias Humanas': [
            ('psicologia', 'Psicología'),
            ('comunicacion', 'Ciencias de la Comunicación'),
            ('sociologia', 'Sociología'),
            ('teologia', 'Teología'),
            ('historia', 'Historia')
        ]
        
    }