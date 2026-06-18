from Panel import *
from Status_bar import *
import pygame
from pygame.locals import *


'''
*****************Documentation*****************
 11/30/24   All Panels are initialized and drawn.
 12/10/24   Drew status bars to screen. 
 12/30/24   Each status bar is now listening for events to turn red.
 1/6/25   Added Panel_bar class into Status_bar.py file and drew all elements on primary display
 1/16/25    Primary Panel d key plays deepspace video and o plays the orbit video
 1/24/25    Video_display.py plays videos for Video_display objects see class for specifics.
 
 **********************************************
'''
pygame.init()
clock = pygame.time.Clock()

ORIGINAL_SCREEN_SIZE = [1920, 1080]
WINDOWED_SIZE = [1680, 945]
FPS = 60

def main():
    pygame.display.set_caption('StarFleet2DeluxDEMO')

    display = pygame.display.set_mode((0,0), FULLSCREEN|HWSURFACE|DOUBLEBUF)
    display_rect = display.get_rect()
    canvas = pygame.Surface(ORIGINAL_SCREEN_SIZE).convert()# Everything is drawn on canvas to allow for scaling
    canvas_rect = canvas.get_rect()

    # initializes status bars for the top of the screen.
    top_bars = Status_bar.init_status_bars()
    bottom_bars = Status_bar.init_menu_bars()
    bottom_bars[0].set_highlight_letter(0)
    bottom_bars[1].set_highlight_letter(0)  
    bottom_bars[2].set_highlight_letter(2)
    bottom_bars[3].set_highlight_letter(0)
    bottom_bars[4].set_highlight_letter(0)
    bottom_bars[5].set_highlight_letter(2)
    bottom_bars[6].set_highlight_letter(2)
    bottom_bars[7].set_highlight_letter(2)
    bottom_bars[8].set_highlight_letter(2)
    notepad_bar = Status_bar('grey', 'NotePad')
    panels = Panel.init_panels() # Panels and elements are init
    isFullscreen = True
    running = True
    while running:
        events = pygame.event.get()
        for event in events: 
            if event.type == KEYDOWN:
                if event.key == K_F11:
                    if isFullscreen:
                        display = pygame.display.set_mode(WINDOWED_SIZE, HWSURFACE|DOUBLEBUF)
                    else:
                        display = pygame.display.set_mode(ORIGINAL_SCREEN_SIZE, HWSURFACE|DOUBLEBUF|FULLSCREEN)
                    display_rect = display.get_rect()
                    isFullscreen = not isFullscreen
                    break
                Status_bar.event_listener(top_bars, event)
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
                break
        Panel.event_listener(panels, events)
        Status_bar.sequence_flash(top_bars) # Sequentially flashes each status bar.
        canvas.fill(BACKGREY)
        Panel.draw_panels(canvas, panels) # Draws each panel to the screen.
        Status_bar.draw_bars(canvas, top_bars, 660, 10,bottom_bars, notepad_bar) # draws top canvas status bars
        Panel.draw_elements(panels)


        if display_rect != ORIGINAL_SCREEN_SIZE: # Auto adjust all elements on the window to fit.
            canvas_rect = canvas_rect.fit(display_rect)
            canvas_rect.center = display_rect.center
            scaled_canvas = pygame.transform.smoothscale(canvas, canvas_rect.size)
            display.blit(scaled_canvas, canvas_rect)
        else:
            display.blit(canvas, (0,0))
        clock.tick(FPS)
        pygame.display.flip()

main()
