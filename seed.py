"""
Script para poblar la base de datos con datos iniciales
"""
from app import create_app
from models import db, User, Material, Reward, Achievement, Quiz, QuizQuestion, Mision
import json

def seed_database():
    app = create_app()
    
    with app.app_context():
        print("🌱 Iniciando seed de base de datos...")
        
        if User.query.first():
            print("⚠️  Usuarios ya existen. Saltando creación de usuarios.")
        else:
            print("👤 Creando usuario administrador...")
            admin = User(username='admin', email='admin@uca.edu.sv', nombre_completo='Administrador UCA Verde', facultad='Administración', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            
            print("👥 Creando usuarios de prueba...")
            # ... (código de usuarios existente) ...

        if Material.query.first():
             print("⚠️  Materiales ya existen. Saltando.")
        else:
            print("♻️  Creando materiales reciclables...")
            materiales = [
                {'nombre': 'Botella de Plástico (PET)', 'categoria': 'Plástico', 'puntos_valor': 10, 'unidad_medida': 'unidad', 'impacto_co2': 0.08, 'impacto_agua': 0.5},
                {'nombre': 'Lata de Aluminio', 'categoria': 'Metal', 'puntos_valor': 15, 'unidad_medida': 'unidad', 'impacto_co2': 0.17, 'impacto_agua': 0.2},
                {'nombre': 'Papel Bond', 'categoria': 'Papel', 'puntos_valor': 5, 'unidad_medida': 'hoja', 'impacto_co2': 0.01, 'impacto_agua': 0.1},
                {'nombre': 'Cartón', 'categoria': 'Papel', 'puntos_valor': 8, 'unidad_medida': 'kg', 'impacto_co2': 0.05, 'impacto_agua': 0.3},
                {'nombre': 'Botella de Vidrio', 'categoria': 'Vidrio', 'puntos_valor': 12, 'unidad_medida': 'unidad', 'impacto_co2': 0.15, 'impacto_agua': 0.4}
            ]
            
            for mat_data in materiales:
                material = Material(**mat_data)
                db.session.add(material)

        if Reward.query.first():
            print("⚠️  Recompensas ya existen. Saltando.")
        else:
            print("🎁 Creando recompensas...")
            recompensas = [
                {'nombre': 'Vale de Cafetería $1', 'descripcion': 'Canjeable en cualquier cafetería del campus.', 'categoria': 'Alimentación', 'puntos_costo': 200, 'stock_disponible': 50, 'imagen_url': 'cafe_voucher.png'},
                {'nombre': 'Vale de Librería $5', 'descripcion': 'Descuento en libros y papelería.', 'categoria': 'Educación', 'puntos_costo': 800, 'stock_disponible': 20, 'imagen_url': 'book_voucher.png'},
                {'nombre': 'Botella Eco UCA', 'descripcion': 'Botella reutilizable con logo de la UCA.', 'categoria': 'Merch', 'puntos_costo': 1500, 'stock_disponible': 15, 'imagen_url': 'eco_bottle.png'},
                {'nombre': 'Camiseta UCA Verde', 'descripcion': 'Camiseta de algodón orgánico.', 'categoria': 'Merch', 'puntos_costo': 2000, 'stock_disponible': 10, 'imagen_url': 'tshirt.png'},
                {'nombre': 'Plantación de Árbol', 'descripcion': 'Plantamos un árbol en tu nombre.', 'categoria': 'Ecología', 'puntos_costo': 500, 'stock_disponible': 100, 'imagen_url': 'tree.png'}
            ]
            
            for reward_data in recompensas:
                reward = Reward(**reward_data)
                db.session.add(reward)

        if Achievement.query.first():
            print("⚠️  Logros ya existen. Saltando.")
        else:
            print("🏆 Creando logros...")
            logros = [
                {'nombre': 'Primer Reciclaje', 'descripcion': 'Recicla tu primer objeto.', 'icono': '🌱', 'criterio': 'reciclaje_1', 'puntos_requeridos': 1, 'categoria': 'Reciclaje'},
                {'nombre': 'Reciclador Comprometido', 'descripcion': 'Alcanza 100 objetos reciclados.', 'icono': '♻️', 'criterio': 'reciclaje_100', 'puntos_requeridos': 100, 'categoria': 'Reciclaje'},
                {'nombre': 'Maestro del Conocimiento', 'descripcion': 'Completa 5 quizzes con puntaje perfecto.', 'icono': '🧠', 'criterio': 'quiz_perfect_5', 'puntos_requeridos': 5, 'categoria': 'Educación'},
                {'nombre': 'Racha Semanal', 'descripcion': 'Mantén una racha de 7 días.', 'icono': '🔥', 'criterio': 'racha_7', 'puntos_requeridos': 7, 'categoria': 'Constancia'}
            ]
            
            for logro_data in logros:
                logro = Achievement(**logro_data)
                db.session.add(logro)

        if Quiz.query.first():
            print("⚠️  Quizzes ya existen. Saltando.")
        else:
            print("📚 Creando quizzes...")
            quiz1 = Quiz(titulo='Fundamentos del Reciclaje', categoria='General', puntos_recompensa=20)
            db.session.add(quiz1)
            db.session.flush() # Para obtener el ID
            
            preguntas_q1 = [
                {'pregunta': '¿Qué color de contenedor se usa para el papel?', 'opciones': json.dumps(['Azul', 'Verde', 'Amarillo', 'Gris']), 'respuesta_correcta': 0, 'explicacion': 'El contenedor azul es internacionalmente usado para papel y cartón.'},
                {'pregunta': '¿Cuánto tiempo tarda una botella de plástico en degradarse?', 'opciones': json.dumps(['10 años', '50 años', '100 años', '500 años']), 'respuesta_correcta': 3, 'explicacion': 'El plástico PET puede tardar hasta 500 años en descomponerse.'},
                {'pregunta': '¿Qué material es infinitamente reciclable?', 'opciones': json.dumps(['Plástico', 'Papel', 'Vidrio', 'Cartón']), 'respuesta_correcta': 2, 'explicacion': 'El vidrio y el metal pueden reciclarse indefinidamente sin perder propiedades.'}
            ]
            
            for p_data in preguntas_q1:
                pregunta = QuizQuestion(quiz_id=quiz1.id, **p_data)
                db.session.add(pregunta)
                
            quiz2 = Quiz(titulo='Huella de Carbono', categoria='Ecología', puntos_recompensa=25)
            db.session.add(quiz2)
            db.session.flush()
            
            preguntas_q2 = [
                {'pregunta': '¿Qué actividad genera más CO2?', 'opciones': json.dumps(['Usar bicicleta', 'Comer carne roja', 'Reciclar', 'Plantar árboles']), 'respuesta_correcta': 1, 'explicacion': 'La industria ganadera es una de las mayores emisoras de gases de efecto invernadero.'},
                {'pregunta': '¿Qué es la huella de carbono?', 'opciones': json.dumps(['Una marca de zapatos', 'Total de gases de efecto invernadero emitidos', 'Huella en el suelo', 'Carbón quemado']), 'respuesta_correcta': 1, 'explicacion': 'Mide la totalidad de gases de efecto invernadero emitidos por efecto directo o indirecto.'}
            ]
            
            for p_data in preguntas_q2:
                pregunta = QuizQuestion(quiz_id=quiz2.id, **p_data)
                db.session.add(pregunta)

        if Mision.query.first():
            print("⚠️  Misiones ya existen. Saltando.")
        else:
            print("🎯 Creando misiones...")
            misiones = [
                # Misiones Diarias
                {'nombre': 'Inicio de Sesión Diario', 'descripcion': 'Inicia sesión en la plataforma.', 'tipo': 'login', 'objetivo': 1, 'recompensa_puntos': 5, 'frecuencia': 'diaria'},
                {'nombre': 'Reciclador de Plástico Diario', 'descripcion': 'Recicla al menos 3 botellas de plástico.', 'tipo': 'reciclaje', 'objetivo': 3, 'recompensa_puntos': 10, 'frecuencia': 'diaria'},
                {'nombre': 'Sabio del Día', 'descripcion': 'Completa un quiz.', 'tipo': 'quiz', 'objetivo': 1, 'recompensa_puntos': 15, 'frecuencia': 'diaria'},
                
                # Misiones Semanales
                {'nombre': 'Reciclador Constante', 'descripcion': 'Recicla un total de 20 objetos durante la semana.', 'tipo': 'reciclaje', 'objetivo': 20, 'recompensa_puntos': 50, 'frecuencia': 'semanal'},
                {'nombre': 'Maratón de Quizzes', 'descripcion': 'Completa 3 quizzes en la semana.', 'tipo': 'quiz', 'objetivo': 3, 'recompensa_puntos': 40, 'frecuencia': 'semanal'},
                {'nombre': 'Compromiso Semanal', 'descripcion': 'Inicia sesión 5 días diferentes en la semana.', 'tipo': 'login', 'objetivo': 5, 'recompensa_puntos': 25, 'frecuencia': 'semanal'}
            ]
            
            for mision_data in misiones:
                mision = Mision(**mision_data, activo=True)
                db.session.add(mision)

        db.session.commit()
        
        print("✅ Base de datos poblada exitosamente!")
        print(f"   - Misiones: {Mision.query.count()}")

if __name__ == '__main__':
    seed_database()
