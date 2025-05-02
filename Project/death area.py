import pygame
import sys
import os
import subprocess

pygame.init()

# Fullscreen setup
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("DEATH")

clock = pygame.time.Clock()

GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
line_y = HEIGHT // 2
line_speed = 10
step = 0

# Pattern: flat → dip → spike → drop → flat — repeated 5x, then flatline
spike_pattern = [0, 0, 0, -40, 100, -100, 0, 0, 0, 0]
flatline_pattern = [0] * 50
waveform = spike_pattern * 5 + flatline_pattern

ekg_x = 0
points = []

# The script to run after 15 seconds:
NEXT_SCRIPT = 'Maze.py'  # ← replace with your target file

# Record when we started
start_time = pygame.time.get_ticks()
launched = False

running = True
while running:
    dt = clock.tick(15)
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type in (pygame.QUIT, pygame.KEYDOWN):
            running = False

    # After 15 seconds, launch the next script once
    if not launched and now - start_time >= 15000:
        launched = True
        pygame.quit()
        # Build absolute path to the next script
        next_path = os.path.join(os.path.dirname(__file__), NEXT_SCRIPT)
        subprocess.Popen([sys.executable, next_path])
        sys.exit()  # ensure this script exits immediately

    # Generate waveform
    if step < len(waveform):
        dy = waveform[step]
    else:
        dy = 0  # stay flat
    new_y = line_y + dy
    points.append((ekg_x, new_y))
    ekg_x += line_speed
    step += 1

    # Scroll off screen then hold flatline
    if ekg_x > WIDTH:
        ekg_x = 0
        points = []
        step = len(waveform)  # go straight to flatline

    # Draw
    screen.fill(BLACK)
    if len(points) > 1:
        pygame.draw.lines(screen, GREEN, False, points, 3)
    pygame.display.flip()

pygame.quit()
sys.exit()