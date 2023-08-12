import pygame
import signal
import sys

def stop_playback(signal, frame):
    pygame.mixer.stop()
    pygame.quit()
    sys.exit(0)

# Register the signal handler for Ctrl + C
signal.signal(signal.SIGINT, stop_playback)

pygame.mixer.init()
sound = pygame.mixer.Sound("alarm.mp3")
sound.play()

try:
    while pygame.mixer.get_busy():
        pygame.time.Clock().tick(10)
except KeyboardInterrupt:
    stop_playback(None, None)
