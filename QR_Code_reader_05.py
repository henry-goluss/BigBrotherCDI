import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
import datetime
import time
from pydub import AudioSegment
from pydub.playback import play
import sqlite3
import os

from db.db import DBConnection

# Connection to database
DB = DBConnection()

"""
    PARTIE PURGE
"""
def purge_alreadyScanned(alreadyScanned):
    for key in list(alreadyScanned.keys()):
        if alreadyScanned[key]<=datetime.datetime.now(): 
            del alreadyScanned[key]
    return alreadyScanned
"""
    FIN PARTIE PURGE
"""

"""
    CAPTURE QR CODE
"""
#lancer la capture vidéo
cap = cv2.VideoCapture(0)

def capture_qrcode():
    #capture et affichage de l'image
    _, frame = cap.read()
    cv2.imshow("Frame", frame)
    return pyzbar.decode(frame)
"""
    FIN PARTIE QR CODE
"""

def add_to_db(id_e,timestamp):
    cur = DB.conn.cursor()
    cur.execute("INSERT INTO Passages (id_eleve, passage_time) VALUES (?, ?)", (id_e, timestamp))
    DB.conn.commit()

    DB.dump()

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
    #Parcours des QRcodes récupérés
    for obj in decodedObjects:
        id_eleve = obj.data.decode("utf-8") 
        #Vérification que l'on ne traite pas 2 fois le même objet
        if id_eleve not in alreadyScanned:
            #Ajout de l'id eleve dans AlreadyScanned afin qu'il ne soit pas scanné plusieurs fois de suite
            alreadyScanned[id_eleve]=scan_time+datetime.timedelta(minutes=5)
            
            #MAJ de la BDD
            add_to_db(id_eleve, scan_time)

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