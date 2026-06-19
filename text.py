import pygame
pygame.font.init()
pygame.display.init()
class Text:
    def __init__(self, label:str, panel:object, position:list, font:str, font_size:int, color:str):
        self.label = label # You can get a text element by searching what is in the text.
        self.panel = panel
        self.position = position
        self.font = font
        self.font_size = font_size
        self.desc_font = pygame.font.SysFont(self.font, self.font_size, False) 
        self.text_surf = self.desc_font.render(self.label, True, pygame.Color(color))
        self.panel.elements.append(self)

    def draw(self):
        self.panel.surf.blit(self.text_surf, (self.position[0], self.position[1]))
