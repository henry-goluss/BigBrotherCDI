import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
import datetime
import time
from pydub import AudioSegment
from pydub.playback import play



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

def add_to_db(id_e,timestamp,database):
    print(id,timestamp)

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
            add_to_db(id_eleve, alreadyScanned[id_eleve],"passages_CDI.db")

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