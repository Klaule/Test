from gpiozero import MotionSensor
import picamera
from time import sleep
from datetime import datetime
import os

# Pfad des Zielordners
folder_path = "/home/klaule/Videos/"

if not os.path.exists(folder_path):
    
    os.makedirs(folder_path)

pir = MotionSensor(23, queue_len=2, threshold=0.7)  #an GPIO17 angeschlossen, Empindlichkeit 50%



with picamera.PiCamera() as camera:
    while True:
        pir.wait_for_motion()
        print("Bewegung erkannt")
        
        # Generiere Datenname basierend auf dem aktuellen Datum und Uhrzeit
        date_string = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{date_string}.h264"
        # Camera um 180 Grad drehen
        camera.rotation = 180
        
        # camera.zoom = (0.0, 0.0, 1.0, 1.0)
        #Starte Aufnahme
        camera.start_recording(os.path.join(folder_path, filename))
        sleep(5)  # Aufnahmezeit von 5 Sekunden
        camera.stop_recording()
        
        print(f"Video {filename} gespeichert")
        
        # Warte bis die Bewegung aufhrt bevor du nach der nchsten Bewegung suchst
        pir.wait_for_no_motion()
        
        
        
        
        
        
        
        

