import pygame
from Text import *
from Status_bar import *
from Display import *
pygame.init()

BACKGREY = (150, 150, 150)
status_font = pygame.font.SysFont('arial', 12, True)
PANELGREY = (210, 210, 210)

# Panel class that creates a panel for the display. Lets you put elements upon the panel.
class Panel:
    # Panel class that creates a panel for the display. Lets you put elements upon the panel. 
    def __init__(self, x_position:int, y_position:int, width:int, height:int, has_tab:bool, tab_label:str, tab_width:int):
        self.surf = pygame.surface.Surface((width, height))
        self.rect = self.surf.get_rect()
        self.surf.fill(BACKGREY)
        self.x_position = x_position
        self.y_position = y_position
        self.width = width
        self.height = height
        self.has_tab = has_tab
        self.tab_label = tab_label
        self.tab_width = tab_width
        self.tab_surf = pygame.surface.Surface((tab_width, 20))
        self.tab_surf.fill(BACKGREY)

        self.label_text = status_font.render(self.tab_label, True, 'black')
        self.text_rect = self.label_text.get_rect(center=self.tab_surf.get_rect().center)

        self.elements = [] # elements are appended to this list to be apart of the panel

    def draw(self, surface:pygame.Surface):
        surface.blit(self.surf, (self.x_position, self.y_position))
        pygame.draw.rect(self.surf, PANELGREY, self.rect, 0, 3)
        if self.has_tab:
            surface.blit(self.tab_surf, (self.x_position, self.y_position - 15))
            pygame.draw.rect(self.tab_surf, PANELGREY, self.tab_surf.get_rect(), 0, 2, 2, 2, 0, 0)
            self.tab_surf.blit(self.label_text, self.text_rect)
        else:
            self.surf.blit(self.label_text, self.rect.topleft)
        for element in self.elements:
            element.draw()

    @staticmethod
    def draw_panels(surface:pygame.Surface, panels:list):
        for panel in panels:
            panel.draw(surface)
    
    @staticmethod
    def get_panel(chosen_panel:str, panels:list) -> object:
        for panel in panels:
            if panel.tab_label == chosen_panel:
                return panel
        print('Object Panel not found.')

    def get_element(self, element_name:str) -> object:
        for element in self.elements:
            if element_name == element.label:
                return element
        print ('Element not found!')
    
    @staticmethod
    def init_panels() -> list:
        panels = [
            Panel(10, 30, 440, 330, True, 'Navigation Console', 100), 
            Panel(455, 30, 192, 225, True, 'Science Console', 100),
            Panel(656, 50, 655, 385, True, 'Primary Display', 100),
            Panel(1330, 30, 440, 60, True, 'Status Indicators', 100),
            Panel(451, 265, 197, 170, False, 'Navigation', 0),
            Panel(10, 361, 475, 225, False, 'Star Map', 0),
            Panel(1330, 110, 580, 260, True, 'Computer Display', 100),
            Panel(490, 455, 160, 135, True, 'Data', 50),
            Panel(660, 455, 655, 550, True, 'Combat Console', 100),
            Panel(1330, 390, 580, 350, True, 'Stratigic Command Console', 150),
            Panel(10, 605, 640, 240, True, 'Engineering Console', 120),
            Panel(10, 865, 640, 205, True, 'Communication Console', 120),
            Panel(1330, 760, 330, 310, True, 'Security Console', 100),
            Panel(1670, 760, 240, 310, True, 'Commanders Log', 100)
        ]

        # Init all elements in each panel
        primary_display = Panel.get_panel('Primary Display', panels)
        # inits elements on primary display panel.
        Video_display('primary display', (645, 320), primary_display, (5, 5)).set_videos([r'assets/DeepSpace.mp4', r'assets/EarthOrbit.mp4'])
        Text('MnsElpTime:', primary_display, (5, 350), 'arial', 12)
        Panel_bar('15.24 Days', (50, 50, 50), (80, 20), primary_display, (65, 345), 'green', 15, 0, 0)
        Text('Time Left:', primary_display, (160, 350), 'arial', 12)
        Panel_bar('5.26 Days', (50, 50, 50) ,(80, 20) ,primary_display, (205, 345), 'green', 15, 0, 0)
        Panel_bar('Button', (230, 230, 230), (60, 20), primary_display, (305, 335), 'black', 15, 1, 0)
        Panel_bar('Button', (50, 50, 50), (60, 20), primary_display, (305, 360), 'white', 15, 1, 0)
        Panel_bar('Status:\nGreen', 'green', (80, 40), primary_display, (550, 335), 'black', 15, 3, 1)

        science_console = Panel.get_panel('Science Console', panels)
        # init elements in Science Console.
        CircleDisplay('sights display', (5, 20), science_console, 90)
        Text('LRS', science_console, (2, 3), 'arial',12)
        Panel_bar('SRS', BACKGREY, (30, 15), science_console, (160, 2), 'black',11, 1, 0)
        Panel_bar('Dept Q',BACKGREY, (70, 13), science_console, (2, 209), 'black', 11, 1, 0)
        Panel_bar('Planet Data',BACKGREY, (70, 13), science_console, (120, 209), 'black', 11, 1, 0)
        # init Navigation Console elements
        navigation_console = Panel.get_panel('Navigation Console', panels)
        Display('planet orbit', (210,210), navigation_console, (5, 20))
        Display('solor system', (210,210), navigation_console, (225, 20))
        Display('status screen 1', (210,80), navigation_console, (5,245))
        Display('status screen 2', (210,80), navigation_console, (225,245))
        Panel_bar('Objects', BACKGREY, (60,13), navigation_console, (5, 231), 'black', 11, 0, 0)
        Panel_bar('Orbit Zones', BACKGREY, (60,13), navigation_console, (61, 231), 'black', 11, 0, 0)
        Panel_bar('Mercator Map', BACKGREY, (60,13), navigation_console, (121, 231), 'black', 11, 0, 0)
        Text('Orbital Displays', navigation_console, (5,5), 'arial', 11)
        Text('System Map', navigation_console, (225,5), 'arial', 11)
        Text('Planets', navigation_console, (310,230), 'arial', 11)

        # init Navigation elements
        navigation = Panel.get_panel('Navigation', panels)
        Display('navigation', (192,72), navigation, (2, 20))
        Display('navigation 2', (159,70), navigation, (35,92))

        # init Star Map elements
        star_map = Panel.get_panel('Star Map', panels)
        Display('star map', (465,200), star_map, (5,20))
        Panel_bar('Mercator Map', BACKGREY, (60,13), star_map, (270,5), 'black', 11, 0,0)
        Panel_bar('Nav Map', BACKGREY, (60,13), star_map, (331,5), 'black', 11, 0,0)
        Panel_bar('War Map', BACKGREY, (60,13), star_map, (392,5), 'black', 11, 0,0)

        # init Data elements
        data = Panel.get_panel('Data', panels)
        Display('data display', (150, 120), data, (5, 10))

        # init engineering console
        engineering_console = Panel.get_panel('Engineering Console', panels)
        Display('probes control', (380,90),engineering_console, (5,25))
        Display('energy display', (380,90),engineering_console, (5,145))
        Display('ship & speed status', (250,210), engineering_console, (386,25))
        Panel_bar('Operations',BACKGREY,(80,15),engineering_console,(220,8),'black',12,0,0)
        Panel_bar('Launch',BACKGREY,(80,15),engineering_console,(301,8),'black',12,0,0)
        Panel_bar('SPD','green',(30,20),engineering_console,(320,120),'black',11,0,0)
        Panel_bar('TB','magenta',(30,20),engineering_console,(353,120),'black',11,0,0)
        Text('Probes Control', engineering_console, (5,8), 'arial', 12)
        Text('DAMAGE - Ship Display', engineering_console, (385,8), 'arial', 12)
        Text('Velocity',engineering_console, (550,8),'arial', 12)
        Text('Energy',engineering_console, (5,125),'arial',12)

        # init communication console
        communication_console = Panel.get_panel('Communication Console', panels)
        Display('status',(315,175),communication_console,(5,25))
        Display('status',(310,175),communication_console,(325,25))
        Text('Status',communication_console,(5,9),'arial',12)
        Panel_bar('CMF','palegreen3',(30,13),communication_console,(290,10),'black',12,0,0)
        Panel_bar('Messages',BACKGREY,(60,13),communication_console,(325,10),'black',12,0,0)
        Panel_bar('Reports',BACKGREY,(60,13),communication_console,(386,10),'black',12,0,0)
        Panel_bar('Combined',BACKGREY,(60,13),communication_console,(447,10),'black',12,0,0)
        Panel_bar('Send Message',BACKGREY,(75,13),communication_console,(508,10),'black',12,0,0)

        # init combat console.
        combat_console = Panel.get_panel('Combat Console',panels)
        Display('combat console', (470,470),combat_console,(5,25))
        Display('weapons',(165,120),combat_console,(485,35))
        Display('shields & target data',(165,335),combat_console,(485,160))
        Panel_bar('BCS',BACKGREY,(25,15),combat_console,(420,5),'black',11,0,0)
        Panel_bar('SCS',BACKGREY,(25,15),combat_console,(450,5),'black',11,0,0)
        Panel_bar('Menu',BACKGREY, (40,20),combat_console,(40,510),'black',11,0,0)
        Panel_bar('Grid',BACKGREY, (40,20),combat_console,(90,510),'black',11,0,0)
        Panel_bar('Head',BACKGREY, (40,20),combat_console,(140,510),'black',11,0,0)
        Panel_bar('Target',BACKGREY, (40,20),combat_console,(190,510),'black',11,0,0)
        Panel_bar('Line',BACKGREY, (40,20),combat_console,(240,510),'black',11,0,0)
        Text('Combat Information Display',combat_console,(5,5),'arial',11)
        Text('Alignment',combat_console,(370,5),'arial',11)
        Text('Weapons',combat_console,(485,20),'arial',11)

        #init Status indicators
        status_indicators = Panel.get_panel('Status Indicators',panels)
        x = 10
        for i in range(5):
            Text(str(i+1),status_indicators,(x+16,2),'arial',11)
            Panel_bar('','green',(40,12),status_indicators,(x,15),'black',0,0,0)
            x += 60
        x = 10
        for i in range(5):
            Text(str(i+6),status_indicators,(x+16,28),'arial',11)
            Panel_bar('','green',(40,12),status_indicators,(x,40),'black',0,0,0)
            x += 60
        Panel_bar('\u2640','magenta', (35,20),status_indicators,(310,22),'black',11,0,0)
        Panel_bar('4.8 Ly','black',(50,15),status_indicators,(365,24),'green',12,0,0)
        Text('Distance',status_indicators,(370,10),'arial',11)

        # init computer display
        computer_display = Panel.get_panel('Computer Display',panels)
        Display('computer display',(475,250),computer_display,(100,5))
        Display('computer display options',(90,250),computer_display,(5,5))

        # init Stratigic command console
        stratigic_command_console = Panel.get_panel('Stratigic Command Console',panels)
        Display('escort display',(150,120),stratigic_command_console,(5,10))
        Display('formation', (80,120),stratigic_command_console,(165,10))
        Display('escort fleet',(200, 120),stratigic_command_console,(255,10))
        Display('fleet command',(570,195),stratigic_command_console,(5,150))
        Panel_bar('Escort Commands',BACKGREY,(100,15),stratigic_command_console,(465,10),'black',12,0,0)
        Panel_bar('Fleet Commands',BACKGREY,(100,15),stratigic_command_console,(465,40),'black',12,0,0)
        Panel_bar('Stratigic Commands',BACKGREY,(100,15),stratigic_command_console,(465,70),'black',12,0,0)
        Panel_bar('Menu',BACKGREY,(100,15),stratigic_command_console,(465,100),'black',12,0,0)
        Panel_bar('Editor',BACKGREY,(45,20),stratigic_command_console,(480,130),'black',12,0,0)
        Panel_bar('View',BACKGREY,(45,20),stratigic_command_console,(530,130),'black',12,0,0)

        # init security console
        security_console = Panel.get_panel('Security Console',panels)
        Display('internal security',(320,160),security_console,(5,15))
        Display('prisoner status',(130,100),security_console,(5,205))
        Display('interogations',(165,100),security_console,(160,205))
        Text('Prisoner Status',security_console,(5,185),'arial',12)

        #init commander's log
        commanders_log = Panel.get_panel('Commanders Log',panels)
        Display('commanders log',(230,300),commanders_log,(5,5))

        return panels
    
    def draw_elements(panels:list):
        science_console_display = Panel.get_panel('Science Console', panels).get_element('sights display') # Sights display on science console is drawn onto.
        pygame.draw.line(science_console_display.surf, 'white', (science_console_display.rect.centerx, 0), (science_console_display.rect.centerx, 200), 1)
        pygame.draw.line(science_console_display.surf, 'white', (0, science_console_display.rect.centery), (200, science_console_display.rect.centery), 1)
        for i in range(0 ,science_console_display.rect.centerx * 2, 15):
            pygame.draw.line(science_console_display.surf, 'white', (science_console_display.rect.centerx - 10, i), (science_console_display.rect.centerx + 10, i), 1)
            pygame.draw.line(science_console_display.surf, 'white', (i, science_console_display.rect.centerx - 10), (i, science_console_display.rect.centerx + 10), 1)

    def event_listener(panels:list, events:pygame.event): # listens for all events
        primary = Panel.get_panel('Primary Display', panels)
        display = primary.get_element('primary display')
        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.type == QUIT:
                    for video in display.videos:
                        video.close()
                if event.key == K_n:
                    display.play_video()
        display.update(events)

 