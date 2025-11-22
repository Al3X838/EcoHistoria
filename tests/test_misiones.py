import unittest
from app import create_app
from config import Config
from models import db, User, Mision, UserMision
from utils import asignar_misiones, actualizar_progreso_mision
from datetime import date

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class MisionesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Crear usuario de prueba
        self.user = User(username='testmision', email='testmision@test.com', nombre_completo='Test Mision')
        self.user.set_password('password')
        db.session.add(self.user)

        # Crear misiones de prueba
        self.mision_login_diaria = Mision(nombre='Login Diario', tipo='login', recompensa_puntos=5, frecuencia='diaria', objetivo=1, activo=True)
        self.mision_reciclaje_semanal = Mision(nombre='Reciclaje Semanal', tipo='reciclaje', recompensa_puntos=50, frecuencia='semanal', objetivo=10, activo=True)
        db.session.add(self.mision_login_diaria)
        db.session.add(self.mision_reciclaje_semanal)
        
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_asignar_misiones(self):
        # Asegurarse que el usuario no tiene misiones
        self.assertEqual(self.user.misiones.count(), 0)
        
        # Asignar misiones
        asignar_misiones(self.user)
        
        # Debería haber una misión diaria y una semanal
        self.assertEqual(self.user.misiones.count(), 2)
        
        # Verificar que no se asignan de nuevo
        asignar_misiones(self.user)
        self.assertEqual(self.user.misiones.count(), 2)

    def test_actualizar_progreso_mision(self):
        asignar_misiones(self.user)
        
        # Progresar en la misión de login
        actualizar_progreso_mision(self.user, 'login')
        mision_login = self.user.misiones.filter(UserMision.mision.has(tipo='login')).first()
        self.assertEqual(mision_login.progreso, 1)
        self.assertTrue(mision_login.completada)
        self.assertEqual(self.user.puntos_totales, 5) # Recompensa

        # Progresar en la misión de reciclaje sin completarla
        actualizar_progreso_mision(self.user, 'reciclaje', cantidad=5)
        mision_reciclaje = self.user.misiones.filter(UserMision.mision.has(tipo='reciclaje')).first()
        self.assertEqual(mision_reciclaje.progreso, 5)
        self.assertFalse(mision_reciclaje.completada)
        self.assertEqual(self.user.puntos_totales, 5) # Sin recompensa aún

        # Completar la misión de reciclaje
        actualizar_progreso_mision(self.user, 'reciclaje', cantidad=5)
        self.assertEqual(mision_reciclaje.progreso, 10)
        self.assertTrue(mision_reciclaje.completada)
        self.assertEqual(self.user.puntos_totales, 5 + 50) # Recompensa de misión semanal

if __name__ == '__main__':
    unittest.main()
