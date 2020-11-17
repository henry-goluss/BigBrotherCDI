from db.db import DBConnection

# Connection to database
DB = DBConnection()

def get_students_in_period(date_start, date_end):
    """
        Take two dates (date_start and date_end) of the following form:
            string: 'YYYY-MM-dd hh: mm: ss'
            ex: '2020-10-12 16: 24: 26.073276'
        These are the start and end dates of the interval.
        Returns an array of student IDs, each ID appears only once.
        ------
        Prends deux dates (date_start et date_end) de la forme suivante :
            string : 'YYYY-MM-dd hh:mm:ss'
            ex : '2020-10-12 16:24:26.073276'
        Ce sont les dates du début et de fin de l'intervalle.
        Retourne un tableau d'identifiants d'élèves, chaque identifiant
        n'apparaît qu'une fois.
    """

    cur = DB.conn.cursor()
    cur.execute("SELECT * FROM Passages WHERE passage_time BETWEEN ? AND ?", (date_start, date_end))
    db_results = cur.fetchall()

    students = []
    for passage in db_results:
        if passage[0] not in students:
            students.append(passage[0])

    return students

def get_student_in_contact_in_period(id_eleve, date_start, date_end):
    """
        Take the identifier of a student.
        Take two dates (date_start and date_end) of the following form:
            string: 'YYYY-MM-dd hh: mm: ss'
            ex: '2020-10-12 16: 24: 26.073276'
        These are the start and end dates of the interval.
        Returns an array of student IDs, each ID appears only once.
        ------
        Prends l'identifiant d'un élève.
        Prends deux dates (date_start et date_end) de la forme suivante :
            string : 'YYYY-MM-dd hh:mm:ss'
            ex : '2020-10-12 16:24:26.073276'
        Ce sont les dates du début et de fin de l'intervalle.
        Retourne un tableau d'identifiants d'élèves, chaque identifiant
        n'apparaît qu'une fois.
    """
    students_in_period = get_students_in_period(date_start, date_end)

    if id_eleve not in students_in_period:
        return 1

    students_in_period.remove(id_eleve)

    return students_in_period