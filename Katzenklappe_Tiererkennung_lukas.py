from gpiozero import MotionSensor
import shutil
import picamera
from time import sleep
from datetime import datetime
import os
from moviepy.editor import VideoFileClip
import numpy as np
import tflite_micro_runtime.interpreter as tflite
from PIL import Image

folder_path = '/home/klaule/Videos/'


if not os.path.exists(folder_path):
    os.makedirs(folder_path)

pir = MotionSensor(23, threshold=0.5)

def wait_for_file(file_path):
    while not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        sleep(0.5)  # Wait for half a second
        print(os.path.getsize(file_path))


def video_shows_cat(video_path, interpreter, input_details, output_details, recording_time, interval = 1):
    # Video laden:
    clip = VideoFileClip(video_path)

    # fuer jedes bild im Interval 1 pro Sekunde testen, ob eine Tierklasse zu sehen ist.
    for i in range(0, int(recording_time), interval):
        print(f"Checking image at time {i} seconds")
        
        frame = clip.get_frame(i)
        image = Image.fromarray(frame).resize((224, 224))
        image = np.array(image, dtype=np.float32)  # Normalize the image
        image = np.expand_dims(image, axis=0)


        # Set the tensor to point to the input data to be inferred
        interpreter.set_tensor(input_details[0]['index'], image)

        interpreter.invoke()

        # klassifizierung durchfuehren
        predictions = interpreter.get_tensor(output_details[0]['index'])
        print(np.argsort(predictions[0])[-3:][::-1])

        # Katzenklassen aus ImageNet
        animal_class_ids = [281, 282, 283, 284, 285, 286, 287]
        top_predictions = np.argsort(predictions[0])[-3:][::-1]
        # wenn Bild einem Tier aehnelt dann gebe True zurueck sonst gebe False zurueck
        for class_id in top_predictions:
            if class_id in animal_class_ids:
                return True

    return False


def main():
    # Aufnahme Dauer Festlege: 
    recording_time = 5
    # laden des tensorflow light models:
    interpreter = tflite.Interpreter(model_path="/home/klaule/Documents/Programme/mobilenetv3_small.tflite")
    interpreter.allocate_tensors()

    # Input und Output Details von geladenene modell auslesen:
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print("Starting Programm Katzenklappe Lukas ;)")
    with picamera.PiCamera() as camera:
    
        # vorbereitung der kamera
        camera.resolution = (640, 480)
        camera.framerate = 30
        # kamera um 180 drehen
        camera.rotation = 180
          
        while True:
            
            pir.wait_for_motion()
            print("Bewegung erkannt")

            # generiere dateiname basierend auf dem aktuellen datum und uhrzeit
            date_string = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{date_string}"

            # aufnahme starten
            camera.start_recording(os.path.join(folder_path, f"{filename}.h264"))
            # 5 sekunden aufnahme machen
            camera.wait_recording(recording_time)  


            # aufnahme stoppen
            camera.stop_recording()

            # warten bis video vollstaendig gespeichert wurde!
            wait_for_file(os.path.join(folder_path, f"{filename}.h264"))
            # konvertiere .h264 file zu .mp4 file:
            os.system(f"MP4Box -add {os.path.join(folder_path, filename)}.h264 {os.path.join(folder_path, filename)}.mp4")
            # loesche altes .h264 file und behalte .mp4 file:
            os.remove(os.path.join(folder_path, f"{filename}.h264"))
            
            filename = f"{filename}.mp4"             
            
            print(f"Video {filename} gespeichert")
            # Tiererkennung durchfuehren:
            if video_shows_cat(os.path.join(folder_path, filename), interpreter, input_details, output_details, recording_time):
                # fals Katze im Video --> Verschiebe Video in Katzen Ordner
                print("Katze eraknnt!")
                os.makedirs(os.path.join(folder_path, "Katze"), exist_ok=True)
                shutil.move(os.path.join(folder_path, filename), os.path.join(folder_path, "Katze", filename))
            else:
                # fals Katze nicht im Video --> Verschiebe Video in Leer Ordner
                print("Keine Katze eraknnt!")
                os.makedirs(os.path.join(folder_path, "Leer"), exist_ok=True)
                shutil.move(os.path.join(folder_path, filename), os.path.join(folder_path, "Leer", filename))


if __name__ == "__main__":
    main()
