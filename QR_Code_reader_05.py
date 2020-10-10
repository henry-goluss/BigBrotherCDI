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
# Video Capture
cap = cv2.VideoCapture(0)

def purge_alreadyScanned(alreadyScanned):
    """
        Takes a dictionary as a parameter whose values are 
        timestamps and removes from this dictionary all 
        entries whose timestamp is less than the current timestamp.
        -----
        Prend un dictionnaire en paramètre dont les valeurs sont
        des timestamps et supprime de ce dictionnaire toutes les 
        entrées dont le timestamp est inférieur au timestamp actuel.
    """
    for key in list(alreadyScanned.keys()):
        if alreadyScanned[key]<=datetime.datetime.now(): 
            del alreadyScanned[key]
    return alreadyScanned

def capture_qrcode():
    """
        Takes an image from "cap" and returns its qr codes
        -----
        Prend une image de "cap" et retourne ses qr codes
    """
    _, frame = cap.read() # frame capture
    cv2.imshow("Frame", frame) # frame display
    return pyzbar.decode(frame) # return qr codes

def add_to_db(id_e,timestamp):
    """
        Takes in parameters a student ID, a timestamp 
        and stores them in the database then makes a dump.
        -----
        Prend en paramètres un ID élève, un timestamp 
        et les stocke dans la base de données puis fait un dump.
    """

    if not isinstance(id_e, str):
        return

    if not isinstance(timestamp, datetime.datetime):
        return

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