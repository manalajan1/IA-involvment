import sounddevice as sd
import numpy as np
import os

def clear_console_line():
    print(" " * 80, end="\r")  # efface la ligne précédente

def print_audio_level(indata, frames, time, status):
    volume_norm = np.linalg.norm(indata) * 10
    bar_length = min(int(volume_norm), 50)  # limite la taille max de la barre
    bar = "|" * bar_length
    clear_console_line()
    print(f"Volume: {bar}", end="\r")

print("Test du niveau sonore du micro")

with sd.InputStream(callback=print_audio_level):
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nTest terminé.")