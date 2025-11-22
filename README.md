# 🌱 UCA Puntos Verdes - Sistema de Reciclaje Gamificado

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Sistema web completo de puntos por reciclaje para la Universidad Centroamericana José Simeón Cañas (UCA), implementado con gamificación tipo Duolingo e incluyendo un mini casino verde.

## 🎯 Características Principales

### Sistema de Reciclaje
- ♻️ Registro de materiales reciclados con puntos
- 📊 Tracking de impacto ambiental (CO₂, agua, árboles)
- 🏅 Sistema de niveles progresivos (Semilla Verde → Eco Maestro)
- 🔥 Rachas diarias tipo Duolingo
- 🏆 Sistema de logros desbloqueables

### Formas de Ganar Puntos
- **Reciclaje:** Latas (5 pts), Vidrio (8 pts), Plástico (3 pts), Cartón (4 pts)
- **Quizzes Educativos:** 15 puntos por quiz completado
- **Eventos y Voluntariados:** 30-100 puntos según actividad
- **Desafíos Semanales:** Bonificaciones por cumplir metas

### Sistema de Rankings
- 👑 Top estudiantes más verdes
- 🏛️ Ranking de facultades
- 🎓 Ranking de carreras
- 📈 Estadísticas globales mensuales

### Catálogo de Recompensas
- ☕ Descuentos en cafetería (10%, 20%)
- 🎁 Merchandising UCA ecológico
- 📜 Certificados de sostenibilidad
- 🚗 Estacionamiento preferencial
- 📚 Acceso a espacios de estudio premium

### 🎰 Casino Verde
- **Ruleta Verde:** Apuestas en números, colores, par/impar (multiplicador hasta x35)
- **Slots Ecológicos:** 3 rodillos con símbolos verdes (jackpot x50)
- **Dados Verdes:** Lanzamiento de 2 dados con múltiples apuestas (hasta x30)
- Límite responsable: máximo 30% del saldo por apuesta
- Historial completo de jugadas

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.8+**
- **Flask 3.0** - Framework web
- **Flask-SQLAlchemy** - ORM para base de datos
- **Flask-Login** - Sistema de autenticación
- **Flask-WTF** - Formularios seguros con CSRF protection
- **Flask-Bcrypt** - Hash de contraseñas
- **SQLite** - Base de datos (fácil migración a PostgreSQL)

### Frontend
- **HTML5 + Jinja2** - Templates dinámicos
- **CSS3** - Variables CSS, Grid, Flexbox
- **JavaScript Vanilla** - Interactividad y AJAX
- **Diseño Responsive** - Mobile-first

## 📋 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes Python)
- Git

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Al3X838/Duolingo-Verde.git
cd Duolingo-Verde
```

### 2. Crear entorno virtual

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno (Opcional)

Crea un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu-clave-secreta-super-segura
DATABASE_URL=sqlite:///uca_verde.db
FLASK_ENV=development
```

### 5. Inicializar la base de datos

```bash
# Ejecutar app.py por primera vez crea las tablas automáticamente
python app.py

# Ctrl+C para detener

# Poblar con datos iniciales
python seed.py
```

### 6. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

## 👥 Usuarios de Prueba

### Administrador
- **Usuario:** `admin`
- **Contraseña:** `admin123`
- Acceso completo al panel de administración

### Estudiantes
- **Usuario:** `estudiante1`
- **Contraseña:** `test123`
- Cuenta con 450 puntos iniciales

- **Usuario:** `estudiante2`
- **Contraseña:** `test123`
- Cuenta con 320 puntos iniciales

## 📁 Estructura del Proyecto

```
Duolingo-Verde/
├── app.py                      # Aplicación principal Flask
├── models.py                   # Modelos de base de datos
├── config.py                   # Configuración
├── utils.py                    # Funciones auxiliares
├── forms.py                    # Formularios WTForms
├── seed.py                     # Script de datos iniciales
├── requirements.txt            # Dependencias Python
├── routes/
│   ├── __init__.py
│   ├── auth.py                # Rutas de autenticación
│   ├── main.py                # Rutas principales
│   ├── recycle.py             # Rutas de reciclaje
│   ├── rewards.py             # Rutas de recompensas
│   ├── casino.py              # Rutas del casino
│   └── admin.py               # Rutas de administración
├── templates/
│   ├── base.html              # Template base
│   ├── index.html             # Dashboard principal
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── recycle/
│   │   ├── recycle.html
│   │   └── history.html
│   ├── tasks/
│   │   ├── tasks.html
│   │   ├── quiz.html
│   │   └── events.html
│   ├── rewards/
│   │   ├── rewards.html
│   │   └── my_rewards.html
│   ├── rankings/
│   │   └── rankings.html
│   ├── casino/
│   │   ├── casino.html
│   │   ├── ruleta.html
│   │   ├── slots.html
│   │   └── dados.html
│   ├── profile/
│   │   └── profile.html
│   └── admin/
│       ├── dashboard.html
│       └── materials.html
├── static/
│   ├── css/
│   │   ├── style.css
│   │   ├── casino.css
│   │   └── animations.css
│   ├── js/
│   │   ├── main.js
│   │   ├── casino.js
│   │   ├── ruleta.js
│   │   ├── slots.js
│   │   └── dados.js
│   └── images/
└── README.md
```

