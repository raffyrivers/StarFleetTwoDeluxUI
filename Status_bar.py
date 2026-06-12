# Status_bars class that shows the status of somthing
import pygame
from pygame.locals import *
pygame.font.init()
pygame.display.init()

status_font = pygame.font.SysFont('arial', 12, True)
large_status_font = pygame.font.SysFont('arial', 16)
BACKGREY = (150, 150, 150)
PANELGREY = (210, 210, 210)
labels = ['LowPwr', 'LowSup', 'LowTime','Medical', 
    'SecAlt', 'Mines', 'Distress', 'HullPn']
labels2 = ['NAV', 'ENG', 'CMB', 'CMP', 'SEC', 'COM', 'STG', 'SCI', 'CTL']
class Status_bar(pygame.sprite.Sprite):
    def __init__(self, color:tuple, label:str):
        pygame.sprite.Sprite.__init__(self)
        self.surf = pygame.surface.Surface((80, 20))
        self.bottom_surf = pygame.surface.Surface((71, 20))
        self.surf.fill(BACKGREY)
        self.rect = self.surf.get_rect()
        self.rect2 = self.bottom_surf.get_rect()
        self.color = pygame.Color(color)
        self.og_color = color
        self.label = label
        self.isRed = False
        self.highlight_index = None

    def _draw_label(self, surf:pygame.Surface, rect:pygame.Rect, highlight_index:int | None):
        total_width = sum(status_font.size(char)[0] for char in self.label)
        x_offset = (rect.width - total_width) // 2
        y_offset = (rect.height - status_font.get_height()) // 2

        for index, char in enumerate(self.label):
            char_color = pygame.Color('red') if highlight_index == index else pygame.Color('black')
            char_surf = status_font.render(char, True, char_color)
            surf.blit(char_surf, (x_offset, y_offset))
            x_offset += char_surf.get_width()

    def draw(self, surface:pygame.Surface, x_position:int, y_position:int, boarder_radius:int):
        pygame.draw.rect(self.surf, self.color, self.rect, 0, boarder_radius)
        self._draw_label(self.surf, self.rect, self.highlight_index)
        surface.blit(self.surf, (x_position, y_position))
        x_position += 82
    def draw2(self, surface:pygame.Surface, x_position:int, y_position:int, boarder_radius:int):
        pygame.draw.rect(self.bottom_surf, self.color, self.rect2, 0, boarder_radius)
        self._draw_label(self.bottom_surf, self.rect2, self.highlight_index)
        surface.blit(self.bottom_surf, (x_position, y_position))
        x_position += 73

    def init_status_bars() -> list:
        bars = []
        for label in labels:
            bars.append(Status_bar('grey', label))
        return bars
    def init_menu_bars() -> list:
        bars2 = []
        for label in labels2:
            bars2.append(Status_bar('grey', label))
        return bars2

    def event_listener(bars:list, event:pygame.event):
        if event.key == K_1: # num keys from 1-8 will change the color of the top status bars to red.
            bars[0].change_color('red')
        elif event.key == K_2:
            bars[1].change_color('red')
        elif event.key == K_3:
            bars[2].change_color('red')
        elif event.key == K_4:
            bars[3].change_color('red')
        elif event.key == K_5:
            bars[4].change_color('red')
        elif event.key == K_6:
            bars[5].change_color('red')
        elif event.key == K_7:
            bars[6].change_color('red')
        elif event.key == K_8:
            bars[7].change_color('red')
    
    def draw_bars(surface:pygame.Surface, bars:list, x_position:int, y_position:int, bars2:list):
        label_x = x_position
        for bar in bars:
            bar.draw(surface, label_x, y_position, 2)
            label_x += 82
        label_x = x_position
        for bar in bars2:
            bar.draw2(surface, label_x, 1050, 2)
            label_x += 73
            

    def change_color(self, color:tuple):
        if self.isRed:
            self.color = self.og_color
        else:
            self.color = color    
        self.isRed = not self.isRed

    def set_highlight_letter(self, index:int | None):
        if index is None or index < 0 or index >= len(self.label):
            self.highlight_index = None
        else:
            self.highlight_index = index

    def sequence_flash(bars:list):
        time = pygame.time.get_ticks() % 800 
        bar_index = time // 100 # Determine which bar should be green 
        for i in range(8): 
            if i == bar_index: 
                bars[i].color = 'green' 
            elif i == (bar_index - 1) % 8: 
                bars[i].color = bars[i].og_color
        for bar in bars:
            if bar.isRed:
                bar.color = 'red'

 
class Panel_bar(Status_bar): # These will act as button place holders
    def __init__(self, label:str, color:tuple, dimensions:list, panel:object, 
        position:list, text_color:tuple, text_size:int, boarder_radius:int, text_position:int):
            
        self.surf = pygame.surface.Surface(dimensions)
        self.surf.fill(PANELGREY)
        self.rect = self.surf.get_rect()
        self.label = label # Used for get_element method
        self.color = pygame.Color(color)
        self.dimensions = dimensions

        self.panel = panel
        self.position = position
        self.text_color = text_color
        self.text_size = text_size
        self.boarder_radius = boarder_radius
        self.panel.elements.append(self)
        self.text_position = text_position # 1 is top left of rect 0 is center
        self.font = pygame.font.SysFont('arial', self.text_size, False)
        
    def draw(self):
        pygame.draw.rect(self.surf, self.color, self.rect, 0, self.boarder_radius)
        text_surf = self.font.render(self.label, True, pygame.Color(self.text_color))
        text_rect = text_surf.get_rect(center=self.rect.center)
        if self.text_position == 0:
            self.surf.blit(text_surf, text_rect)
        elif self.text_position == 1:
            self.surf.blit(text_surf, self.rect.topleft)
        self.panel.surf.blit(self.surf, self.position)

    def update(self):
        pass
