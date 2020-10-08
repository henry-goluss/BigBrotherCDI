import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
import datetime
import time
from pydub import AudioSegment
from pydub.playback import play
import sqlite3
import os

"""
    DATABASE CONNECTION
"""
db_file = "db/passages_CDI.db"
sql_file = "db/passages_CDI.sql"
sql_init_file = "db/passages_CDI-init.sql"

def db_connect():
    need_dump = False
    if not os.path.exists(db_file):
        need_dump = True

    try:
        conn = sqlite3.connect(db_file)
		# Activate foreign keys
        conn.execute("PRAGMA foreign_keys = 1")
        
        if need_dump:
            sql_file_to_use = sql_init_file

            if os.path.exists(sql_file):
                sql_file_to_use = sql_file

            createFile = open(sql_file_to_use, 'r')
            createSql = createFile.read()
            createFile.close()
            sqlQueries = createSql.split(";")

            cursor = conn.cursor()
            for query in sqlQueries:
                cursor.execute(query)

            conn.commit()

        return conn
    except sqlite3.Error as e:
        print("db : " + str(e))

    return None

def db_dump(db_conn):
    with open(sql_file, 'w') as f:
        for line in db_conn.iterdump():
            f.write('%s\n' % line)
db_conn = db_connect()

"""
    END DATABASE CONNECTION
"""


def purge_alreadyScanned(alreadyScanned):
    return alreadyScanned

def capture_qrcode():
    return [
        pyzbar.Decoded(
            data=b'Foramenifera', type='CODE128',
            rect=None,
            polygon=None
            
        )
    ]

def add_to_db(id_e,timestamp):
    cur = db_conn.cursor()
    cur.execute("INSERT INTO Passages (id_eleve, passage_time) VALUES (?, ?)", (id_e, timestamp))
    db_conn.commit()

    db_dump(db_conn)

def show_warning(status):
    pass

alreadyScanned=dict()

while True:

    #Pour éviter trop de charge CPU
    time.sleep(0.1)
    
    #On enlève les codes élèves déja scannés il y a plus de 5min
    alreadyScanned=purge_alreadyScanned(alreadyScanned)

    #Affichage de l'image et récupération des codes
    decodedObjects=capture_qrcode()

    #Récupération de l'heure du scan
    scan_time = datetime.datetime.now()
    print("ok")
    #Parcours des QRcodes récupérés
    for obj in decodedObjects:
        id_eleve = obj.data
        #Vérification que l'on ne traite pas 2 fois le même objet
        if id_eleve not in alreadyScanned:
            #Ajout de l'id eleve dans AlreadyScanned afin qu'il ne soit pas scanné plusieurs fois de suite
            alreadyScanned[id_eleve]=scan_time+datetime.timedelta(minutes=5)
            
            #MAJ de la BDD
            add_to_db(id_eleve, alreadyScanned[id_eleve])

            show_warning('ok')
        else :
            show_warning('nok')
            
    #Capture d'un appui de touche sur le clavier
    key = cv2.waitKey(1)
    if key == 27:    # 27 code ascci touche "echap"
        cap.release()
        cv2.destroyWindow("Frame")
        break



# conda install opencv
# pip install pyzbar
# pip install pydub

# https://www.sqlshack.com/python-scripts-to-format-data-in-microsoft-excel/