## 🎮 Guía de Uso

### Para Estudiantes

1. **Registro:** Crea tu cuenta con tus datos de la UCA
2. **Reciclar:** Registra materiales en el Centro de Reciclaje
3. **Tareas:** Completa quizzes y participa en eventos
4. **Recompensas:** Canjea tus puntos por premios
5. **Casino:** Prueba tu suerte (máximo 30% del saldo)
6. **Rankings:** Compite por ser el estudiante más verde

### Para Administradores

1. **Dashboard Admin:** Acceso desde el menú de usuario
2. **Gestionar Materiales:** Agregar, editar o desactivar materiales
3. **Gestionar Recompensas:** Administrar catálogo y stock
4. **Ver Estadísticas:** Monitorear actividad del sistema

## 🎯 Sistema de Niveles

| Nivel | Puntos Requeridos |
|-------|-------------------|
| 🌱 Semilla Verde | 0 - 100 |
| 🌿 Brote Ecológico | 101 - 300 |
| 🍃 Alumno Verde | 301 - 600 |
| 🛡️ Guardián Ambiental | 601 - 1000 |
| 👑 Líder Sostenible | 1001 - 1500 |
| 🏆 Eco Maestro | 1501+ |

## 🏆 Logros Disponibles

- **🌱 Primer Paso Verde:** Realiza tu primer reciclaje
- **🔥 Racha de Fuego:** Mantén 7 días consecutivos de actividad
- **💯 Centurión Verde:** Alcanza 100 puntos totales
- **♻️ Maestro del Reciclaje:** Realiza 50 reciclajes

## 🎰 Reglas del Casino

- **Apuesta Mínima:** 10 puntos
- **Apuesta Máxima:** 30% de tu saldo actual
- **Ruleta:** Multiplicador hasta x35 (número específico)
- **Slots:** Jackpot x50 (3 símbolos ♻️)
- **Dados:** Multiplicador hasta x30 (sumas extremas)

## 🔐 Seguridad

- ✅ Hash de contraseñas con bcrypt
- ✅ CSRF protection en todos los formularios
- ✅ Validación de inputs en backend
- ✅ Session management seguro
- ✅ SQL injection prevention (ORM)
- ✅ Rate limiting en casino

## 📊 Base de Datos

### Modelos Principales

- **User:** Usuarios del sistema
- **Material:** Materiales reciclables
- **Transaction:** Historial de puntos
- **Reward:** Catálogo de recompensas
- **UserReward:** Canjes realizados
- **Achievement:** Logros disponibles
- **UserAchievement:** Logros obtenidos
- **CasinoGame:** Historial de casino
- **Quiz:** Quizzes educativos
- **QuizQuestion:** Preguntas de quizzes
- **UserQuiz:** Quizzes completados

## 🐛 Solución de Problemas

### Error: ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### Error: Base de datos no se crea
```bash
# Eliminar archivo existente
rm uca_verde.db
# Ejecutar de nuevo
python app.py
python seed.py
```

### Error: Puerto 5000 en uso
```bash
# Cambiar puerto en app.py línea final
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 🚀 Despliegue en Producción

### Heroku

```bash
# Instalar Heroku CLI
heroku create uca-verde
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
heroku run python seed.py
```

### Variables de Entorno Requeridas

```
SECRET_KEY=clave-super-segura-aleatoria
DATABASE_URL=postgresql://...
FLASK_ENV=production
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Roadmap

- [ ] App móvil (React Native)
- [ ] Notificaciones push
- [ ] Integración con API de pagos
- [ ] Sistema de referidos
- [ ] Marketplace de productos ecológicos
- [ ] Integración con redes sociales
- [ ] Modo oscuro
- [ ] Multiidioma (ES/EN)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

**Al3X838** - [GitHub](https://github.com/Al3X838)

## 🙏 Agradecimientos

- Universidad Catolica Nuestra Senora de asuncion (UCA)
- Comunidad Flask
- Todos los estudiantes comprometidos con el medio ambiente

## 📧 Contacto

- Email: verde@uca.edu.sv
- GitHub Issues: [Reportar problema](https://github.com/Al3X838/Duolingo-Verde/issues)

---

Hecho con 💚 para un campus más sostenible

**¡Recicla, aprende y gana!** 🌱♻️🏆