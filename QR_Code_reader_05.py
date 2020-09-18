import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
from datetime import datetime
import time
import winsound

frequency = 1500  # Set Frequency To 2500 Hertz
duration = 250  # Set Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)
frequency = 2500  # Set Frequency To 2500 Hertz

cap = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_PLAIN
oldData = ""
while True:

    #Pour éviter trop de charge CPU
    time.sleep(0.5)
    
    _, frame = cap.read()
    cv2.imshow("Frame", frame)
    decodedObjects = pyzbar.decode(frame)

    for obj in decodedObjects:
        Data = obj.data
        if Data != oldData:
            oldData = Data
            winsound.Beep(frequency, duration)
            #print("Data", obj.data)
            cv2.putText(frame, str(obj.data), (50, 50), font, 2,
                        (255, 0, 0), 3)
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print("date and time =", dt_string)
            print("Data + date and time =", obj.data, dt_string)

            your_data1 = {obj.data, dt_string}
            print(your_data1,  file=open('C:\log.txt', 'a'))





    key = cv2.waitKey(1)
    if key == 27:    # 27 code ascci touche "echap"
        cap.release()
        cv2.destroyWindow("Frame")
        break



# conda install opencv
# pip install pyzbar

# https://www.sqlshack.com/python-scripts-to-format-data-in-microsoft-excel/