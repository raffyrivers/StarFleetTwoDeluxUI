import pygame
from pygame.locals import *
import pyvidplayer2

pygame.display.init()
PANELGREY = (210, 210, 210)
class Display:
    def __init__(self, label:str, dimensions:list, panel:object, position:list): # All atributes are initialized before the draw.
        self.label = label # Used for get element method.
        self.position = position
        self.panel = panel
        self.surf = pygame.Surface(dimensions)
        self.rect = self.surf.get_rect()
        self.panel.elements.append(self)
        # Make it so I can draw and update to this display.
        self.elements = []
        
    def draw(self): # Draw with nyo parameters to work with the panel class
        self.panel.surf.blit(self.surf, self.position)
        pygame.draw.rect(self.surf, 'black', self.rect)

    def update(self):
        pass

class CircleDisplay(Display):
    def __init__(self, label:str, position:list, panel:object, radius:int):
        self.label = label
        self.position = position
        self.radius = radius
        self.panel = panel
        self.circumference = radius * 2
        self.surf = pygame.Surface((self.circumference, self.circumference))
        self.rect = self.surf.get_rect()
        self.surf.fill(PANELGREY)
        self.panel.elements.append(self)
        self.elements = []

    def draw(self):
        self.panel.surf.blit(self.surf, self.position)
        pygame.draw.circle(self.surf, 'black', self.rect.center, self.radius, 0)
    
    def eventListener(self, event:pygame.event):
        pass # Do somthing when an event happens

class Video_display(Display):
    def __init__(self, label:str, dimensions:list, panel:object, position:list):
        self.label = label # Used for get_element method in Panel class
        self.dimensions = dimensions
        self.panel = panel
        self.position = position
        self.surf = pygame.Surface(self.dimensions)
        self.rect = self.surf.get_rect()
        self.panel.elements.append(self)

        self.videos = [] # Videos that will be played
        self.playing = 0 # Will play whaever video is at this position in videos.
        
        self.showCircles = False # move this back into 'Display.py' --> navigation console 
        
        self.nav_videos = [r'assets/mmn.mp4', ]
        self.using_nav_videos = False
        self.nav_video_players = []

    def set_videos(self, videos:list): # assign different videos to different displays.
        for video in videos:
            raw_vid = pyvidplayer2.Video(video)
            raw_vid.stop() # Sets active to False when initializing the videos.
            self.videos.append(pyvidplayer2.VideoPlayer(raw_vid, self.rect,loop=True))

    def get_videos(self) -> list:
        return self.videos
   
    def play_video(self):
        length = len(self.get_active_video_list())
        if length == 0:
            print("No videos available.")
            return
        self.playing = (self.playing + 1) % length
   
    def get_active_video_list(self):
        return self.nav_video_players if self.using_nav_videos else self.videos

    def use_nav_videos(self, use=True):
        self.using_nav_videos = use
        self.playing = 0  
    
    def load_nav_videos(self):
        self.nav_video_players.clear()
        for video in self.nav_videos:
            raw_vid = pyvidplayer2.Video(video)
            raw_vid.stop()
            self.nav_video_players.append(pyvidplayer2.VideoPlayer(raw_vid, self.rect, loop=True))
        self.using_nav_videos = True
        self.playing = 0
    
    def reset_to_main_videos(self):
        self.using_nav_videos(False)
        self.playing = 0

    def update(self, events:pygame.event):
        video_list = self.get_active_video_list()
        if self.playing >= len(video_list):
            self.surf.fill('black')
        else:
            video_list[self.playing].draw(self.surf)
            video_list[self.playing].update(events)
#            video_list[self.playing].draw(self.surf)
 #           video_list[self.playing].update(events)
            #self.videos[self.playing].draw(self.surf)
            #self.videos[self.playing].update(events)
            
