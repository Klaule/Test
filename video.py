
import picamera
import time

with picamera.PiCamera() as camera:
    camera.resolution = (1024, 768)  # Adjust the resolution as needed
    camera.start_preview()
    # Camera warm-up time
    time.sleep(2)
    camera.start_recording('video.h264')  # Path to save video
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        camera.stop_recording()
        camera.stop_preview()
        

        
        
        