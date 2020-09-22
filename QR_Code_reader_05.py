import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
from datetime import datetime
import time
import winsound

frequency = 1600  # Set Sound Frequency To 1500 Hertz
duration = 250  # Set Sound Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)

#Lance la capture video
cap = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_PLAIN

oldData = ""
while True:

    #Pour éviter trop de charge CPU
    time.sleep(0.1)
    
    #Capture et affichage de l'image
    _, frame = cap.read()
    cv2.imshow("Frame", frame)

    #Récupération des QRcodes de l'image dans decodedObjects
    decodedObjects = pyzbar.decode(frame)

    #Parcours des QRcodes récupérés
    for obj in decodedObjects:
        Data = obj.data
        #Vérification que l'on ne traite pas 2 fois le même objet
        if Data != oldData:
            oldData = Data
            winsound.Beep(frequency, duration)
            #Pour afficher un texte sur l'image mais ne semble pas fonctionner.
            cv2.putText(frame, str(obj.data), (50, 50), font, 2,
                        (255, 0, 0), 3)

            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            #Affichage du numéro contenu dans le QRcode et de la date en console
            print("Data + date and time =", obj.data, dt_string)
    
    #Capture d'un appui de touche sur le clavier
    key = cv2.waitKey(1)
    if key == 27:    # 27 code ascci touche "echap"
        cap.release()
        cv2.destroyWindow("Frame")
        break



# conda install opencv
# pip install pyzbar

# https://www.sqlshack.com/python-scripts-to-format-data-in-microsoft-excel/