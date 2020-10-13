import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
import datetime
import time
from pydub import AudioSegment
from pydub.playback import play

from db.db import DBConnection

beep = AudioSegment.from_file("beep.wav")

def purge_alreadyScanned(alreadyScanned):
    """
        Takes a dictionary as a parameter whose values are 
        timestamps and removes from this dictionary all 
        entries whose timestamp + 5mn is less than the current timestamp.
        -----
        Prend un dictionnaire en paramètre dont les valeurs sont
        des timestamps et supprime de ce dictionnaire toutes les 
        entrées dont le timestamp + 5mn est inférieur au timestamp actuel.
    """
    for key in list(alreadyScanned.keys()):
        if alreadyScanned[key]+datetime.timedelta(minutes=5)<=datetime.datetime.now(): 
            del alreadyScanned[key]
    return alreadyScanned

def capture_qrcode():
    """
        Takes an image from "cap" and returns its qr codes
        -----
        Prend une image de "cap" et retourne ses qr codes
    """
    _, frame = cap.read() # frame capture
    flipped_frame=cv2.flip(frame, 1)
    return flipped_frame, pyzbar.decode(flipped_frame) # return qr codes

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

def add_infos(qr_code_object, frame, scan_time): 
    """
        Takes the QrCode object from pyzbar, 
        the frame and the date of the scan. 
        Returns the (modified) frame.
        If the scan date has passed for less than 3 seconds,
        "Scanne!" is displayed in green. If it has been 
        exceeded for more than 3 seconds, 
        "Scanne il y a moins de 5 mn" is displayed in orange.
        -----
        Prend l'objet QrCode de pyzbar, 
        la frame et la date du scan. 
        Retourne la frame (modifiée).
        Si la date du scan est dépassée depuis moins de 3 secondes, 
        on affiche "Scanne !" en vert. Si elle est dépassée 
        depuis plus de 3 secondes, on affiche 
        "Scanne il y a moins de 5 mn" en orange.
    """


    if not isinstance(qr_code_object, pyzbar.Decoded):
        return frame
    if not isinstance(frame, np.ndarray):
        return frame
    if not isinstance(scan_time, datetime.datetime):
        return frame

    pts = np.array([
        [
            qr_code_object.polygon[0].x,
            qr_code_object.polygon[0].y
        ],
        [
            qr_code_object.polygon[1].x,
            qr_code_object.polygon[1].y
        ],
        [
            qr_code_object.polygon[2].x,
            qr_code_object.polygon[2].y
        ],
        [
            qr_code_object.polygon[3].x,
            qr_code_object.polygon[3].y
        ]
    ], np.int32) # creates an array of polygon points from the QrCode
    pts = pts.reshape((-1,1,2))

    # default
    color = (0, 165, 255) # orange
    text = "Scanne il y a moins de 5 mn"
    
    # if the scan date has passed for less than 3 seconds
    time_between_scan_and_now = (datetime.datetime.now() - scan_time).total_seconds()
    if time_between_scan_and_now < 3:
        color = (0, 255, 0) # green
        text = "Scanne !"


    frame = cv2.polylines(frame, [pts], True, color, thickness=5) # draw the outline of the qrcode

    labelSize=cv2.getTextSize(text,cv2.FONT_HERSHEY_COMPLEX,0.5,2) # calculating the text size on the screen

    labelX = int(qr_code_object.rect.left + qr_code_object.rect.width / 2 - labelSize[0][0]/2) # text X
    labelY = int(qr_code_object.rect.top + qr_code_object.rect.height + 30) # text Y

    padding = 8

    frame = cv2.rectangle(frame,
        (
            labelX - padding,
            labelY + padding
        ),
        (
            labelX + int(labelSize[0][0]) + padding,
            labelY - int(labelSize[0][1]) - padding
        )
        , color, cv2.FILLED) # draw a background for the text

    frame = cv2.putText(frame, text, (labelX, labelY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA) # draw the text
    
    return frame


# Connection to database
DB = DBConnection()
# Start Video Capture
cap = cv2.VideoCapture(0)

alreadyScanned=dict() 

while True:

    #Pour éviter trop de charge CPU
    time.sleep(0.1)
    
    #On enlève les codes élèves déja scannés il y a plus de 5min
    alreadyScanned=purge_alreadyScanned(alreadyScanned)

    #Affichage de l'image et récupération des codes
    frame, decodedObjects=capture_qrcode()

    #Récupération de l'heure du scan
    scan_time = datetime.datetime.now()
    #Parcours des QRcodes récupérés
    for obj in decodedObjects:
        id_eleve = obj.data.decode("utf-8") 
        #Vérification que l'on ne traite pas 2 fois le même objet
        if id_eleve not in alreadyScanned:
            #Ajout de l'id eleve dans AlreadyScanned afin qu'il ne soit pas scanné plusieurs fois de suite
            alreadyScanned[id_eleve]=scan_time
            
            #MAJ de la BDD
            add_to_db(id_eleve, alreadyScanned[id_eleve])
            play(beep)

        frame = add_infos(obj, frame, alreadyScanned[id_eleve]) # update the frame with the text...

    cv2.imshow("Frame", frame) # frame display
            
    #Capture d'un appui de touche sur le clavier
    key = cv2.waitKey(1)
    if key == 27:    # 27 code ascci touche "echap"
        cap.release()
        cv2.destroyWindow("Frame")
        break


# pip install -r requirements.txt

# https://www.sqlshack.com/python-scripts-to-format-data-in-microsoft-excel/