from gtts import gTTS
import pygame
import time
import os

def speak_gtts(text: str, lang: str = "de", filename: str = "tts.mp3") -> None:
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # warten bis fertig
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.quit()

    # optional: Datei wieder löschen
    try:
        os.remove(filename)
    except OSError:
        pass

if __name__ == "__main__":
    speak_gtts("Das ist ein Test.", "de")
    speak_gtts("I'm an alian from New York.", "en")
    speak_gtts("Parlo Italiano e anche altre lingue", "it")
    speak_gtts("как дела?", "ru")
