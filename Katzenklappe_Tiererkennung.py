from gpiozero import MotionSensor
import time
import picamera
from time import sleep
from datetime import datetime
import os
from moviepy.editor import VideoFileClip
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions

folder_path = 'home/klaule/Videos/'

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

pir = MotionSensor(23, threshold=0.5)

#laden des vortrainierten MobileNetV2-Modells
model = MobileNetV2(weights='imagenet')

def classify_image(image):
    #bild für MobileNetV2 vorverarbeiten.
    image = cv2.resize(image,(224, 224))
    image = preprocess_input(image)
    image = np.expand_dims(image,axis=0)
    
    #klassifizierung durchführen
    predictions = model.predict(image)
    
    #tierklassen-id aus ImageNet
    animal_class_ids = [16, 22, 27, 31, 32, 33, 49,50, 51]
    
    #überprüfen, ob eine Tierklasse in den top-3 vorhersagen vorhanden ist.
    top_predictions = decode_predictions(predictions, top3)[0]
    for _, _, class_id in top_predictions:
        if class_id in animal_class_ids:
            return True
        
    return False

def main():
    with picamera.PiCamera() as camera:
        while True:
            pir.wait_for_motion()
            print("Bewegung erkannt")
            
            #generiere dateiname basierend auf dem aktuellen datum und uhrzeit
            date_string = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{date_string}.h264"
            
            
         #vorbereitung der kamera
        camera.resolution = (640, 480)
        camera.framerate = 30
        #kamera um 180 drehen
        camera.rotation = 180
        
        #aufnahme starten
        camera.start_preview()
        camera.start_recording(os.path.join(folder_path, filename))
        
        #video aufnahme 5s
        sleep(5)
        
        #aufnahme stoppen
        camera.stop_recording()
        
        #videodatei in OpenCV-Format konvertieren
        video_capture = cv2.VideoCapture(filename)
        
        #franes durchgehen und tiererkennung durchführen
        while True:
            ret, frame = video_capture_read()
            if not ret:
                break
            
            #tiererkennung durchführen
            if classify_image(frame):
                print("Tier erkannt! Speichere Video ab.")
                
                #code zum speichern des video mit tier
                video_filename = ("Tier Video" + filename)
                break
            
        #aufräumen
        video_capture.release(folder_path, video_filename)
        cv2.destroyAllWindows()
        
if __name__ == "__main__":
    main()
       
    
