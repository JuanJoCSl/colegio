# Sistema de Gestión Escolar - Rafael Mendoza Castellón

Este es un sistema web desarrollado en Flask para la gestión integral de la Unidad Educativa "Rafael Mendoza Castellón".

## Características

- **Gestión de Estudiantes**: Registro, edición, eliminación y listado de estudiantes
- **Gestión de Profesores**: Administración completa del personal docente
- **Gestión de Materias**: Control de asignaturas y asignación de profesores
- **Gestión de Notas**: Registro y consulta de calificaciones
- **Sistema de Horarios**: Programación y visualización de clases con calendario interactivo
- **Sistema de Anuncios**: Publicación y gestión de anuncios con categorización y filtros
- **Gestión de Aulas**: Administración de espacios físicos y recursos
- **Sistema de Autenticación**: Control de acceso por roles (Director, Profesor, Padre)
- **Dashboard Informativo**: Estadísticas y resumen del sistema con anuncios recientes

## Nuevas Funcionalidades

### Sistema de Horarios
- Vista de lista semanal de clases programadas
- Calendario interactivo con FullCalendar
- Asignación de profesores, materias y aulas
- Gestión de horarios por grado
- Navegación por semanas

### Sistema de Anuncios
- Publicación de anuncios con diferentes prioridades
- Categorización (Académico, Administrativo, Evento, Emergencia, General)
- Filtros por categoría y prioridad
- Dirigido a audiencias específicas (Todos, Estudiantes, Profesores, Padres)
- Fechas de expiración opcionales
- Vista detallada de anuncios

### Gestión de Aulas
- Registro de aulas con capacidad y equipamiento
- Diferentes tipos de espacios (Aula, Laboratorio, Biblioteca, etc.)
- Información de ubicación y recursos disponibles

## Roles de Usuario

1. **Director**: Acceso completo al sistema
2. **Profesor**: Gestión de estudiantes y notas
3. **Padre**: Consulta de notas de sus hijos

## Instalación

1. Instalar las dependencias:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. Ejecutar la aplicación:
\`\`\`bash
python app.py
\`\`\`

3. Inicializar datos de prueba (opcional):
\`\`\`bash
python scripts/init_sample_data.py
\`\`\`

## Acceso al Sistema

**Usuario Administrador por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

**Usuarios de prueba (después de ejecutar init_sample_data.py):**
- Profesor: `profesor1` / `profesor123`
- Padre: `padre1` / `padre123`

## Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Base de Datos**: SQLite3
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Iconos**: Font Awesome

## Estructura del Proyecto

\`\`\`
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias
├── README.md             # Documentación
├── school_management.db  # Base de datos SQLite
├── scripts/
│   └── init_sample_data.py
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── students/
    ├── teachers/
    ├── grades/
    └── subjects/
\`\`\`

## Funcionalidades Implementadas

### Módulo de Estudiantes
- ✅ Registrar estudiante (CU 3)
- ✅ Editar estudiante (CU 4)
- ✅ Eliminar estudiante (CU 5)
- ✅ Listar estudiantes (CU 7)

### Módulo de Profesores
- ✅ Crear profesor (CU 8)
- ✅ Editar profesor (CU 9)
- ✅ Eliminar profesor (CU 10)
- ✅ Listar profesores (CU 12)

### Módulo de Notas
- ✅ Registrar notas (CU 14)
- ✅ Consultar notas (CU 13)
- ✅ Listar notas (CU 15)

### Sistema de Autenticación
- ✅ Iniciar sesión (CU 1)
- ✅ Validar datos (CU 2)
- ✅ Control de roles y permisos

## Base de Datos Actualizada

El sistema ahora incluye las siguientes tablas adicionales:
- `rooms`: Información de aulas y espacios
- `schedules`: Horarios de clases programadas
- `announcements`: Sistema de anuncios y comunicaciones

## Base de Datos

El sistema utiliza SQLite3 con las siguientes tablas:
- `users`: Usuarios del sistema
- `students`: Información de estudiantes
- `teachers`: Información de profesores
- `subjects`: Materias/asignaturas
- `grades`: Calificaciones

## Funcionalidades por Rol

### Director
- Acceso completo a todas las funcionalidades
- Gestión de horarios y aulas
- Publicación y eliminación de anuncios
- Administración completa del sistema

### Profesor
- Gestión de estudiantes y notas
- Creación y edición de horarios
- Publicación y edición de anuncios
- Consulta de información del sistema

### Padre
- Consulta de notas de sus hijos
- Visualización de horarios
- Lectura de anuncios dirigidos a padres
- Acceso al calendario de actividades

## Seguridad

- Autenticación basada en sesiones
- Contraseñas hasheadas con Werkzeug
- Control de acceso por roles
- Validación de permisos en cada ruta
