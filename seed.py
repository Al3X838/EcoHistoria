"""
Script para poblar la base de datos con 6 usuarios y datos de prueba.
"""
from app import create_app
from models import db, User, Material, Reward, Achievement, Quiz, QuizQuestion, Mision, Transaction, UserAchievement, UserMision
import json
from datetime import datetime, timedelta
import random

def seed_database():
    app = create_app()
    
    with app.app_context():
        print("🌱 Iniciando seed de la base de datos...")
        
        # Limpiar base de datos previa (Opcional, para empezar limpio)
        db.drop_all()
        db.create_all()
        print("🧹 Base de datos limpiada y recreada.")

        # ==========================================
        # 1. CREACIÓN DE USUARIOS (6 Total)
        # ==========================================
        print("👥 Creando usuarios...")
        
        # 1. Administrador
        admin = User(
            username='admin',
            email='admin@uca.edu.sv',
            nombre_completo='Super Admin',
            facultad='Rectoría',
            carrera='Administración',
            role='admin',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)

        # 2. Funcionario Autorizado (Staff)
        staff = User(
            username='funcionario',
            email='staff@uca.edu.sv',
            nombre_completo='Roberto Funcionario',
            facultad='Administración',
            carrera='Logística',
            role='funcionario',
            is_admin=False
        )
        staff.set_password('staff123')
        db.session.add(staff)

        # 3. Estudiante 1 (El Reciclador Top)
        estudiante1 = User(
            username='ana.garcia',
            email='ana@uca.edu.sv',
            nombre_completo='Ana García',
            facultad='Ingeniería',
            carrera='Ingeniería Industrial',
            role='estudiante',
            puntos_totales=1250,
            nivel='Líder Sostenible',
            racha_actual=15
        )
        estudiante1.set_password('test1234')
        db.session.add(estudiante1)

        # 4. Estudiante 2 (El Nuevo)
        estudiante2 = User(
            username='carlos.perez',
            email='carlos@uca.edu.sv',
            nombre_completo='Carlos Pérez',
            facultad='Ciencias Jurídicas y Diplomáticas',
            carrera='Derecho',
            role='estudiante',
            puntos_totales=50,
            nivel='Semilla Verde',
            racha_actual=2
        )
        estudiante2.set_password('test1234')
        db.session.add(estudiante2)

        # 5. Estudiante 3 (El Jugador de Casino)
        estudiante3 = User(
            username='luis.martinez',
            email='luis@uca.edu.sv',
            nombre_completo='Luis Martínez',
            facultad='Ciencias Empresariales',
            carrera='Marketing',
            role='estudiante',
            puntos_totales=800,
            nivel='Guardián Ambiental',
            racha_actual=5
        )
        estudiante3.set_password('test1234')
        db.session.add(estudiante3)

        # 6. Estudiante 4 (La Intelectual de los Quizzes)
        estudiante4 = User(
            username='sofia.rodriguez',
            email='sofia@uca.edu.sv',
            nombre_completo='Sofía Rodríguez',
            facultad='Ciencias y Tecnología',
            carrera='Ingeniería Informática',
            role='estudiante',
            puntos_totales=450,
            nivel='Alumno Verde',
            racha_actual=8
        )
        estudiante4.set_password('test1234')
        db.session.add(estudiante4)

        db.session.commit() # Guardar usuarios para tener sus IDs

        # ==========================================
        # 2. CATÁLOGOS (Materiales, Premios, etc.)
        # ==========================================
        print("📦 Creando catálogos...")

        # Materiales
        materiales = [
            Material(nombre='Botella Plástico (PET)', categoria='Plástico', puntos_valor=10, unidad_medida='unidad', impacto_co2=0.08, impacto_agua=0.5),
            Material(nombre='Lata de Aluminio', categoria='Metal', puntos_valor=15, unidad_medida='unidad', impacto_co2=0.17, impacto_agua=0.2),
            Material(nombre='Papel Bond', categoria='Papel', puntos_valor=5, unidad_medida='hoja', impacto_co2=0.01, impacto_agua=0.1),
            Material(nombre='Cartón', categoria='Papel', puntos_valor=8, unidad_medida='kg', impacto_co2=0.05, impacto_agua=0.3),
            Material(nombre='Botella de Vidrio', categoria='Vidrio', puntos_valor=12, unidad_medida='unidad', impacto_co2=0.15, impacto_agua=0.4)
        ]
        db.session.add_all(materiales)

        # Recompensas
        recompensas = [
            Reward(nombre='Vale Cafetería $1', descripcion='Válido en cualquier cafetería UCA.', categoria='Comida', puntos_costo=200, stock_disponible=50),
            Reward(nombre='Camiseta UCA Verde', descripcion='100% Algodón orgánico.', categoria='Merchandising', puntos_costo=1500, stock_disponible=10),
            Reward(nombre='Entrada al Cine', descripcion='Cinepolis Multiplaza.', categoria='Entretenimiento', puntos_costo=800, stock_disponible=20),
            Reward(nombre='Termo Ecológico', descripcion='Mantiene bebidas frías/calientes.', categoria='Merchandising', puntos_costo=1200, stock_disponible=15)
        ]
        db.session.add_all(recompensas)

        # Logros
        logros = [
            Achievement(nombre='Primer Paso', descripcion='Realiza tu primer reciclaje.', icono='🌱', criterio='reciclaje_1', puntos_requeridos=1, categoria='Reciclaje'),
            Achievement(nombre='Reciclador Pro', descripcion='Alcanza 100 reciclajes.', icono='♻️', criterio='reciclaje_100', puntos_requeridos=100, categoria='Reciclaje'),
            Achievement(nombre='Racha de Fuego', descripcion='Mantén una racha de 7 días.', icono='🔥', criterio='racha_7', puntos_requeridos=7, categoria='Constancia')
        ]
        db.session.add_all(logros)

        # Misiones
        misiones = [
            Mision(nombre='Reciclaje Diario', descripcion='Recicla 5 botellas hoy.', tipo='reciclaje', objetivo=5, recompensa_puntos=20, frecuencia='diaria'),
            Mision(nombre='Login Semanal', descripcion='Entra 5 días seguidos.', tipo='login', objetivo=5, recompensa_puntos=50, frecuencia='semanal')
        ]
        db.session.add_all(misiones)

        db.session.commit()

        # ==========================================
        # 3. DATOS DE PRUEBA (Transacciones)
        # ==========================================
        print("📊 Generando historial de prueba...")

        # Simular historial para Ana (Estudiante 1)
        material_pet = Material.query.filter_by(nombre='Botella Plástico (PET)').first()
        
        # Transacción de reciclaje
        t1 = Transaction(
            user_id=estudiante1.id,
            tipo='reciclaje',
            puntos=100,
            descripcion='Reciclaje de 10 Botellas',
            fecha=datetime.now() - timedelta(days=2),
            metadata_json=json.dumps({'material_id': material_pet.id, 'cantidad': 10})
        )
        db.session.add(t1)

        # Logro desbloqueado
        logro_primer = Achievement.query.filter_by(criterio='reciclaje_1').first()
        ua1 = UserAchievement(user_id=estudiante1.id, achievement_id=logro_primer.id, progreso=100)
        db.session.add(ua1)

        # Misión activa para Carlos (Estudiante 2)
        mision_diaria = Mision.query.filter_by(frecuencia='diaria').first()
        um1 = UserMision(user_id=estudiante2.id, mision_id=mision_diaria.id, progreso=2)
        db.session.add(um1)

        db.session.commit()
        print("✅ ¡Seed completado con éxito! 6 Usuarios listos.")
        print("   - Admin: admin / admin123")
        print("   - Staff: funcionario / staff123")
        print("   - Estudiantes: ana.garcia, carlos.perez, etc. (Pass: test1234)")

if __name__ == '__main__':
    seed_database()