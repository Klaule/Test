import RPi.GPIO as GPIO
import time

pir_pin = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(pir_pin, GPIO.IN)

try:
    print("Warte auf Bewegung...")
    while True:
        if GPIO.input(pir_pin):
            print("Bewegung erkannt")
            
        time.sleep(1)
        
except KeyboardInterrupt:
    print("Programm wurde beendet.")
    GPIO.cleanup()