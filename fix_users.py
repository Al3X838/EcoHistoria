from app import create_app  # <--- IMPORTAMOS LA FÁBRICA, NO LA APP DIRECTAMENTE
from models import db, User, Transaction, UserReward, UserAchievement, UserQuiz, UserMision, CasinoGame

# Inicializamos la app usando la fábrica
app = create_app()

def limpiar_usuarios():
    # Usamos el contexto de la app que acabamos de crear
    with app.app_context():
        nombres_a_borrar = ["Asad Armele", "Alexander Pereira", "José Romero"]
        print("--- INICIANDO LIMPIEZA ---")

        for nombre in nombres_a_borrar:
            # Buscamos coincidencias parciales
            usuarios = User.query.filter(User.nombre_completo.ilike(f"%{nombre}%")).all()
            
            if not usuarios:
                print(f"⚠️ No se encontró a nadie llamado: {nombre}")
                continue

            for u in usuarios:
                print(f"🗑️ Procesando a: {u.nombre_completo} (ID: {u.id})")
                
                try:
                    # 1. Borrar historial (Tablas hijas)
                    Transaction.query.filter_by(user_id=u.id).delete()
                    UserReward.query.filter_by(user_id=u.id).delete()
                    UserAchievement.query.filter_by(user_id=u.id).delete()
                    UserQuiz.query.filter_by(user_id=u.id).delete()
                    UserMision.query.filter_by(user_id=u.id).delete()
                    CasinoGame.query.filter_by(user_id=u.id).delete()
                    
                    # 2. Borrar al usuario padre
                    db.session.delete(u)
                    print(f"   -> Eliminado correctamente.")
                except Exception as e:
                    print(f"   ❌ Error al eliminar {u.username}: {e}")

        # 3. Confirmar cambios
        db.session.commit()
        print("✅ ¡Limpieza y commit finalizados!")

if __name__ == "__main__":
    limpiar_usuarios()