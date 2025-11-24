from flask import Flask, render_template, request, session
from flask_babel import Babel
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
from models import db, User
from utils import inject_csrf_token
import os
import traceback

babel = Babel()

def create_app(config_class=Config):
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configuración de Babel
    app.config['LANGUAGES'] = ['es', 'en']
    
    def get_locale():
        if 'language' in session:
            return session.get('language')
        return request.accept_languages.best_match(app.config['LANGUAGES'])

    # Inicializar extensiones
    babel.init_app(app, locale_selector=get_locale)
    db.init_app(app)
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registrar blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.recycle import recycle_bp
    from routes.rewards import rewards_bp
    from routes.casino import casino_bp
    from routes.admin import admin_bp
    from routes.share import share_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(recycle_bp)
    app.register_blueprint(rewards_bp)
    app.register_blueprint(casino_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(share_bp)
    
    # Registrar procesador de contexto
    app.context_processor(inject_csrf_token)
    
    @app.context_processor
    def inject_get_locale():
        return dict(get_locale=get_locale)

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
    
    # Página de error 404
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    # Página de error 500
    @app.errorhandler(500)
    def internal_error(error):
        traceback.print_exc() # Imprimir el stack trace en la consola
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
