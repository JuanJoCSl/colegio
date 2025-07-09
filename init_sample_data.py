import sqlite3
import random
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def init_sample_data():
    """Initialize the database with extended sample data for testing"""
    conn = sqlite3.connect('school_management.db')
    
    # ================ ROOMS ================
    rooms_data = [
        ('Aula 101', 30, 'aula', 'Pizarra acrílica, proyector, 30 pupitres', 'Primer piso, ala este'),
        ('Aula 102', 25, 'aula', 'Pizarra de tiza, 25 pupitres, armario', 'Primer piso, ala este'),
        ('Laboratorio Ciencias', 20, 'laboratorio', '20 microscopios, reactivos, mesas resistentes', 'Segundo piso, norte'),
        ('Sala Computación', 25, 'sala_computo', '25 PCs, proyector, aire acondicionado', 'Segundo piso, sur'),
        ('Biblioteca Central', 40, 'biblioteca', 'Colección 5000 libros, 10 PCs, zona silenciosa', 'Planta baja, centro'),
        ('Auditorio Principal', 150, 'auditorio', 'Sistema sonido 5.1, proyector 4K, escenario', 'Planta baja, este'),
        ('Gimnasio', 80, 'gimnasio', 'Cancha multiusos, equipos fitness, vestuarios', 'Exterior, oeste'),
        ('Taller Arte', 25, 'taller', 'Caballetes, materiales pintura, horno cerámica', 'Tercer piso, norte'),
        ('Laboratorio Idiomas', 20, 'laboratorio', '20 cabinas, sistema audio, pantalla interactiva', 'Segundo piso, centro'),
        ('Aula 201', 35, 'aula', 'Pizarra inteligente, sistema videoconferencia', 'Segundo piso, este')
    ]
    
    for room in rooms_data:
        conn.execute('''
            INSERT OR IGNORE INTO rooms (name, capacity, room_type, equipment, location)
            VALUES (?, ?, ?, ?, ?)
        ''', room)
    
    # ================ SCHEDULES (2 semanas completas) ================
    # Generar horarios para 2 semanas laborales (lunes a viernes)
    start_date = datetime(2024, 1, 15)  # Lunes
    subjects = [1, 2, 3, 4, 5, 6, 7]    # IDs de materias
    teachers = [1, 2, 3, 4, 5]          # IDs de profesores
    rooms = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # IDs de aulas
    grades = ['1ro Primaria', '2do Primaria', '3ro Primaria', 
              '4to Primaria', '5to Primaria', '6to Primaria',
              '1ro Secundaria', '2do Secundaria', '3ro Secundaria']
    
    time_slots = [
        ('08:00', '09:00'),
        ('09:00', '10:00'),
        ('10:30', '11:30'),
        ('11:30', '12:30'),
        ('14:00', '15:00'),
        ('15:00', '16:00')
    ]
    
    schedules_data = []
    for week in range(2):  # 2 semanas
        for day in range(5):  # 5 días (lun-vie)
            current_date = start_date + timedelta(weeks=week, days=day)
            date_str = current_date.strftime('%Y-%m-%d')
            
            for slot_idx, (start_time, end_time) in enumerate(time_slots):
                # Variar asignaciones para crear un horario realista
                subject_id = subjects[(day + slot_idx) % len(subjects)]
                teacher_id = teachers[(day + slot_idx + week) % len(teachers)]
                room_id = rooms[(day * 2 + slot_idx) % len(rooms)]
                grade_level = grades[(day + week) % len(grades)]
                
                notes = f"Clase regular de {get_subject_name(subject_id)} para {grade_level}"
                
                schedules_data.append((
                    subject_id, teacher_id, room_id, date_str, 
                    start_time, end_time, grade_level, notes
                ))
    
    for schedule in schedules_data:
        conn.execute('''
            INSERT OR IGNORE INTO schedules (subject_id, teacher_id, room_id, date, start_time, end_time, grade, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', schedule)
    
    # ================ ANNOUNCEMENTS ================
    announcements_data = [
        # Académicos
        ('Exámenes Bimestrales', 'Del 5 al 9 de febrero se realizarán los exámenes del primer bimestre. Consulten el cronograma en Secretaría.', 'academico', 'alta', 'todos', 1, '2024-02-10'),
        ('Taller de Matemáticas', 'Refuerzo para estudiantes de secundaria los viernes de 15:00 a 17:00 en el Aula 201. Inscripciones abiertas.', 'academico', 'media', 'estudiantes', 1, '2024-03-01'),
        ('Entrega de Proyectos Ciencia', 'Fecha límite: 25 de enero. Los proyectos deben incluir informe escrito y demostración práctica.', 'academico', 'alta', 'estudiantes', 2, '2024-01-26'),
        
        # Administrativos
        ('Pago de Pensiones', 'Recordatorio: Último día para pago sin recargo es el 30 de enero. Pueden pagar en caja o por transferencia.', 'administrativo', 'media', 'padres', 1, '2024-01-31'),
        ('Actualización de Datos', 'Padres de familia, favor actualizar datos de contacto en la plataforma antes del 20 de enero.', 'administrativo', 'baja', 'padres', 1, '2024-01-21'),
        ('Cambio en Transporte Escolar', 'A partir del 1 de febrero, la ruta 3 tendrá nuevo horario. Consulten en administración.', 'administrativo', 'media', 'padres', 1, '2024-02-05'),
        
        # Eventos
        ('Feria del Libro', 'Del 15 al 17 de febrero en la biblioteca. Descuentos especiales para estudiantes. ¡No falten!', 'evento', 'media', 'todos', 1, '2024-02-18'),
        ('Día del Deporte', '24 de enero: Competencias interaulas. Inscripciones abiertas en dirección deportiva.', 'evento', 'alta', 'estudiantes', 3, '2024-01-25'),
        ('Concierto de Fin de Trimestre', 'Presentación de la orquesta estudiantil el 28 de enero a las 18:00 en el auditorio. Entrada libre.', 'evento', 'baja', 'todos', 1, '2024-01-29'),
        
        # Emergencias
        ('Suspensión de Clases', 'Mañana 22 de enero no habrá clases debido a alerta meteorológica. Manténganse informados.', 'emergencia', 'alta', 'todos', 1, '2024-01-23'),
        ('Protocolo COVID', 'Recordatorio: Uso obligatorio de mascarillas en espacios cerrados. Favor reportar síntomas.', 'emergencia', 'alta', 'todos', 1, '2024-02-28'),
        
        # Generales
        ('Becas Estudiantiles', 'Convocatoria abierta para becas de excelencia académica. Postulaciones hasta el 15 de febrero.', 'general', 'media', 'padres', 1, '2024-02-16'),
        ('Nuevo Servicio de Cafetería', 'A partir de febrero, nuevo menú saludable en cafetería. Horario extendido hasta las 16:30.', 'general', 'baja', 'todos', 1, '2024-02-10'),
        ('Voluntariado Ambiental', 'Únete al programa de reciclaje los sábados de 9:00 a 12:00. Certificados de participación disponibles.', 'general', 'media', 'estudiantes', 2, '2024-03-15'),
        
        # Anuncios específicos por rol
        ('Capacitación Docente', 'Jueves 25 de enero, 15:00-17:00: Taller de nuevas metodologías educativas. Sala de Profesores.', 'academico', 'alta', 'profesores', 1, '2024-01-26'),
        ('Reunión APAFA', 'Miércoles 31 de enero, 18:00: Planificación actividades del trimestre. Confirmar asistencia.', 'administrativo', 'media', 'padres', 1, '2024-02-01')
    ]
    
    for announcement in announcements_data:
        conn.execute('''
            INSERT OR IGNORE INTO announcements (title, content, category, priority, target_audience, author_id, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', announcement)
    
    # ================ EVENTOS ESPECIALES EN CALENDARIO ================
    special_events = [
        ('Conferencia de Ciencia', '2024-02-05', '14:00', '16:00', 'Auditorio Principal', 'Conferencista invitado: Dr. Luis Pérez, Premio Nacional de Ciencias'),
        ('Olimpiada Matemática', '2024-02-12', '09:00', '12:00', 'Aula 201', 'Competencia intercolegial - Equipo seleccionado'),
        ('Feria Vocacional', '2024-02-20', '10:00', '14:00', 'Gimnasio', 'Universidades participantes: UMSA, UCB, UPSA, UE'),
        ('Festival Cultural', '2024-03-08', '15:00', '18:00', 'Auditorio Principal', 'Presentaciones de danza, música y teatro estudiantil'),
        ('Campaña de Vacunación', '2024-03-15', '08:00', '12:00', 'Enfermería', 'Vacunas influenza para estudiantes - Traer carnet de vacunación')
    ]
    
    for event in special_events:
        conn.execute('''
            INSERT INTO schedules (subject_id, teacher_id, room_id, date, start_time, end_time, grade, notes)
            SELECT NULL, NULL, r.id, ?, ?, ?, 'Evento Especial', ?
            FROM rooms r WHERE r.name = ?
        ''', (event[1], event[2], event[3], event[4], event[0]))
    
    conn.commit()
    conn.close()
    print("¡Datos de muestra extendidos creados exitosamente!")

def get_subject_name(subject_id):
    """Función auxiliar para obtener nombre de materia"""
    subjects = {
        1: 'Matemáticas',
        2: 'Ciencias Naturales',
        3: 'Lenguaje y Literatura',
        4: 'Historia',
        5: 'Inglés',
        6: 'Educación Física',
        7: 'Arte'
    }
    return subjects.get(subject_id, 'Materia General')

if __name__ == '__main__':
    init_sample_data()