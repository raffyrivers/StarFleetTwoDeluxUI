import pygame
import math
from Text import *
from Status_bar import *
from Display import *
import os
pygame.init()

lastTime = 0 # <---------- USE FOR ANY TIMED EVENTS!!!
BACKGREY = (150, 150, 150)
status_font = pygame.font.SysFont('arial', 12, True)
PANELGREY = (210, 210, 210)
PANELGREYDARK = (180, 180, 180) # this is slightly darker than panelgrey, and is used as the background color for 'combat console' --> 'weapons', 'shields', etc
ALTPANELGREY = (50, 50, 50) # this is the very dark grey, which is used for data displays as seen in 'Data', 'Navigation', etc
BUTTONPRESSED = (115,115,115)
ship_dmg_display = pygame.image.load(r'assets/shipdmg.png')
combatCShldShip = pygame.image.load(r'assets/babaaa 2.png')
buttonBoard = pygame.image.load(r'assets/tempBoardResize.png') # should manually redraw this later, but this is going to an image because of of time's sake 
mainDispShip = pygame.image.load(r'assets/combcShip.png')
nav_map_png = pygame.image.load(r'assets/NavMap.png')
war_map_png = pygame.image.load(r'assets/WarMap.png')
# fonts 
txt_font = pygame.font.SysFont('arial', 12, True); txt_font_small = pygame.font.SysFont('arial', 10, True); txt_font_medium = pygame.font.SysFont('arial', 11, True); 
txt_font_combatC = pygame.font.SysFont('arial', 30, True); txt_font_very_small = pygame.font.SysFont('arial', 7, True); 

# for UI toggles via key press, check bottom of script or wherever key presses are handled
    # navigation console --> orbit data
toggle_i = {'val': False}; pressed_i = {'pressed': False}
toggle_o = {'val': False}; pressed_o = {'pressed': False}
toggle_p = {'val': False}; pressed_p = {'pressed': False}
    # nav con --> star map
toggle_l = {'val': False}; pressed_l = {'pressed': False}
toggle_sCol = {'val': False}; pressed_sCol = {'pressed': False}
toggle_quo = {'val': False}; pressed_quo = {'pressed': False}
    # engineering console --> probes
toggle_q = {'val': False}; pressed_q = {'pressed': False}
toggle_w = {'val': False}; pressed_w = {'pressed': False}
    # combat console --> main display 
toggle_d = {'val': False}; pressed_d = {'pressed': False}
toggle_f = {'val': False}; pressed_f = {'pressed': False}
toggle_g = {'val': False}; pressed_g = {'pressed': False}
toggle_h = {'val': False}; pressed_h = {'pressed': False}
toggle_j = {'val': False}; pressed_j = {'pressed': False}
    # combat console --> target data
toggle_rShift = {'val': False}; pressed_rShift = {'pressed': False}

message_index = 0
sub_index = 0
messages = ['message test', 'message test 2', 'message test 3', 'message test', 'message test 2', 'message test 3', 'message test', 'message test 2', 'message test 3', 'message test', 'message test 2', 'message test 3']
sub_messages = ['sub message', 'sub message 2', 'sub message 3']
message_surfs = []
sub_message_surfs = []
reports = ['report test', 'report test 2', 'report test 3']
sub_reports = ['sub reports', 'sub reports 2', 'sub reports 3']
report_surfs = []
sub_report_surfs = []

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
            Panel(1670, 760, 240, 310, True, 'Commanders Log', 100),
            #Panel(660, 150, 330, 50, False, 'Shortcut Keypad', 0)
        ]

        # Init all elements in each panel
        primary_display = Panel.get_panel('Primary Display', panels)
        # inits elements on primary display panel.
        DeepSpace = r'assets/DeepSpace.mp4'; EarthOrbit = r'assets/EarthOrbit.mp4'
        Video_display('primary display', (645, 320), primary_display, (5, 5)).set_videos([DeepSpace, EarthOrbit])
        Text('MnsElpTime:', primary_display, (5, 350), 'arial', 12,'black')
        Panel_bar('15.24 Days', (50, 50, 50), (80, 20), primary_display, (65, 345), 'green', 15, 0, 0)
        Text('Time Left:', primary_display, (160, 350), 'arial', 12,'black')
        Panel_bar('5.26 Days', (50, 50, 50) ,(80, 20) ,primary_display, (205, 345), 'green', 15, 0, 0)
        Panel_bar('REST', (230, 230, 230), (60, 20), primary_display, (305, 335), 'black', 13, 1, 0)
        Panel_bar('Sim Freeze', (50, 50, 50), (60, 20), primary_display, (305, 360), 'white', 13, 1, 0)
        Panel_bar('Status:\nGreen', 'green', (80, 40), primary_display, (550, 335), 'black', 15, 3, 1)

        science_console = Panel.get_panel('Science Console', panels)
        # init elements in Science Console.
        CircleDisplay('sights display', (5, 20), science_console, 90)
        Text('LRS', science_console, (2, 3), 'arial',12,'black')
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
        Text('Orbital Displays', navigation_console, (5,5), 'arial', 11,'black')
        Text('System Map', navigation_console, (225,5), 'arial', 11,'black')
        Text('Planets', navigation_console, (310,230), 'arial', 11,'black')
        navigation_console.navButtonUI1 = False # press i
        navigation_console.navButtonUI2 = False # press o
        navigation_console.navButtonUI3 = False # press p
        nav_display = Panel.get_panel(("Navigation Console"), panels).get_element("Navigation Video")
        nav_display = Video_display("Navigation Video", [420, 210], navigation_console, [5, 330])
        nav_display.set_videos([])
        
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
        star_map.ButtonUI1 = False # press l
        star_map.ButtonUI2 = False # press ;
        star_map.ButtonUI3 = False # press '

        # init Data elements
        data = Panel.get_panel('Data', panels)
        Display('data display', (150, 120), data, (5, 10))

        # init engineering console
        engineering_console = Panel.get_panel('Engineering Console', panels); engC = engineering_console
        Display('probes control', (380,90),engineering_console, (5,25))
        Display('energy display', (380,90),engineering_console, (5,145))
        Display('ship & speed status', (250,210), engineering_console, (386,25))
        Panel_bar('Operations',BACKGREY,(80,15),engineering_console,(220,8),'black',12,0,0)
        Panel_bar('Launch',BACKGREY,(80,15),engineering_console,(301,8),'black',12,0,0)
        Panel_bar('SPD','green',(30,20),engineering_console,(320,120),'black',11,0,0)
        Panel_bar('TB','magenta',(30,20),engineering_console,(353,120),'black',11,0,0)
        Text('Probes Control', engineering_console, (5,8), 'arial', 12,'black')
        Text('DAMAGE - Ship Display', engineering_console, (400,8), 'arial', 12,'black')
        Text('Velocity',engineering_console, (560,8),'arial', 12,'black')
        Text('Energy',engineering_console, (5,125),'arial',12,'black')
        engC.ButtonUI1 = False # press q
        engC.ButtonUI2 = False # press w
        engC.CycleDamage = [1,] # 1 is default, is green or fully functional | 2 is yellow or damaged | 3 is red or heavily damaged | 4 is black or inop/destroyed  # function keys 1-4
        engC.vHypUp = False # press z
        engC.vHypDown = False # press x 
        engC.vSpcUp = False # press c
        engC.vSpcDown = False # press v
        engC.kVal = engC.rect.centery+92; engC.lVal = engC.rect.centery+92
        engC.k = 0; engC.l = 0 # hold values
        engC.vHypBar = [] #meant to store values of 'k' that indicate the starting ypos of something that was drawn 
        engC.vSpcBar = [1,]
        engC.energy_usage = 20; 
        engC.energy_quantity = 94; 
        engC.energy_backup = 100; 
        engC.energy_shields = 58; 
        engC.color = 'green' # color of energy usage bars (fill)
        engC.inc_counter = [1,] # increment counter, hold indexes

        # init communication console
        communication_console = Panel.get_panel('Communication Console', panels)
        Display('status1',(315,175),communication_console,(5,25))
        Display('status2',(310,175),communication_console,(325,25))
        Text('Status',communication_console,(5,9),'arial',12,'black')
        Panel_bar('CMF','palegreen3',(30,13),communication_console,(290,10),'black',12,0,0)
        Panel_bar('Messages',BACKGREY,(60,13),communication_console,(325,10),'black',12,0,0)
        Panel_bar('Reports',BACKGREY,(60,13),communication_console,(386,10),'black',12,0,0)
        Panel_bar('Combined',BACKGREY,(60,13),communication_console,(447,10),'black',12,0,0)
        Panel_bar('Send Message',BACKGREY,(75,13),communication_console,(508,10),'black',12,0,0)
        communication_console.reportsButton = False # press '-'
        communication_console.messageButton = True # press '+'
        communication_console.comboButton = False
        for message in messages: # init messages
            message_surfs.append(txt_font.render(message, True, 'green'))
        for sub in sub_messages:
            sub_message_surfs.append(txt_font.render(sub, True, 'white'))
        for report in reports:
            report_surfs.append(txt_font.render(report, True, 'green'))
        for sub in sub_reports:
            sub_report_surfs.append(txt_font.render(sub, True, 'white'))

        # init combat console.
        combat_console = Panel.get_panel('Combat Console',panels); combatC = combat_console
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
        Text('Combat Information Display',combat_console,(5,5),'arial',11,'black')
        Text('Alignment',combat_console,(370,5),'arial',11,'black')
        Text('Weapons',combat_console,(485,20),'arial',11,'black')
        combatC.actMenu = False # press d
        combatC.actGrid = False # press f
        combatC.actHeading = False  # press g
        combatC.actTarget = False # press h
        combatC.actLine = False # press j
        combatC.weaponIndex = 0
        combatC.weapons = [] # weapons are cycled by left & right arrow keys
        combatC.shldAuto = False # press m
        combatC.shldManual = True # press , | is on by default 
        combatC.shldBattleEntry = False # press . 
        combatC.shldMaximum = False # press /
        combatC.targetBoard = False # press right shift

        #init Status indicators
        status_indicators = Panel.get_panel('Status Indicators',panels)
        x = 10
        for i in range(5):
            Text(str(i+1),status_indicators,(x+16,2),'arial',11,'black')
            Panel_bar('','green',(40,12),status_indicators,(x,15),'black',0,0,0)
            x += 60
        x = 10
        for i in range(5):
            Text(str(i+6),status_indicators,(x+16,28),'arial',11,'black')
            Panel_bar('','green',(40,12),status_indicators,(x,40),'black',0,0,0)
            x += 60
        Panel_bar('\u2640','magenta', (35,20),status_indicators,(310,22),'black',11,0,0)
        Panel_bar('4.8 Ly','black',(50,15),status_indicators,(365,24),'green',12,0,0)
        Text('Distance',status_indicators,(370,10),'arial',11,'black')

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
        Text('Prisoner Status',security_console,(5,185),'arial',12, 'black')

        #init commander's log
        commanders_log = Panel.get_panel('Commanders Log',panels)
        Display('commanders log',(230,300),commanders_log,(5,5))

        # init shortcut key panel + notepad 
        shortcut_keypad = Panel.get_panel('Shortcut Keypad', panels)
        #for i in range(9):
         #   Display('Shortcut Keypad', (50, 30), shortcut_keypad, (0,0))
        navigation_console_display = Panel.get_panel('Navigation Console', panels); navigation = Panel.get_panel('Navigation', panels); ncd = navigation_console_display
         
        for i, x in enumerate(range(5, 0, -1)):     # distance labels 
            Text(str(x), ncd, (ncd.rect.centery + 65, 20 + i * 20), 'arial', 12, 'cyan')
        for i, x in enumerate(range(1, 6)):
            Text(str(x), ncd, (ncd.rect.centery + 65, 135 + i * 20), 'arial', 12, 'cyan')
        Text('0', ncd, (ncd.rect.centery + 65, 117.5), 'arial', 12, 'cyan')
        for i, x in enumerate(range(5, 0, -1)):
            Text(str(x), ncd, (120 + i * 20 + 110, ncd.rect.centery + 50), 'arial', 12, 'cyan') 
        for i, x in enumerate(range(1, 6)):
            Text(str(x), ncd, (230 + i * 20 + 110, ncd.rect.centery + 50), 'arial', 12, 'cyan')
        
        Text('0', ncd, (ncd.rect.centery + 160, 215), 'arial', 12, 'cyan')

        for i in range(5, 0, -1):
            Text(str(i), ncd, (ncd.rect.centerx - 210, 20 + (5 - i) * 20), 'arial', 12, 'cyan')
        for i in range(1, 6):
            Text(str(i), ncd, (ncd.rect.centerx - 210, 135 + (i - 1) * 20), 'arial', 12, 'cyan')
        for i in range(5, 0, -1):
            Text(str(i), ncd, (10 + (5 - i) * 20, ncd.rect.centerx - 5), 'arial', 12, 'cyan')
        for i in range(1, 6):
            Text(str(i), ncd, (125 + (i - 1) * 20, ncd.rect.centerx - 5), 'arial', 12, 'cyan') 


        Text('A', ncd, (ncd.rect.centerx+11, ncd.rect.centery+96), 'arial', 11, 'green')
        Text('B', ncd, (ncd.rect.centerx+11, ncd.rect.centery+111), 'arial', 11, 'green')
        Text('A', ncd, (ncd.rect.centerx+32, ncd.rect.centery+96), 'arial', 11, 'dark blue')
        Text('A', ncd, (ncd.rect.centerx+32, ncd.rect.centery+111), 'arial', 11, 'dark blue')
        Text('Hum', ncd, (ncd.rect.centerx+55, ncd.rect.centery+96), 'arial', 11, 'green')
        Text('?', ncd, (ncd.rect.centerx+60, ncd.rect.centery+111), 'arial', 11, 'green')
        Text('3', ncd, (ncd.rect.centerx+85, ncd.rect.centery+96), 'arial', 11, 'green')
        Text('?', ncd, (ncd.rect.centerx+85, ncd.rect.centery+111), 'arial', 11, 'green')
        Text('Unknown', ncd, (ncd.rect.centerx+157.5, ncd.rect.centery+96), 'arial', 11, 'grey')
        Text('Unknown', ncd, (ncd.rect.centerx+157.5, ncd.rect.centery+111), 'arial', 11, 'grey')

        return panels

    def draw_elements(panels:list):
        currentTime = pygame.time.get_ticks() # <------- USE FOR ANY TIMED EVENTS!!!
        global lastTime

        primary = Panel.get_panel('Primary Display', panels); pri = primary.get_element('primary display')
            # SCIENCE CONSOLE
        science_console_display = Panel.get_panel('Science Console', panels).get_element('sights display') # Sights display on science console is drawn onto.
        pygame.draw.line(science_console_display.surf, 'white', (science_console_display.rect.centerx, 0), (science_console_display.rect.centerx, 200), 1)
        pygame.draw.line(science_console_display.surf, 'white', (0, science_console_display.rect.centery), (200, science_console_display.rect.centery), 1)
        for i in range(0 ,science_console_display.rect.centerx * 2, 15):
            pygame.draw.line(science_console_display.surf, 'white', (science_console_display.rect.centerx - 10, i), (science_console_display.rect.centerx + 10, i), 1)
            pygame.draw.line(science_console_display.surf, 'white', (i, science_console_display.rect.centerx - 10), (i, science_console_display.rect.centerx + 10), 1)
            
            # NAVIGATION CONSOLE
        navigation_console_display = Panel.get_panel('Navigation Console', panels); navigation = Panel.get_panel('Navigation', panels); ncd = navigation_console_display
        show_navigation = True
        # navigation console and navigation are two separate panels but belong to the same 'console', star map also belongs to this console too
        transparent_surface = pygame.Surface(ncd.surf.get_size(), pygame.SRCALPHA); transparent_rect = transparent_surface.get_rect() 
        transparent_color = (255, 255, 255, 50) # 4th val for transparency, lower = more transparent, higher = less transparent
        sm = Panel.get_panel('Star Map', panels)
        def draw_rect_with_border(surface, fill_color, border_color, rect, border_width=1):
            pygame.draw.rect(surface, fill_color, rect)
            pygame.draw.rect(surface, border_color, rect, border_width)

        # System Map
        for i in range(20, 220, 10):
            pygame.draw.line(transparent_surface, transparent_color, (220 + 5, i + 10), (440 - 5, i + 10), 1)
        for i in range(235, 435, 10):
            pygame.draw.line(transparent_surface, transparent_color, (i, 25 - 5), (i, 225 + 5), 1)
        ncd.surf.blit(transparent_surface, transparent_rect) 
        circles = [     # star system assets
            ('red', 90, 1),     # planet 1 orbit
            ('blue', 50, 1),    # planet 2 orbit
            ('yellow', 10, 10),     # star
            ('orange', 7, 7, 330, 35),    # planet 1
            ('cyan', 5, 5, 290, 95),    # planet 2
        ]
        for circle in circles:
            color, radius, width = circle[:3]
            pos = (circle[3], circle[4]) if len(circle) > 3 else (330, 125)
            pygame.draw.circle(ncd.surf, color, pos, radius, width)

        headings = [
            ('0', ncd.rect.centerx - 111.5, ncd.rect.centery - 138.5),
            ('180', ncd.rect.centerx - 111.5, ncd.rect.centery + 56.5),
            ('90', ncd.rect.centerx - 19.5, ncd.rect.centery - 43.5),
            ('270', ncd.rect.centerx - 202.5, ncd.rect.centery - 43.5),
        ]
        pygame.draw.rect(ncd.surf, (210, 210, 210), [ncd.rect.centerx - 125, ncd.rect.centery + 50, 30, 15])
        pygame.draw.rect(ncd.surf, 'black', [ncd.rect.centerx - 125, ncd.rect.centery + 50, 30, 15], 3)
        pygame.draw.rect(ncd.surf, (210, 210, 210), [ncd.rect.centerx - 125, ncd.rect.centery - 145, 30, 15])
        pygame.draw.rect(ncd.surf, 'black', [ncd.rect.centerx - 125, ncd.rect.centery -145, 30, 15], 3)
        pygame.draw.rect(ncd.surf, (210, 210, 210), [ncd.rect.centerx - 215, ncd.rect.centery - 50, 30, 15])
        pygame.draw.rect(ncd.surf, 'black', [ncd.rect.centerx - 215, ncd.rect.centery - 50, 30, 15], 3)
        pygame.draw.rect(ncd.surf, (210, 210, 210), [ncd.rect.centerx - 35, ncd.rect.centery - 50, 30, 15])
        pygame.draw.rect(ncd.surf, 'black', [ncd.rect.centerx - 35, ncd.rect.centery - 50, 30, 15], 3)
        for txt, x, y in headings:
            txt_surf = txt_font.render(txt, True, 'black')
            txt_rect = txt_surf.get_rect(center=(x, y))
            ncd.surf.blit(txt_surf, txt_rect)
        #'Navigation'
        pygame.draw.rect(navigation.surf, ALTPANELGREY, [navigation.rect.centerx-96, navigation.rect.centery-65, 192, 145])
        def draw_navigation():  # draws outlines / where data is meant to go
            bwRects = [     # black bg w/ white outline
                (-51.5, -52.5, 30, 13),
                (-16.5, -52.5, 30, 13),
                (-51.5, -37.5, 30, 13),
                (-16.5, -37.5, 30, 13),
                (60.5, -52.5, 30, 13),
                (-35, -17.5, 48, 13),
                (-35, -2.5, 48, 13),
                (-5, 30, 75, 13),
                (-5, 50, 75, 13),
            ]
            pgRects = [     # grey bg w/ black outline 
                (30, -30, 50, 13),
                (35, 2.5, 15, 13),
                (57.5, 2.5, 15, 13),
            ]
            lines = [
                ((navigation.rect.centerx+37, navigation.rect.centery+7.5), (navigation.rect.centerx+45, navigation.rect.centery+5)),
                ((navigation.rect.centerx+37, navigation.rect.centery+7.5), (navigation.rect.centerx+45, navigation.rect.centery+10)),
                ((navigation.rect.centerx+60, navigation.rect.centery+10), (navigation.rect.centerx+68, navigation.rect.centery+7.5)),
                ((navigation.rect.centerx+60, navigation.rect.centery+5), (navigation.rect.centerx+68, navigation.rect.centery+7.5)),
            ]
            for x_os, y_os, w, h, in bwRects:# x offset and y offset
                rect = [navigation.rect.centerx + x_os, navigation.rect.centery + y_os, w, h]
                draw_rect_with_border(navigation.surf, 'black', 'white', rect)
            for x_os, y_os, w, h, in pgRects:
                rect = [navigation.rect.centerx + x_os, navigation.rect.centery + y_os, w, h]
                draw_rect_with_border(navigation.surf, PANELGREY, 'black', rect)
            for start_pos, end_pos in lines:
                pygame.draw.line(navigation.surf, 'black', start_pos, end_pos, 2)
        def navigation_txt(surface, font, text, color, x_os, y_os): 
            center = (navigation.rect.centerx + x_os, navigation.rect.centery + y_os)
            txt_surf = font.render(text, True, pygame.Color(color))
            txt_rect = txt_surf.get_rect(center=center) 
            surface.blit(txt_surf,txt_rect)
        def draw_navigation_data():
            txt_data = [
                ('X', 'cyan', -37.5, -59),
                ('Y', 'cyan', -5, -59),
                ('Reg. Loc:', 'cyan', -74, -47.5),
                ('Orb Pos:', 'cyan', -74, -32.5),
                ('Dist. Trgt:', 'cyan', 36, -47.5),
                ('Course Set:', 'cyan', -69, -12.5),
                ('Target 1:', 'cyan', -69, 2.5),
                ('Object:', 'cyan', -35, 35),
                ('Mode:', 'cyan', -35, 55),
                ('Evasive', 'black', 54, -24.5),
                ('Sideslip', 'cyan', 52.5, -7.5),
                ('4', 'green', -30, -47.5),
                ('6', 'green', 5, -47.5),
                ('1.4', 'green', 80, -47.5),
                ('40', 'green', -30, -32.5),
                ('0', 'green', 5, -32.5),
                ('135°', 'green', 0, -12.5),
                ('40, 0', 'green', 0, 2.5),
                ('Planet', 'green', 32.5, 35),
            ]
            for text, color, x_os, y_os in txt_data:
                navigation_txt(navigation.surf, txt_font_small, text, color, x_os, y_os)
        if show_navigation:
            draw_navigation()
            draw_navigation_data()
        pygame.draw.rect(navigation.surf, 'light blue', [navigation.rect.centerx-4,navigation.rect.centery+51, 73, 11]) # this corelates to what video is playing (default is hyperspace, orbit, normal space)
        txt_surf = txt_font_small.render('Hyperpace', True, 'black')
        txt_rect = txt_surf.get_rect(center=(navigation.rect.centerx+32.5, navigation.rect.centery+55))
        navigation.surf.blit(txt_surf,txt_rect)
        #ncd.mercatorMapN = r'assets/mmn.mp4'
        #mercatorMapSM 

        # data tables 
        if pri.showCircles == True: #orbit zones for 'Orbital Display', this activates when press n --> supposed to correlate with what video playsin primary display, by dfault primary display plays hyperspace vid, so show circles off, but when press n and primary shows mercator map then show cirlce on for obrital stuffs 
            pygame.draw.circle(ncd.surf, 'blue', (ncd.rect.centerx - 110, ncd.rect.centery - 40), 80, 1)
            pygame.draw.circle(ncd.surf, 'blue', (ncd.rect.centerx - 110, ncd.rect.centery - 40), 65, 1)
            pygame.draw.circle(ncd.surf, 'blue', (ncd.rect.centerx - 110, ncd.rect.centery - 40), 55, 1)
            pygame.draw.circle(ncd.surf, 'green', (ncd.rect.centerx - 110, ncd.rect.centery - 40), 40, 1)
            # make it so that the 4 drawn circles above are only active when in orbit of a planet, not while in hyperspace
            # so by default that ui should have none of the cirlces drawn, but when you press 'n' and go into orbit the cricles will turn on 
        if ncd.navButtonUI1 == True: #'Objects'
            pygame.draw.rect(ncd.surf, BUTTONPRESSED, [ncd.rect.centerx-215, ncd.rect.centery+66, 60, 13])
            txt_surf = txt_font_small.render('Objects', True, 'black'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-185,ncd.rect.centery+72.5))
            ncd.surf.blit(txt_surf,txt_rect)
            pygame.draw.rect(ncd.surf, ALTPANELGREY, [ncd.rect.centerx-215, ncd.rect.centery+80, 210, 15])
            pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx -215, ncd.rect.centery+95), (ncd.rect.centerx-6, ncd.rect.centery+95), 1)
            pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx -180, ncd.rect.centery+80), (ncd.rect.centerx-180, ncd.rect.centery+160), 1)
            pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx -115, ncd.rect.centery+80), (ncd.rect.centerx-115, ncd.rect.centery+160), 1)
            pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx -75, ncd.rect.centery+80), (ncd.rect.centerx-75, ncd.rect.centery+160), 1)
            txt_surf = txt_font.render('ID#', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-197, ncd.rect.centery+87))
            ncd.surf.blit(txt_surf, txt_rect)
            txt_surf = txt_font.render('Name', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-147.5,ncd.rect.centery+87))
            ncd.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font.render('Rel-Pos', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-95,ncd.rect.centery+87))
            ncd.surf.blit(txt_surf, txt_rect)
            txt_surf = txt_font.render('Status', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-40,ncd.rect.centery+87))
            ncd.surf.blit(txt_surf,txt_rect)
        if navigation_console_display.navButtonUI2 == True: #'Planet data'
            #create lists to optimize cause this one's really bad 
            pygame.draw.rect(ncd.surf, BUTTONPRESSED, [ncd.rect.centerx-155,ncd.rect.centery+66,50,13])
            txt_surf = txt_font_small.render('Orbit Zones', True, 'black'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-130,ncd.rect.centery+72.5))
            ncd.surf.blit(txt_surf,txt_rect)
            pygame.draw.rect(ncd.surf, ALTPANELGREY, [ncd.rect.centerx-215, ncd.rect.centery+80, 210, 15])
            pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx -215, ncd.rect.centery+95), (ncd.rect.centerx-6, ncd.rect.centery+95), 1)
            pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx -180, ncd.rect.centery+80), (ncd.rect.centerx-180, ncd.rect.centery+160), 1)
            pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx -125, ncd.rect.centery+80), (ncd.rect.centerx-125, ncd.rect.centery+160), 1)
            pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx -105, ncd.rect.centery+80), (ncd.rect.centerx-105, ncd.rect.centery+160), 1)   
            pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx -82.5, ncd.rect.centery+80), (ncd.rect.centerx-82.5, ncd.rect.centery+160), 1) 
            pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx -55, ncd.rect.centery+80), (ncd.rect.centerx-55, ncd.rect.centery+160), 1) 
            pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx -30, ncd.rect.centery+80), (ncd.rect.centerx-30, ncd.rect.centery+160), 1) 
            txt_surf = txt_font.render('ID#', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-197,ncd.rect.centery+87))
            ncd.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font.render('Name', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-152.5,ncd.rect.centery+87))
            ncd.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font.render('SP', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-114,ncd.rect.centery+87))
            ncd.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font.render('Cls', True, 'cyan'); txt_rect =txt_surf.get_rect(center=(ncd.rect.centerx-94,ncd.rect.centery+87))
            ncd.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font.render('LP', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-68,ncd.rect.centery+87))
            ncd.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font.render('Bs', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-41,ncd.rect.centery+87))
            ncd.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font.render('T', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-17.5,ncd.rect.centery+87))
            ncd.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('SS-39A', True, 'green'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-198,ncd.rect.centery+102))
            ncd.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('Gurth', True, 'green'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-152.5,ncd.rect.centery+102))
            ncd.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('N', True, 'green'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-114,ncd.rect.centery+102))
            ncd.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('A', True, 'dark blue'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-94,ncd.rect.centery+102))
            ncd.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('N', True, 'green'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-68,ncd.rect.centery+102))
            ncd.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('N', True, 'green'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-41,ncd.rect.centery+102))
            ncd.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('N', True, 'green'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-17.5,ncd.rect.centery+102))
            ncd.surf.blit(txt_surf,txt_rect)
        if navigation_console_display.navButtonUI3 == True:
            pygame.draw.rect(ncd.surf, BUTTONPRESSED, [ncd.rect.centerx-100,ncd.rect.centery+66,60,13])
            txt_surf = txt_font_small.render('Mercator Map', True, 'black'); txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx-70,ncd.rect.centery+72.5))
            ncd.surf.blit(txt_surf, txt_rect)
            nav_display = ncd.get_element("Navigation Video")
            ncd.surf.blit(nav_display.surf, (0, 245))
            #ncd.surf.blit(mercatorMapN.surf, (ncd.rect.centerx-215, ncd.rect.centery+80))
            #'Planets'
                # data of planets will only show when actively in a star system, for example; if in hyperspace there shouldnt be any planet data here
        # make lists to optimize
        pygame.draw.rect(ncd.surf, ALTPANELGREY, [ncd.rect.centerx+5, ncd.rect.centery+80, 210, 15])
        pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx, ncd.rect.centery+95), (ncd.rect.centerx+220, ncd.rect.centery+95), 1)
        pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx+25, ncd.rect.centery+80), (ncd.rect.centerx+25, ncd.rect.centery+160), 1)
        pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx+50, ncd.rect.centery+80), (ncd.rect.centerx+50, ncd.rect.centery+160), 1)
        pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx+75, ncd.rect.centery+80), (ncd.rect.centerx+75, ncd.rect.centery+160), 1)
        pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx+100, ncd.rect.centery+80), (ncd.rect.centerx+100, ncd.rect.centery+160), 1)
        pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx+120, ncd.rect.centery+80), (ncd.rect.centerx+120, ncd.rect.centery+160), 1)
        pygame.draw.line(ncd.surf, PANELGREY, (ncd.rect.centerx+140, ncd.rect.centery+80), (ncd.rect.centerx+140, ncd.rect.centery+160), 1)
        txt_surf = txt_font.render('ID', True, pygame.Color('cyan'))
        txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx+15,ncd.rect.centery+87))
        ncd.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('Cls', True, 'cyan')
        txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx+37.5,ncd.rect.centery+87))
        ncd.surf.blit(txt_surf,txt_rect)
        txt_surf= txt_font.render('Inh', True, 'cyan')
        txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx+62.5,ncd.rect.centery+87))
        ncd.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('Tch', True, 'cyan')
        txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx+87.5,ncd.rect.centery+87))
        ncd.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('LP', True, 'cyan')
        txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx+110,ncd.rect.centery+87))
        ncd.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('BS', True, 'cyan')
        txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx+131,ncd.rect.centery+87))
        ncd.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('Status', True, 'cyan')
        txt_rect = txt_surf.get_rect(center=(ncd.rect.centerx+175,ncd.rect.centery+87))
        ncd.surf.blit(txt_surf,txt_rect)
        # Star Map
        if sm.ButtonUI1 == True:
            pygame.draw.rect(sm.surf, BUTTONPRESSED, [sm.rect.centerx+33,sm.rect.centery-107,59,13])
            txt_surf = txt_font_small.render('Mercator Map', True, 'black'); txt_rect = txt_surf.get_rect(center=(sm.rect.centerx+62.5,sm.rect.centery-100.5))
            sm.surf.blit(txt_surf,txt_rect)
            #vidDisp.play_video(r'assets/EarthOrbit.mp4')
            #place mercator map here
        if sm.ButtonUI2 == True:
            pygame.draw.rect(sm.surf, BUTTONPRESSED, [sm.rect.centerx+94,sm.rect.centery-107,60,13])
            txt_surf = txt_font_small.render('Nav Map', True, 'black'); txt_rect = txt_surf.get_rect(center=(sm.rect.centerx+122.5,sm.rect.centery-100.5))
            sm.surf.blit(txt_surf,txt_rect)
            sm.surf.blit(nav_map_png, (sm.rect.centerx-232,sm.rect.centery-92))
        if sm.ButtonUI3 == True:
            pygame.draw.rect(sm.surf, BUTTONPRESSED, [sm.rect.centerx+156,sm.rect.centery-107,58,13])
            txt_surf = txt_font_small.render('War Map', True, 'black'); txt_rect = txt_surf.get_rect(center=(sm.rect.centerx+184.5,sm.rect.centery-100.5))
            sm.surf.blit(txt_surf,txt_rect)
            sm.surf.blit(war_map_png, (sm.rect.centerx-232,sm.rect.centery-92))
            # DATA (misc)
        data = Panel.get_panel('Data', panels)
        data.showData = True
        pygame.draw.rect(data.surf, ALTPANELGREY, [4, 9, 150, 120])
        def draw_data_panel(data, font):
            dataItems = [
                ('Crew', '275', -47.5),
                ('Shk Troops', '150', -22.5),
                ('Supplies', '88%', 0),
                ('Escorts', '4', 22.5),
                ('Oblitr. Pods', '2', 45),
            ]
            for label, value, y_os in dataItems: # y_os = y offset needed for centering 
                rect = [data.rect.centerx+25, data.rect.centery+y_os-5, 40, 13]
                pygame.draw.rect(data.surf, 'black', rect)
                pygame.draw.rect(data.surf, 'white', rect, 1)
                txt_surf = font.render(label, True, 'cyan'); txt_rect = txt_surf.get_rect(center=(data.rect.centerx-45, data.rect.centery+y_os)); data.surf.blit(txt_surf,txt_rect)
                txt_surf = font.render(value, True, 'green'); txt_rect = txt_surf.get_rect(center=(data.rect.centerx+50, data.rect.centery+y_os)); data.surf.blit(txt_surf,txt_rect)
        if data.showData:
            draw_data_panel(data, txt_font_medium)
            # ENGINEERING CONSOLE
        engC = Panel.get_panel('Engineering Console', panels)
        # Probes Control
        def draw_probe_data(): # launch data
            # column & row data
            headers = ['#', 'Status', 'TG', 'RAD', 'SS', 'REG. L', 'SYS. L', 'DETECT']
            headers_xpos = [15, 55, 102.5, 142.5, 182.5, 230, 292.5, 355]; headers_ypos = engC.rect.centery-88
            rows = [
                ['1', 'Passive', '43', '', '43', '(6, 7)', '(49, 43)', ''],
                ['2', 'Passive', '30', '', '30', '(2, 8)', '(51, 67)', ''],
                ['3', 'Passive', '9', '', '9', '(2, 9)', '(52, 24)', ''],
                ['4', 'Passive', '41', '', '41', '(0, 8)', '(21, 63)', ''],
                ['5', 'Passive', '7', '', '7', '(0, 4)', '(21, 63)', ''],
            ]
            row_ypos = engC.rect.centery-70.5; row_height = 14
            for i, header in enumerate(headers):
                txt_surf = txt_font.render(header, True, 'cyan'); txt_rect = txt_surf.get_rect(center=(headers_xpos[i], headers_ypos)); engC.surf.blit(txt_surf,txt_rect)
            for row_idx, row in enumerate(rows):
                y = row_ypos + row_idx*row_height
                for col_idx, cell in enumerate(row):
                    if cell:
                        txt_surf = txt_font.render(cell, True, 'green'); txt_rect = txt_surf.get_rect(center=(headers_xpos[col_idx], y)); engC.surf.blit(txt_surf,txt_rect)
        def draw_probe_operations():
            headers = ['#', 'Mode', 'TG', 'SS#', 'R. LOC', 'S. LOC', 'Pw%', 'Status', 'S', 'X', 'sh', 'bs']
            headers_xpos = [15, 55, 97.5, 128, 166, 215, 257.5, 300, 332.5, 347.5, 362.5, 377.5]; headers_ypos = engC.rect.centery-88
            rows = [
                ['1', 'Passive', 'SS-42', '', '(4, 6)', '', '100', 'Transit', '', '', '', ''],
                ['2', 'Passive', 'SS-35', '', '(4, 6)', '', '100', 'Transit', '', '', '', ''],
                ['3', 'Passive', 'SS-10', '', '(4, 6)', '', '100', 'Transit', '', '', '', ''],
                ['4', 'Passive', 'SS-45', '', '(4, 6)', '', '100', 'Transit', '', '', '', ''],
                ['5', 'Passive', 'SS-36', '', '(4, 6)', '', '100', 'Transit', '', '', '', ''],
            ]
            row_ypos = engC.rect.centery-70.5; row_height = 14
            for i, header in enumerate(headers):
                txt_surf = txt_font.render(header, True, 'cyan'); txt_rect = txt_surf.get_rect(center=(headers_xpos[i], headers_ypos)); engC.surf.blit(txt_surf,txt_rect)
            for row_idx, row in enumerate(rows):
                y = row_ypos + row_idx*row_height
                for col_idx, cell in enumerate(row):
                    if cell:
                        txt_surf = txt_font.render(cell, True, 'green'); txt_rect = txt_surf.get_rect(center=(headers_xpos[col_idx], y)); engC.surf.blit(txt_surf,txt_rect)
        if engC.ButtonUI1 == True:
            vertLines_xpos = [25, 80, 115, 140, 190, 240, 275, 325, 340, 355, 370, 385]
            pygame.draw.rect(engC.surf, BUTTONPRESSED, [220, engC.rect.centery-112, 80, 15])
            txt_surf = txt_font_small.render('Operations', True, 'black'); txt_rect = txt_surf.get_rect(center=(260, engC.rect.centery-105.5)); engC.surf.blit(txt_surf,txt_rect)
            pygame.draw.rect(engC.surf, ALTPANELGREY, [5,25,380,15])
            pygame.draw.line(engC.surf, PANELGREY, (5, engC.rect.centery-80), (385, engC.rect.centery-80), 1)
            for x in vertLines_xpos:
                pygame.draw.line(engC.surf, PANELGREY, (x, engC.rect.centery - 95), (x, engC.rect.centery-5), 1)
            draw_probe_operations()
        if engC.ButtonUI2 == True:
            vertLines_xpos = [25, 85, 120, 165, 200, 260, 325]
            pygame.draw.rect(engC.surf, BUTTONPRESSED, [301, engC.rect.centery-112, 80, 15])
            txt_surf = txt_font_small.render('Launch', True, 'black'); txt_rect = txt_surf.get_rect(center=(340, engC.rect.centery-105.5)); engC.surf.blit(txt_surf,txt_rect)
            pygame.draw.rect(engC.surf, ALTPANELGREY, [5,25,380,15])
            pygame.draw.line(engC.surf, PANELGREY, (5, engC.rect.centery-80), (385, engC.rect.centery-80), 1)
            for x in vertLines_xpos:
                pygame.draw.line(engC.surf, PANELGREY, (x, engC.rect.centery - 95), (x, engC.rect.centery-5), 1)
            draw_probe_data()
        # DAMAGE - SHIP DISPLAY
        f = engC.rect.centery+22.5; g = engC.rect.centery+22.5
        pygame.draw.line(engC.surf, PANELGREY, (520, engC.rect.centery-95), (520, engC.rect.centery+115))
        pygame.draw.line(engC.surf, PANELGREY, (385, engC.rect.centery+10), (520, engC.rect.centery+10))
        engC.surf.blit(ship_dmg_display, (130, engC.rect.centery-200))  # one way to make this dynamic, is through the separation of each section of the ship into their own png files, each section will have 4 variations; green = good condition, yellow = damaged, red = heavily damaged, black = inoperative/destroyed
        for i, dmgStatus in enumerate(engC.CycleDamage):
            if dmgStatus == 1:
                pygame.draw.rect(engC.surf, 'green', [440, engC.rect.centery+25, 25, 65])
                txt_surf = txt_font.render('HULL', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(452.5, engC.rect.centery+100)); engC.surf.blit(txt_surf,txt_rect)
                for i in range(0, 6, 1):
                    pygame.draw.rect(engC.surf, 'green', [390, f+i, 40, 11])
                    i=13; f+=i
                for i in range(0, 6, 1):
                    pygame.draw.rect(engC.surf, 'green', [475, g+i, 40, 11])
                    i=13; g+=i
            if dmgStatus == 2:
                pygame.draw.rect(engC.surf, 'black', [440, engC.rect.centery+95, 26, 20])
                txt_surf = txt_font.render('HULL', True, 'yellow'); txt_rect = txt_surf.get_rect(center=(452.5, engC.rect.centery+100)); engC.surf.blit(txt_surf,txt_rect)
                pygame.draw.rect(engC.surf, 'yellow', [440, engC.rect.centery+25, 25, 65])
                for i in range(0, 6, 1):
                    pygame.draw.rect(engC.surf, 'yellow', [390, f+i, 40, 11])
                    i=13; f+=i
                for i in range(0, 6, 1):
                    pygame.draw.rect(engC.surf, 'yellow', [475, g+i, 40, 11])
                    i=13; g+=i
            if dmgStatus == 3:
                pygame.draw.rect(engC.surf, 'black', [440, engC.rect.centery+95, 26, 20])
                txt_surf = txt_font.render('HULL', True, 'red'); txt_rect = txt_surf.get_rect(center=(452.5, engC.rect.centery+100)); engC.surf.blit(txt_surf,txt_rect)
                pygame.draw.rect(engC.surf, 'red', [440, engC.rect.centery+25, 25, 65])
                for i in range(0, 6, 1):
                    pygame.draw.rect(engC.surf, 'red', [390, f+i, 40, 11])
                    i=13; f+=i
                for i in range(0, 6, 1):
                    pygame.draw.rect(engC.surf, 'red', [475, g+i, 40, 11])
                    i=13; g+=i
            txt_surf = txt_font_small.render('CMPTR', True, 'black'); txt_rect = txt_surf.get_rect(center=(407.5, engC.rect.centery+27)); engC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('S/L ENG', True, 'black'); txt_rect = txt_surf.get_rect(center=(408.5, engC.rect.centery+40.5)); engC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('HYP ENG', True, 'black'); txt_rect = txt_surf.get_rect(center=(410, engC.rect.centery+54)); engC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('SRS', True, 'black'); txt_rect = txt_surf.get_rect(center=(408.5, engC.rect.centery+68.5)); engC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('LRS', True, 'black'); txt_rect = txt_surf.get_rect(center=(408.5, engC.rect.centery+82.5)); engC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('SHD CTL', True, 'black'); txt_rect = txt_surf.get_rect(center=(408.5, engC.rect.centery+96.5)); engC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('TRP CTL', True, 'black'); txt_rect = txt_surf.get_rect(center=(495, engC.rect.centery+27)); engC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('PHS CTL', True, 'black'); txt_rect = txt_surf.get_rect(center=(495, engC.rect.centery+40.5)); engC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('TELEPRT', True, 'black'); txt_rect = txt_surf.get_rect(center=(495, engC.rect.centery+54)); engC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('COM CTL', True, 'black'); txt_rect = txt_surf.get_rect(center=(495, engC.rect.centery+68.5)); engC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('TRAC BM', True, 'black'); txt_rect = txt_surf.get_rect(center=(495, engC.rect.centery+82.5)); engC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('PLS', True, 'black'); txt_rect = txt_surf.get_rect(center=(495, engC.rect.centery+96.5)); engC.surf.blit(txt_surf,txt_rect)
            if dmgStatus == 4:
                pygame.draw.rect(engC.surf, 'black', [440, engC.rect.centery+25, 26, 85]); pygame.draw.rect(engC.surf, 'white', [440, engC.rect.centery+25, 25, 65], 1)
                txt_surf = txt_font.render('HULL', True, 'white'); txt_rect = txt_surf.get_rect(center=(452.5, engC.rect.centery+100)); engC.surf.blit(txt_surf,txt_rect)
                for i in range(0, 6, 1):
                    pygame.draw.rect(engC.surf, 'black', [390, f+i, 40, 11]); pygame.draw.rect(engC.surf, 'white', [390, f+i, 40, 11], 1)
                    i=13; f+=i
                for i in range(0, 6, 1):
                    pygame.draw.rect(engC.surf, 'black', [475, g+i, 40, 11]); pygame.draw.rect(engC.surf, 'white', [475, g+i, 40, 11], 1)
                    i=13; g+=i
                txt_surf = txt_font_small.render('CMPTR', True, 'white'); txt_rect = txt_surf.get_rect(center=(407.5, engC.rect.centery+27)); engC.surf.blit(txt_surf,txt_rect)
                txt_surf = txt_font_small.render('S/L ENG', True, 'white'); txt_rect = txt_surf.get_rect(center=(408.5, engC.rect.centery+40.5)); engC.surf.blit(txt_surf,txt_rect)
                txt_surf = txt_font_small.render('HYP ENG', True, 'white'); txt_rect = txt_surf.get_rect(center=(410, engC.rect.centery+54)); engC.surf.blit(txt_surf,txt_rect)
                txt_surf = txt_font_small.render('SRS', True, 'white'); txt_rect = txt_surf.get_rect(center=(408.5, engC.rect.centery+68.5)); engC.surf.blit(txt_surf,txt_rect)
                txt_surf = txt_font_small.render('LRS', True, 'white'); txt_rect = txt_surf.get_rect(center=(408.5, engC.rect.centery+82.5)); engC.surf.blit(txt_surf,txt_rect)
                txt_surf = txt_font_small.render('SHD CTL', True, 'white'); txt_rect = txt_surf.get_rect(center=(408.5, engC.rect.centery+96.5)); engC.surf.blit(txt_surf,txt_rect)
                txt_surf = txt_font_small.render('TRP CTL', True, 'white'); txt_rect = txt_surf.get_rect(center=(495, engC.rect.centery+27)); engC.surf.blit(txt_surf,txt_rect)
                txt_surf = txt_font_small.render('PHS CTL', True, 'white'); txt_rect = txt_surf.get_rect(center=(495, engC.rect.centery+40.5)); engC.surf.blit(txt_surf,txt_rect)
                txt_surf = txt_font_small.render('TELEPRT', True, 'white'); txt_rect = txt_surf.get_rect(center=(495, engC.rect.centery+54)); engC.surf.blit(txt_surf,txt_rect)
                txt_surf = txt_font_small.render('COM CTL', True, 'white'); txt_rect = txt_surf.get_rect(center=(495, engC.rect.centery+68.5)); engC.surf.blit(txt_surf,txt_rect)
                txt_surf = txt_font_small.render('TRAC BM', True, 'white'); txt_rect = txt_surf.get_rect(center=(495, engC.rect.centery+82.5)); engC.surf.blit(txt_surf,txt_rect)
                txt_surf = txt_font_small.render('PLS', True, 'white'); txt_rect = txt_surf.get_rect(center=(495, engC.rect.centery+96.5)); engC.surf.blit(txt_surf,txt_rect)
        # Energy
            # energy usage changes accordingly when velocity is increased/decreased, however not yet implemented for increased shield usage and other functions
        pygame.draw.line(engC.surf, PANELGREY, (80, engC.rect.centery+20), (80, engC.rect.centery+120), 1)
        pygame.draw.line(engC.surf, PANELGREY, (5, engC.rect.centery+90), (385, engC.rect.centery+90), 1)
        pygame.draw.rect(engC.surf, PANELGREY, [100,engC.rect.centery+37.5,60,13], 1)
        pygame.draw.rect(engC.surf, PANELGREY, [165,engC.rect.centery+37.5,200,13], 1)
        pygame.draw.rect(engC.surf, PANELGREY, [100,engC.rect.centery+52.5,60,13], 1)
        pygame.draw.rect(engC.surf, PANELGREY, [165,engC.rect.centery+52.5,200,13], 1)
        pygame.draw.rect(engC.surf, PANELGREY, [100,engC.rect.centery+67.5,60,13], 1)
        pygame.draw.rect(engC.surf, PANELGREY, [165,engC.rect.centery+67.5,200,13], 1)
        pygame.draw.rect(engC.surf, PANELGREY, [100,engC.rect.centery+97.5,60,13], 1)
        pygame.draw.rect(engC.surf, PANELGREY, [165,engC.rect.centery+97.5,200,13], 1)
        pygame.draw.rect(engC.surf, 'green', [166, engC.rect.centery+38.5, 40, 11])
        pygame.draw.rect(engC.surf, 'green', [166, engC.rect.centery+53.5, 190, 11])
        pygame.draw.rect(engC.surf, 'green', [166, engC.rect.centery+68.5, 198, 11])
        pygame.draw.rect(engC.surf, 'yellow', [166, engC.rect.centery+98.5, 116, 11])
        e = 165; f = engC.rect.centery+22.5; g = engC.rect.centery+22.5
        for i in range(0, 220, 20):
            pygame.draw.line(engC.surf, PANELGREY, (e+i, engC.rect.centery+85), (e+i, engC.rect.centery+94), 1)
            i+=20
        txt_surf = txt_font.render('Usage', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(31.5, engC.rect.centery+42.5)); engC.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('Quatity', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(35, engC.rect.centery+57.5)); engC.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('Backup', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(35, engC.rect.centery+72.5)); engC.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('Shields', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(35, engC.rect.centery+102.5)); engC.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('20%', True, 'green'); txt_rect = txt_surf.get_rect(center=(140, engC.rect.centery+42.5)); engC.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('94%', True, 'green'); txt_rect = txt_surf.get_rect(center=(140, engC.rect.centery+57.5)); engC.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('100%', True, 'green'); txt_rect = txt_surf.get_rect(center=(140, engC.rect.centery+72.5)); engC.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('58%', True, 'yellow'); txt_rect = txt_surf.get_rect(center=(140, engC.rect.centery+102.5)); engC.surf.blit(txt_surf,txt_rect)

        # velocity + energy (changes energy usage according to velocity)
        pygame.draw.rect(engC.surf, ALTPANELGREY, [522, engC.rect.centery-95, 115, 210])
        pygame.draw.rect(engC.surf, 'black', [525, engC.rect.centery-85, 20, 13])
        pygame.draw.rect(engC.surf, PANELGREY, [525, engC.rect.centery-85, 20, 13], 1)
        pygame.draw.rect(engC.surf, 'black', [612.5, engC.rect.centery-85, 20, 13])
        pygame.draw.rect(engC.surf, PANELGREY, [612.5, engC.rect.centery-85, 20, 13], 1)
        pygame.draw.rect(engC.surf, 'black', [525, engC.rect.centery+95, 20, 13])
        pygame.draw.rect(engC.surf, PANELGREY, [525, engC.rect.centery+95, 20, 13], 1)
        pygame.draw.rect(engC.surf, 'black', [612.5, engC.rect.centery+95, 20, 13])
        pygame.draw.rect(engC.surf, PANELGREY, [612.5, engC.rect.centery+95, 20, 13], 1)
        pygame.draw.rect(engC.surf, 'black', [562.5, engC.rect.centery-95, 35, 210])
        pygame.draw.rect(engC.surf, PANELGREY, [562.5, engC.rect.centery-97, 35, 214], 1) 
        pygame.draw.line(engC.surf, PANELGREY, (580, engC.rect.centery-95), (580, engC.rect.centery+115))

        pygame.draw.rect(engC.surf, 'magenta', [563.5, engC.rect.centery+111, 17, 4])
        pygame.draw.rect(engC.surf, 'green', [579.5, engC.rect.centery+111, 17, 4])   
        pygame.draw.polygon(engC.surf, 'magenta', [(550, engC.rect.centery+105), (550, engC.rect.centery+115), (560, engC.rect.centery+110)])
        pygame.draw.polygon(engC.surf, 'green', [(608.5, engC.rect.centery+105), (608.5, engC.rect.centery+115), (598.5, engC.rect.centery+110)])

        txt_surf = txt_font.render('S:', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(535, engC.rect.centery-65)); engC.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('0', True, 'green'); txt_rect = txt_surf.get_rect(center=(535, engC.rect.centery-80)); engC.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('C:', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(622.5, engC.rect.centery-65)); engC.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('0', True, 'green'); txt_rect = txt_surf.get_rect(center=(622.5, engC.rect.centery-80)); engC.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('H', True, 'magenta'); txt_rect = txt_surf.get_rect(center=(532.5, engC.rect.centery+87.5)); engC.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('0', True, 'green'); txt_rect = txt_surf.get_rect(center=(537.5, engC.rect.centery+100.5)); engC.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('S', True, 'green'); txt_rect = txt_surf.get_rect(center=(622.5, engC.rect.centery+87.5)); engC.surf.blit(txt_surf,txt_rect)
        txt_surf = txt_font.render('0', True, 'green'); txt_rect = txt_surf.get_rect(center=(622.5, engC.rect.centery+100.5)); engC.surf.blit(txt_surf,txt_rect)

        k = 0.0; l = 0; # place holders for increment
        drawHeight = engC.kVal + engC.rect.centery+92; 
        drawHeight = engC.kVal + engC.rect.centery + 92
        engC.rectw = 35
        engC.energy_usage = max(0, min(100, engC.energy_usage)); 
        energy_usage = engC.energy_usage
        energy_quantity = engC.energy_quantity
        energy_backup = engC.energy_backup
        energy_shields = engC.energy_shields
        color = engC.color
        inc_counter = engC.inc_counter

        if engC.vHypUp == True:
            for k in engC.vHypBar:
                    # velocity stuff
                pygame.draw.rect(engC.surf, 'black', [526, engC.rect.centery-84, 18, 11])
                pygame.draw.rect(engC.surf, 'black', [526, engC.rect.centery+96, 18, 11])
                pygame.draw.rect(engC.surf, 'magenta', [563.5, engC.kVal+24.25-0.5, 17, drawHeight])
                pygame.draw.polygon(engC.surf, ALTPANELGREY, [(550, engC.rect.centery+105), (550, engC.rect.centery+115), (560, engC.rect.centery+110)])
                pygame.draw.polygon(engC.surf, 'magenta', [(550, engC.kVal+29.25), (550, engC.kVal+19.25), (560, engC.kVal+24.25)]) # arrow indicator beside velocity bar
                txt_surf = txt_font.render(str(engC.k), True, 'green'); txt_rect = txt_surf.get_rect(center=(535, engC.rect.centery-80)); engC.surf.blit(txt_surf,txt_rect)
                txt_surf = txt_font.render(str(engC.k), True, 'green'); txt_rect = txt_surf.get_rect(center=(535, engC.rect.centery+100.5)); engC.surf.blit(txt_surf,txt_rect)
                    #energy stuff
                pygame.draw.rect(engC.surf, 'black', [110, engC.rect.centery+38, 40, 11])
                pygame.draw.rect(engC.surf, 'black', [166, engC.rect.centery+38.5, 180, 11])
                if energy_usage > 60: # will change fill color of energy bar 
                    color = 'red'
                elif energy_usage > 25:
                    color = 'yellow'
                else:
                    color = 'green'
                txt_surf = txt_font.render(str(energy_usage)+'%', True, color); txt_rect = txt_surf.get_rect(center=(140, engC.rect.centery+42.5)); engC.surf.blit(txt_surf,txt_rect)
                pygame.draw.rect(engC.surf, color, [166, engC.rect.centery+38.5, 35, 11]) # this is just a place holder for the time being, this draws a small rect for the default energy usage which is like 20% or 25% right now
                for i in inc_counter:
                    pygame.draw.rect(engC.surf, color, [179, engC.rect.centery+38.5, engC.rectw, 11])
                engC.rectw+=10
            if k > 10.0:
                engC.vHypBar.pop()
        if engC.vHypDown == True:
            for k in engC.vHypBar: 
                pygame.draw.rect(engC.surf, 'black', [526, engC.rect.centery-84, 18, 11])
                pygame.draw.rect(engC.surf, 'black', [526, engC.rect.centery+96, 18, 11])
                pygame.draw.rect(engC.surf, 'magenta', [563.5, engC.kVal+24.25-0.5, 17, drawHeight])
                pygame.draw.polygon(engC.surf, ALTPANELGREY, [(550, engC.rect.centery+105), (550, engC.rect.centery+115), (560, engC.rect.centery+110)])
                pygame.draw.polygon(engC.surf, 'magenta', [(550, engC.kVal+29.25), (550, engC.kVal+19.25), (560, engC.kVal+24.25)])
                txt_surf = txt_font.render(str(engC.k), True, 'green'); txt_rect = txt_surf.get_rect(center=(535, engC.rect.centery-80)); engC.surf.blit(txt_surf,txt_rect)
                txt_surf = txt_font.render(str(engC.k), True, 'green'); txt_rect = txt_surf.get_rect(center=(535, engC.rect.centery+100.5)); engC.surf.blit(txt_surf,txt_rect)
                #
                pygame.draw.rect(engC.surf, 'black', [110, engC.rect.centery+38, 40, 11])
                pygame.draw.rect(engC.surf, 'black', [166, engC.rect.centery+38.5, 180, 11])
                if energy_usage > 60:
                    color = 'red'
                elif energy_usage > 25:
                    color = 'yellow'
                else:
                    color = 'green'
                txt_surf = txt_font.render(str(energy_usage)+'%', True, color); txt_rect = txt_surf.get_rect(center=(140, engC.rect.centery+42.5)); engC.surf.blit(txt_surf,txt_rect)
                pygame.draw.rect(engC.surf, color, [166, engC.rect.centery+38.5, 35, 11]) # this is jsut  a place holder for the time being
                for i in inc_counter:
                    pygame.draw.rect(engC.surf, color, [179, engC.rect.centery+38.5, engC.rectw, 11])
                engC.rectw+=10
            if k < 0:
                engC.vHypBar.append(k+1)
        if engC.vSpcUp == True:
            for l in engC.vSpcBar:
                pygame.draw.rect(engC.surf, 'black', [613.5, engC.rect.centery-84, 18, 11])
                pygame.draw.rect(engC.surf, 'black', [613.5, engC.rect.centery+96, 18, 11])
                pygame.draw.rect(engC.surf, 'green', [581.5, engC.lVal+24.25-0.5, 15, drawHeight])
                pygame.draw.polygon(engC.surf, ALTPANELGREY, [(608.5, engC.rect.centery+105), (608.5, engC.rect.centery+115), (598.5, engC.rect.centery+110)])
                pygame.draw.polygon(engC.surf, 'green', [(608.5, engC.lVal+29.25), (608.5, engC.lVal+19.25), (598.5, engC.lVal+24.25)])
                txt_surf = txt_font.render(str(engC.l), True, 'green'); txt_rect = txt_surf.get_rect(center=(622.5, engC.rect.centery-80)); engC.surf.blit(txt_surf,txt_rect)
                txt_surf = txt_font.render(str(engC.l), True, 'green'); txt_rect = txt_surf.get_rect(center=(622.5, engC.rect.centery+100.5)); engC.surf.blit(txt_surf,txt_rect)
                #
                pygame.draw.rect(engC.surf, 'black', [110, engC.rect.centery+38, 40, 11])
                pygame.draw.rect(engC.surf, 'black', [166, engC.rect.centery+38.5, 180, 11])
                if energy_usage > 60:
                    color = 'red'
                elif energy_usage > 25:
                    color = 'yellow'
                else:
                    color = 'green'
                txt_surf = txt_font.render(str(energy_usage)+'%', True, color); txt_rect = txt_surf.get_rect(center=(140, engC.rect.centery+42.5)); engC.surf.blit(txt_surf,txt_rect)
                pygame.draw.rect(engC.surf, color, [166, engC.rect.centery+38.5, 35, 11])
                for i in inc_counter:
                    pygame.draw.rect(engC.surf, color, [179, engC.rect.centery+38.5, engC.rectw-8, 11])
                engC.rectw+=6
            if l > 10.0:
                engC.vSpcBar.pop()
        if engC.vSpcDown == True:
            for l in engC.vSpcBar:
                pygame.draw.rect(engC.surf, 'black', [613.5, engC.rect.centery-84, 18, 11])
                pygame.draw.rect(engC.surf, 'black', [613.5, engC.rect.centery+96, 18, 11])
                pygame.draw.rect(engC.surf, 'green', [581.5, engC.lVal+24.25, 15, drawHeight])
                pygame.draw.polygon(engC.surf, ALTPANELGREY, [(608.5, engC.rect.centery+105), (608.5, engC.rect.centery+115), (598.5, engC.rect.centery+110)])
                pygame.draw.polygon(engC.surf, 'green', [(608.5, engC.lVal+29.25-0.5), (608.5, engC.lVal+19.25), (598.5, engC.lVal+24.25)])
                txt_surf = txt_font.render(str(engC.l), True, 'green'); txt_rect = txt_surf.get_rect(center=(622.5, engC.rect.centery-80)); engC.surf.blit(txt_surf,txt_rect)
                txt_surf = txt_font.render(str(engC.l), True, 'green'); txt_rect = txt_surf.get_rect(center=(622.5, engC.rect.centery+100.5)); engC.surf.blit(txt_surf,txt_rect)
                #
                pygame.draw.rect(engC.surf, 'black', [110, engC.rect.centery+38, 40, 11])
                pygame.draw.rect(engC.surf, 'black', [166, engC.rect.centery+38.5, 180, 11])
                if energy_usage > 60:
                    color = 'red'
                elif energy_usage > 25:
                    color = 'yellow'
                else:
                    color = 'green'
                txt_surf = txt_font.render(str(energy_usage)+'%', True, color); txt_rect = txt_surf.get_rect(center=(140, engC.rect.centery+42.5)); engC.surf.blit(txt_surf,txt_rect)
                pygame.draw.rect(engC.surf, color, [166, engC.rect.centery+38.5, 35, 11])
                for i in inc_counter:
                    pygame.draw.rect(engC.surf, color, [179, engC.rect.centery+38.5, engC.rectw-8, 11])
                engC.rectw+=6
            if l < 0:
                engC.vSpcBar.append(l+1)
        pygame.draw.line(engC.surf, PANELGREY, (563.5, engC.rect.centery+117), (608.5, engC.rect.centery+117), 5)
        pygame.draw.line(engC.surf, PANELGREY, (540, engC.rect.centery-98), (618.5, engC.rect.centery-98), 5)
        h = engC.rect.centery+89.5; j = engC.rect.centery+115.75
        for i in range(0, 12, 1): # velocity level ticks on velocity bar 
            pygame.draw.line(engC.surf, PANELGREY, (575, h+5), (585, h+5))
            h-=21
        for i in range(0, 12, 1):
            pygame.draw.line(engC.surf, PANELGREY, (575, j), (585, j), 2)
            j-=42


        # Communication Console
        global message_index # place holder variable delete when reading events from a file
        commC = Panel.get_panel("Communication Console", panels)
        leftDisplay = commC.get_element("status1")
        rightDisplay = commC.get_element("status2")
        
        
        comB = commC.get_element('Combined')
        mesB = commC.get_element('Messages')
        repB = commC.get_element('Reports')

        def check_end_list():
            global message_index
            if message_index > len(messages) or message_index > len(sub_messages) or message_index > len(reports) or message_index > len(sub_reports):
                    message_index = 0

        def draw_text(surfs1:list, surfs2:list):
            y = 3
            for i in range(message_index):
                leftDisplay.surf.blit(surfs1[i], (3,y))
                rightDisplay.surf.blit(surfs2[i], (3,y))
                if y > leftDisplay.rect.height - 20:
                    y  = 3
                y += 13


        if commC.messageButton: 
            mesB.color = pygame.Color(BUTTONPRESSED)
            mesB.font = txt_font_small
            comB.color = pygame.Color(BACKGREY); repB.color = pygame.Color(BACKGREY)
            comB.font = txt_font; repB.font = txt_font

            if currentTime > (lastTime + 1000): # place holder statement delete when reading events from a file
                message_index += 1
                lastTime = currentTime
                check_end_list()
            draw_text(message_surfs, sub_message_surfs)
        elif commC.reportsButton:
            repB.color = pygame.Color(BUTTONPRESSED)
            repB.font = txt_font_small
            comB.color = pygame.Color(BACKGREY); mesB.color = pygame.Color(BACKGREY)
            comB.font = txt_font; mesB.font= txt_font

            if currentTime > (lastTime + 1000):
                message_index += 1
                lastTime = currentTime
                check_end_list()
            draw_text(report_surfs, sub_report_surfs)
        elif commC.comboButton:
            comB.color = pygame.Color(BUTTONPRESSED)
            comB.font = txt_font_small
            repB.color = pygame.Color(BACKGREY); mesB.color = pygame.Color(BACKGREY)
            repB.font = txt_font; mesB.font = txt_font

            if currentTime > (lastTime + 1000):
                message_index += 1
                lastTime = currentTime
                check_end_list()
            draw_text(message_surfs, report_surfs)
                

    # Combat Console
        showCombatC = True
        combatC = Panel.get_panel('Combat Console', panels)
        def draw_combat_console():
            transparent_surface = pygame.Surface(combatC.surf.get_size(), pygame.SRCALPHA); transparent_rect = transparent_surface.get_rect() 
            transparent_color = (255, 255, 255, 50); transparent_blue = (0, 0, 225, 125); transparent_orange = (255, 127, 80, 75); color = transparent_color; 
            
        # axis
            pygame.draw.line(combatC.surf, 'white', (15, 260), (465, 260), 2)
            pygame.draw.line(combatC.surf, 'white', (240, 35), (240, 485), 2)
            a = 25; #top 
            for i in range(0, 8, 1): 
                pygame.draw.line(combatC.surf, 'white', (225, 35+a), (256, 35+a), 2)
                a+=25
            a = 12.5; 
            for i in range(0, 8, 1):
                pygame.draw.line(combatC.surf, 'white', (230, 35+a), (251, 35+a))
                a+=25
            a = 25; #left
            for i in range(0, 8, 1):
                pygame.draw.line(combatC.surf, 'white', (15+a, 245), (15+a, 276), 2)
                a+=25
            a = 12.5; 
            for i in range(0, 8, 1):
                pygame.draw.line(combatC.surf, 'white', (15+a, 250), (15+a, 271))
                a+=25
            a = 25; # bottom
            for i in range(0, 8, 1): 
                pygame.draw.line(combatC.surf, 'white', (225, 260+a), (256, 260+a), 2)
                a+=25
            a = 12.5; 
            for i in range(0, 8, 1):
                pygame.draw.line(combatC.surf, 'white', (230, 285+a), (251, 285+a))
                a+=25
            a = 25; # right
            for i in range(0, 8, 1):
                pygame.draw.line(combatC.surf, 'white', (240+a, 245), (240+a, 276), 2)
                a+=25
            a = 12.5; 
            for i in range(0, 8, 1):
                pygame.draw.line(combatC.surf, 'white', (265+a, 250), (265+a, 271))
                a+=25
            
            # bottom buttons
        #menu
            if combatC.actMenu:
                pygame.draw.rect(combatC.surf, BUTTONPRESSED, [40, 510, 40, 20])
                txt_surf = txt_font_medium.render('Menu', True, 'black'); txt_rect = txt_surf.get_rect(center=(60, 520)); combatC.surf.blit(txt_surf,txt_rect)
        #grid 
            if combatC.actGrid:
                pygame.draw.rect(combatC.surf, BUTTONPRESSED, [90, 510, 40, 20])
                txt_surf = txt_font_medium.render('Grid', True, 'black'); txt_rect = txt_surf.get_rect(center=(110, 520)); combatC.surf.blit(txt_surf,txt_rect)
                cirX = 15; cirY = 35 # x-veryleft, y-verytop draw location of circles (dots of grid)
                for i in range(0, 9, 1): # topleft
                    pygame.draw.circle(transparent_surface, color, (cirX, cirY), 2, 2)
                    for i in range(0, 9, 1):
                        if cirY > 85 and cirX > 65:
                            color = transparent_blue
                            if (cirX == 90 and cirY <= 185) or (cirX == 115 and cirY <= 135) or (cirY == 110 and cirX < 185):
                                color = transparent_color
                            if (cirX > 140 and cirY > 160) or (cirX == 140 and cirY == 235) or (cirX == 215 and cirY == 160):
                                color = transparent_orange
                        pygame.draw.circle(transparent_surface, color, (cirX, cirY), 2, 2)
                        cirY+=25
                    color = transparent_color
                    cirY=35; cirX+=25
                cirX=15
                for i in range(0, 9, 1): # bottomleft
                    cirY=285
                    pygame.draw.circle(transparent_surface, color, (cirX, cirY), 2, 2)
                    for i in range(0, 9, 1):
                        if cirY > 260 and cirX > 65:
                            color = transparent_blue
                            if (cirX == 90 and cirY >= 335) or (cirX == 115 and cirY >= 385) or (cirY == 410 and cirX < 185) or cirY > 415:
                                color = transparent_color
                            if (cirX > 140 and cirY < 360) or (cirX == 140 and cirY == 285) or (cirX == 215 and cirY == 360):
                                color = transparent_orange
                        pygame.draw.circle(transparent_surface, color, (cirX, cirY), 2, 2)
                        cirY+=25
                    cirX+=25
                cirX=265; cirY=35
                for i in range(0, 9, 1): # topright
                    pygame.draw.circle(transparent_surface, color, (cirX, cirY), 2, 2)
                    for i in range(0, 9, 1):
                        if cirY > 85 and cirX < 415:
                            color = transparent_blue
                            if (cirX >= 315 and cirY < 135) or (cirX == 365 and cirY == 135) or (cirY < 210 and cirX == 390):
                                color = transparent_color
                            if (cirX <= 315 and cirY > 160) or (cirX == 265 and cirY == 160) or (cirX == 340 and cirY == 235):
                                color = transparent_orange
                        pygame.draw.circle(transparent_surface, color, (cirX, cirY), 2, 2)
                        cirY+=25
                    color = transparent_color
                    cirY=35; cirX+=25
                cirX=265
                for i in range(0, 9, 1): # bottomright
                    cirY=285
                    pygame.draw.circle(transparent_surface, color, (cirX, cirY), 2, 2)
                    for i in range(0, 9 ,1):
                        if cirY > 260 and cirX < 415:
                            color = transparent_blue
                            if (cirX >= 265 and cirY >= 435) or (cirX == 390 and cirY >= 360) or (cirY == 410 and cirX > 290) or (cirX == 365 and cirY == 385):
                                color = transparent_color
                            if (cirX <= 315 and cirY <= 335) or (cirX == 340 and cirY <= 285) or (cirX == 265 and cirY <= 360):
                                color = transparent_orange
                        pygame.draw.circle(transparent_surface, color, (cirX, cirY), 2, 2)
                        cirY+=25
                    cirX+=25
                pygame.draw.circle(combatC.surf, transparent_blue, (241, 261), 165, 2)
                pygame.draw.circle(combatC.surf, transparent_orange, (241, 261), 105, 2)
                combatC.surf.blit(transparent_surface,transparent_rect)
        #heading + move heading circle here
        # possibly make this into a function to compress and optimize code 
            if combatC.actHeading:
                pygame.draw.rect(combatC.surf, BUTTONPRESSED, [140, 510, 40, 20])
                txt_surf = txt_font_medium.render('Head', True, 'black'); txt_rect = txt_surf.get_rect(center=(160, 520)); combatC.surf.blit(txt_surf,txt_rect)
            # heading and stuff + add the small arrow headings on the ships N also move this into its button area later
            # headings are drawn as 4 separate arcs, they are meant to form a circle of text with headings every 15 degrees or so
                topLeftBox = 270; topRightBox = 0; bottomLeftBox = 180; bottomRightBox = 90; 
                drawX = 21.5; centerX = 50 
                drawY = 261; centerY = 300
                increment = 15
                start_angle = 180; end_angle = 270; angle_range = end_angle-start_angle; 
                draw_radius = 175; 
                label_amount = 5
                    # topleft
                pygame.draw.rect(combatC.surf, PANELGREY, [10, 255, 25, 13])
                txt_surf = txt_font.render(str(topLeftBox), True, 'black'); txt_rect = txt_surf.get_rect(center=(21.5, 261)); combatC.surf.blit(txt_surf,txt_rect)
                for i in range(label_amount):
                    angle_deg = start_angle+(i*angle_range/(label_amount-1))
                    angle_rad = math.radians(angle_deg)
                    drawX = centerX+draw_radius*math.cos(angle_rad)
                    drawY = centerY+draw_radius*math.sin(angle_rad)
                    txt_surf = txt_font.render(str(topLeftBox+increment), True, 'white'); txt_rect = txt_surf.get_rect(center=(drawX+150, drawY-87.5)); combatC.surf.blit(txt_surf,txt_rect)
                    increment+=15; 
                    # topright
                increment = 15
                pygame.draw.rect(combatC.surf, PANELGREY, [228.5, 30, 25, 13])
                txt_surf = txt_font.render(str(topRightBox), True, 'black'); txt_rect = txt_surf.get_rect(center=(240, 35.5)); combatC.surf.blit(txt_surf,txt_rect)
                for i in range(label_amount):
                    start_angle = 270; end_angle = 360; 
                    angle_deg = start_angle+(i*angle_range/(label_amount-1))
                    angle_rad = math.radians(angle_deg)
                    drawX = centerX+draw_radius*math.cos(angle_rad)
                    drawY = centerY+draw_radius*math.sin(angle_rad)
                    txt_surf = txt_font.render(str(topRightBox+increment), True, 'white'); txt_rect = txt_surf.get_rect(center=(drawX+230, drawY-87.5)); combatC.surf.blit(txt_surf,txt_rect)
                    increment+=15; 
                    # bottom left
                increment = 15
                pygame.draw.rect(combatC.surf, PANELGREY, [ 228.5, 477, 25, 13])
                txt_surf = txt_font.render(str(bottomLeftBox), True, 'black'); txt_rect = txt_surf.get_rect(center=(240, 482.5)); combatC.surf.blit(txt_surf,txt_rect)
                for i in range(label_amount):
                    start_angle = 90; end_angle = 180; 
                    angle_deg = start_angle+(i*angle_range/(label_amount-1))
                    angle_rad = math.radians(angle_deg)
                    drawX = centerX+draw_radius*math.cos(angle_rad)
                    drawY = centerY+draw_radius*math.sin(angle_rad)
                    txt_surf = txt_font.render(str(bottomLeftBox+increment), True, 'white'); txt_rect = txt_surf.get_rect(center=(drawX+150, drawY+7.5)); combatC.surf.blit(txt_surf,txt_rect)
                    increment+=15; 
                    # bottom right
                increment = 15
                pygame.draw.rect(combatC.surf, PANELGREY, [445, 255, 25, 13])
                txt_surf = txt_font.render(str(bottomRightBox), True, 'black'); txt_rect = txt_surf.get_rect(center=(457.5, 261)); combatC.surf.blit(txt_surf,txt_rect)
                for i in range(label_amount):
                    start_angle = 0; end_angle = 90; 
                    angle_deg = start_angle+(i*angle_range/(label_amount-1))
                    angle_rad = math.radians(angle_deg)
                    drawX = centerX+draw_radius*math.cos(angle_rad)
                    drawY = centerY+draw_radius*math.sin(angle_rad)
                    txt_surf = txt_font.render(str(bottomRightBox+increment), True, 'white'); txt_rect = txt_surf.get_rect(center=(drawX+230, drawY+7.5)); combatC.surf.blit(txt_surf,txt_rect)
                    increment+=15; 
        #target
            if combatC.actTarget:
                pygame.draw.rect(combatC.surf, BUTTONPRESSED, [190, 510, 40, 20])
                txt_surf = txt_font_medium.render('Target', True, 'black'); txt_rect = txt_surf.get_rect(center=(210, 520)); combatC.surf.blit(txt_surf,txt_rect)

        #line, i've got no clue what this is meant to be 
            if combatC.actLine:
                pygame.draw.rect(combatC.surf, BUTTONPRESSED, [ 240, 510, 40, 20])
                txt_surf = txt_font_medium.render('Line', True, 'black'); txt_rect = txt_surf.get_rect(center=(260, 520)); combatC.surf.blit(txt_surf,txt_rect) 
           
            pygame.draw.rect(combatC.surf, PANELGREY, [25, 30, 35, 20])
            txt_surf = txt_font_combatC.render('-', True, 'black'); txt_rect = txt_surf.get_rect(center=(42.5, 35)); combatC.surf.blit(txt_surf,txt_rect)
            pygame.draw.rect(combatC.surf, PANELGREY, [65, 30, 35, 20])
            txt_surf = txt_font_combatC.render('+', True, 'black'); txt_rect = txt_surf.get_rect(center=(82.5, 37.5)); combatC.surf.blit(txt_surf,txt_rect)
            # weapons 
            weapons = [
                ['Phaser'],
                ['Trp1'],
                ['Trp2'],
                ['ObltrPd'],
            ]
            combatC.weapons = weapons
            z = 487.5 # just random variable that hold x pos for draw to make for loop easier 
            pygame.draw.rect(combatC.surf, PANELGREYDARK, [485, 35, 165, 120])
            pygame.draw.rect(combatC.surf, (160,160,160), [485, 35, 165, 120], 2)
            for i in range(0, 4, 1): # draws rects that has 'weapons' drawn over 
                pygame.draw.rect(combatC.surf, 'white', [z, 40, 40, 15])
                pygame.draw.rect(combatC.surf, 'black', [z, 40, 40, 15], 2)
                z+=40
            z-=160
            if combatC.weaponIndex == 0: # lights up green on selected weapon 
                pygame.draw.rect(combatC.surf, 'green', [489.5, 42, 36, 11])
            elif combatC.weaponIndex == 1:
                pygame.draw.rect(combatC.surf, 'green', [529.5, 42, 36, 11])
            elif combatC.weaponIndex == 2:
                pygame.draw.rect(combatC.surf, 'green', [569.5, 42, 36, 11])
            elif combatC.weaponIndex == 3: 
                pygame.draw.rect(combatC.surf, 'green', [609.5, 42, 36, 11])
            for weap in weapons: # draws weapon names over color
                txt_surf = txt_font_medium.render(weap[0], True, 'black'); txt_rect = txt_surf.get_rect(center=(z+18, 46)); combatC.surf.blit(txt_surf,txt_rect)
                z+=40
            z = 550
            for i in range(0,2,1): # other boxes in weapons panel
                pygame.draw.rect(combatC.surf, 'black', [z, 60, 30, 15])
                pygame.draw.rect(combatC.surf, 'white', [z, 60, 30, 15], 1)
                z+= 65
            txt_surf = txt_font_medium.render('Bmb:', True, 'black'); txt_rect = txt_surf.get_rect(center=(535, 66)); combatC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_medium.render('N', True, 'green'); txt_rect = txt_surf.get_rect(center=(565, 66)); combatC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_medium.render('Qty:', True, 'black'); txt_rect = txt_surf.get_rect(center=(603, 66)); combatC.surf.blit(txt_surf,txt_rect)
            pygame.draw.rect(combatC.surf, 'green', [615, 85, 30, 13])
            pygame.draw.rect(combatC.surf, 'white', [615, 85, 30, 13], 1)
            txt_surf = txt_font_small.render('ECM', True, 'black'); txt_rect = txt_surf.get_rect(center=(630, 90.5)); combatC.surf.blit(txt_surf,txt_rect)

            weapon_labels = [
                ['Mode'],
                ['Settings'],
            ]        
            z=75
            for i in range(0,2,1):
                pygame.draw.rect(combatC.surf, 'cyan', [500, z, 40, 15])
                pygame.draw.rect(combatC.surf, 'black', [500, z, 40, 15], 1)
                txt_surf = txt_font_small.render(weapon_labels[i][0], True, 'black'); txt_rect = txt_surf.get_rect(center=(520, z+6)); combatC.surf.blit(txt_surf,txt_rect)
                z+= 30
            weapon_mode = [
                ['Auto      Manual'], # recolor specific characters in these strings; capitialized letters are recolored red
            ]
            weapon_settings = [
                ['Destroy      disaBle'], # strings are spaced weirdly like this because it helps with the centering when drawn (less lines of code to write)
                ['Standby      coNditional'],
            ]
            z-=60
            for setting in weapon_settings:
                txt_surf = txt_font_medium.render(setting[0], True, 'black'); txt_rect = txt_surf.get_rect(midleft=(510, z+52.5)); combatC.surf.blit(txt_surf,txt_rect)
                z+=15
            txt_surf = txt_font_medium.render('D', True, 'red'); txt_rect = txt_surf.get_rect(midleft=(510, 127.5)); combatC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_medium.render('S', True, 'red'); txt_rect = txt_surf.get_rect(midleft=(510, 142.5)); combatC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_medium.render('B', True, 'red'); txt_rect = txt_surf.get_rect(midleft=(591, 127.5)); combatC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_medium.render('N', True, 'red'); txt_rect = txt_surf.get_rect(midleft=(585, 142.5)); combatC.surf.blit(txt_surf,txt_rect)
            for mode in weapon_mode:
                txt_surf = txt_font_medium.render(mode[0], True, 'black'); txt_rect = txt_surf.get_rect(center=(547.5, 95)); combatC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_medium.render('A', True, 'red'); txt_rect = txt_surf.get_rect(center=(510, 95)); combatC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_medium.render('M', True, 'red'); txt_rect = txt_surf.get_rect(center=(556,95)); combatC.surf.blit(txt_surf,txt_rect)            
            
            # shields
            pygame.draw.rect(combatC.surf, PANELGREYDARK, [485, 160, 165, 170])
            pygame.draw.rect(combatC.surf, (160,160,160), [485, 160, 165, 170], 2)
            txt_surf = txt_font.render('Shields', True, 'black'); txt_rect = txt_surf.get_rect(center=(510, 170)); combatC.surf.blit(txt_surf,txt_rect)
            pygame.draw.rect(combatC.surf, (95,135,85), [620, 165, 25, 13])
            pygame.draw.rect(combatC.surf, (160,160,160), [620, 165, 25, 13], 1)
            txt_surf = txt_font_small.render('AAS', True, 'black'); txt_rect = txt_surf.get_rect(center=(631.5, 171)); combatC.surf.blit(txt_surf,txt_rect)
            
            def draw_shield_arcs(surface, color, center, inRadius, outRadius, sAng, eAng, inc): # change coloring so that it is like a 'gradient', i assume make the colors fade into each other or something along those lines
                if eAng < sAng: # eng angle < start angle
                    eAng += 360
                angles = [math.radians(a) for a in range(sAng, eAng+1, inc)]
                outPoints = [(center[0]+outRadius*math.cos(a), center[1]+outRadius*math.sin(a)) for a in angles] # points for outer radius of arc
                inPoints = [(center[0]+inRadius*math.cos(a), center[1]+inRadius*math.sin(a)) for a in reversed(angles)] # samething but for inner radius of arc
                allPoints = outPoints+inPoints
                if len(allPoints)>=3:
                    pygame.draw.polygon(surface, color, allPoints)
                    pygame.draw.polygon(surface, 'black', allPoints, 2)
            center = (567.5,230)
            angles = [(45, 135), (135, 225), (225, 315), (315, 45)]
            colors = ['dark green', 'green', 'forest green', 'red']
            shldNum = ['3', '2', '1', '4']
            shldAmount = ['1000', '2000', '500', '0']
            def draw_all_shld():
                for i in range(0,4,1):
                    s, e = angles[i] # s = start angle; e = end angle 
                    draw_shield_arcs(
                        surface=combatC.surf,
                        color=colors[i],
                        center=center,
                        inRadius=45, outRadius=60,
                        sAng=s, eAng=e,
                        inc=1 # increment by
                    )
                    mAng = (s+e)/2 # middle angle 
                    if e<s:
                        mAng = ((s+(e+360))/2)%360
                    mAng_rad = math.radians(mAng)
                    labelRadius = (45+57.5)/2
                    labelX = center[0]+labelRadius*math.cos(mAng_rad)
                    labelY = center[1]+labelRadius*math.sin(mAng_rad)
                    txt = f'{shldNum[i]}: {shldAmount[i]}'
                    txt_surf = txt_font.render(txt, True, 'black'); 
                    if shldNum[i] == '2': # rotates text to match how arc is drawn 
                        rotated_surf = pygame.transform.rotate(txt_surf, 90); rotated_rect = rotated_surf.get_rect(center=(labelX,labelY)); combatC.surf.blit(rotated_surf,rotated_rect)
                    elif shldNum[i] == '4':
                        rotated_surf = pygame.transform.rotate(txt_surf, -90); rotated_rect = rotated_surf.get_rect(center=(labelX,labelY)); combatC.surf.blit(rotated_surf,rotated_rect)
                    else:  
                        txt_rect = txt_surf.get_rect(center=(labelX,labelY))
                        combatC.surf.blit(txt_surf,txt_rect)
            combatC.surf.blit(combatCShldShip, (545, 172.5))
            draw_all_shld()
            x = 495; y = 292.5
            shld_button_labels = ['Auto', 'Manual', 'Battle Entry', 'Maximum']; 
            for i in range(0,4,1):
                pygame.draw.rect(combatC.surf, PANELGREY, [x, y, 55, 15])
                pygame.draw.rect(combatC.surf, (160,160,160), [x, y, 55, 15], 1)
                txt_surf = txt_font_small.render(shld_button_labels[i], True, 'black'); txt_rect = txt_surf.get_rect(center=(x+27.5,y+6)); combatC.surf.blit(txt_surf,txt_rect)
                x+=90
                if x > 585:
                    x = 495; y+=17.5
            if combatC.shldAuto:
                pygame.draw.rect(combatC.surf, BUTTONPRESSED, [495, 293.5, 53, 13])
                txt_surf = txt_font_small.render(shld_button_labels[0], True, 'black'); txt_rect = txt_surf.get_rect(center=(520, 298.5)); combatC.surf.blit(txt_surf,txt_rect)
                colors = ['forest green', 'forest green', 'dark green', 'forest green']
                shldAmount = ['500', '500', '1000', '500']
                draw_all_shld()
            if combatC.shldManual:
                pygame.draw.rect(combatC.surf, BUTTONPRESSED, [586, 293.5, 53, 13])
                txt_surf = txt_font_small.render(shld_button_labels[1], True, 'black'); txt_rect = txt_surf.get_rect(center=(611,298.5)); combatC.surf.blit(txt_surf,txt_rect)
                draw_all_shld()
            if combatC.shldBattleEntry:
                pygame.draw.rect(combatC.surf, BUTTONPRESSED, [495, 311, 53, 13])
                txt_surf = txt_font_small.render(shld_button_labels[2], True, 'black'); txt_rect = txt_surf.get_rect(center=(520, 316)); combatC.surf.blit(txt_surf,txt_rect)
                colors = ['forest green', 'dark green', 'green', 'dark green']
                shldAmount = ['500', '1000', '2000', '1000']
                draw_all_shld()
            if combatC.shldMaximum:
                pygame.draw.rect(combatC.surf, BUTTONPRESSED, [586, 311, 53, 13])
                txt_surf = txt_font_small.render(shld_button_labels[3], True, 'black'); txt_rect = txt_surf.get_rect(center=(611,316)); combatC.surf.blit(txt_surf,txt_rect)
                colors = ['green', 'green', 'green', 'green']
                shldAmount = ['2000', '2000', '2000', '2000']
                draw_all_shld()

            # weapon status & targeting 
            pygame.draw.line(combatC.surf, PANELGREY, (485, 330), (650, 330), 5)
            pygame.draw.rect(combatC.surf, PANELGREYDARK, [485, 333, 165, 30])
            pygame.draw.rect(combatC.surf, (160,160,160), [485, 333, 165, 30], 2)
            pygame.draw.line(combatC.surf, PANELGREY, (485, 365), (650, 365), 5)
            
            wn = ['Ph', 'T1', 'T2'] # weapon name 
            wm = ['Auto', 'Auto', 'Manual',] # wm is just separate weapon mode list

            x = 502.5
            for i in range(0,3,1):
                pygame.draw.rect(combatC.surf, 'green', [x, 338, 25, 5]) # shows weapon health i think
                pygame.draw.rect(combatC.surf, 'black', [x, 338, 25, 5], 1)
                pygame.draw.rect(combatC.surf, 'red',  [x, 342, 25, 13]) # shows selected weapon i think
                pygame.draw.rect(combatC.surf, 'black', [x, 342, 25, 13], 1)
                pygame.draw.rect(combatC.surf, PANELGREY, [x, 351, 25, 8]) # shows weapon mode
                pygame.draw.rect(combatC.surf, 'black', [x, 351, 25, 8], 1)
                txt_surf = txt_font_very_small.render(wn[i], True, 'black'); txt_rect = txt_surf.get_rect(center=(x+12.5, 355)); combatC.surf.blit(txt_surf,txt_rect)
                txt_surf = txt_font_very_small.render(wm[i], True, 'black'); txt_rect = txt_surf.get_rect(center=(x+12.5, 346.5)); combatC.surf.blit(txt_surf,txt_rect)
                #if weapons[i] == "Phaser":
                    # this part is meant to allow you to choose firing modes when 'x' weapon is selected 
                x+=35
            pygame.draw.rect(combatC.surf, 'cyan', [610, 338, 25, 21])
            pygame.draw.rect(combatC.surf, 'black', [610, 338, 25, 21], 1)
            txt_surf = txt_font_small.render('Cont', True, 'black'); txt_rect = txt_surf.get_rect(center=(621.5, 348)); combatC.surf.blit(txt_surf,txt_rect)
                #stuff above is the last of the weapons stuffs, just falls under targeting
                #stuff below is the actual targeting stuffs
            pygame.draw.rect(combatC.surf, ALTPANELGREY, [485, 369, 165, 30])
            pygame.draw.line(combatC.surf, PANELGREY, (485, 399), (650, 399), 2)
            pygame.draw.line(combatC.surf, PANELGREY, (485, 384), (650, 384), 1)
            x = 526
            for i in range(0,3,1):
                pygame.draw.line(combatC.surf, PANELGREY, (x, 384), (x, 500))
                x+=41
            pygame.draw.rect(combatC.surf, PANELGREYDARK, [585, 369, 50, 13])
            txt_surf = txt_font_small.render('Board', True, 'black'); txt_rect = txt_surf.get_rect(center=(610, 375)); combatC.surf.blit(txt_surf,txt_rect)
            target_data_labels = ['R.Pos', 'Brng', 'Vel.', 'Wpn']
            txt_surf = txt_font_small.render('Target Data', True, 'cyan'); txt_rect = txt_surf.get_rect(center=(510, 375)); combatC.surf.blit(txt_surf,txt_rect)
            x=505
            for i in range(0,4,1):
                txt_surf = txt_font_small.render(target_data_labels[i], True, 'cyan');  txt_rect = txt_surf.get_rect(center=(x, 391)); combatC.surf.blit(txt_surf,txt_rect)
                x+=42
            target_data = [
                ['(3, 2)', '90°', '.9¥', 'PTT'],
            ]
            for i in range(0,1):
                txt_surf = txt_font_small.render('             '.join(target_data[i]), True, 'green'); txt_rect = txt_surf.get_rect(center=(565, 408)); combatC.surf.blit(txt_surf,txt_rect)
                # 13 spaces when joining strings, or split each string into individual items in list for better spacing
            # this is to match the coloring
            txt_surf = txt_font_small.render('¥', True, 'red'); txt_rect = txt_surf.get_rect(center=(591, 408)); combatC.surf.blit(txt_surf,txt_rect)
            txt_surf = txt_font_small.render('PTT', True, 'red'); txt_rect = txt_surf.get_rect(center=(627, 408)); combatC.surf.blit(txt_surf,txt_rect)
            if combatC.targetBoard:
                #pygame.draw.rect(combatC.surf, PANELGREY, [495, 369, 100, 100])
                pygame.draw.rect(combatC.surf, BUTTONPRESSED, [585, 369, 50, 13])
                txt_surf = txt_font_small.render('Board', True, 'black'); txt_rect = txt_surf.get_rect(center=(610, 375)); combatC.surf.blit(txt_surf,txt_rect)
                combatC.surf.blit(buttonBoard, (485, 372))
            # assets on main display
        if showCombatC:
            draw_combat_console()
        combatC.surf.blit(mainDispShip, (218, 200))

    def event_listener(panels:list, events:pygame.event): # listens for all events
        primary = Panel.get_panel('Primary Display', panels); pri = primary.get_element('primary display')
        nav = Panel.get_panel('Navigation Console', panels); sm = Panel.get_panel('Star Map', panels)
        nav_display = Panel.get_panel(("Navigation Console"), panels).get_element("Navigation Video")
        engC = Panel.get_panel('Engineering Console', panels); i = 21; k = -1; l = -1
        commC = Panel.get_panel('Communication Console', panels)
        
        combatC = Panel.get_panel('Combat Console', panels); 

        # change keybinds to match actual keybinds of starfleet 2 
    # init new vars at very top of script and make global here
        global toggle_i, pressed_i, toggle_o, pressed_o, toggle_p, pressed_p  # for navigation console --> orbit data
        global toggle_l, pressed_l, toggle_sCol, pressed_sCol, toggle_quo, pressed_quo # navigation console --> star map
        global toggle_q, pressed_q, toggle_w, pressed_w # engineering console --> probes
        global toggle_d, pressed_d, toggle_f, pressed_f, toggle_g, pressed_g, toggle_h, pressed_h, toggle_j, pressed_j # combat console --> main display
        global toggle_rShift, pressed_rShift # combat console --> target data

        def handleToggle(event, key, key_state, toggle_flag): # this handles toggling on and off of button activated UIs 
            if event.type == pygame.KEYDOWN and event.key == key and not key_state['pressed']:
                toggle_flag['val'] = not toggle_flag['val']
                key_state['pressed'] = True
                return True
            if event.type == pygame.KEYUP and event.key == key:
                key_state['pressed'] = False
            return False 

        for event in events:
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                if event.type == QUIT or event.key == K_ESCAPE:
                    for video in pri.videos:
                        video.close()
                        pri.showCircles = False
            # toggle keys
                #nav console
                if handleToggle(event, pygame.K_i, pressed_i, toggle_i):
                    if toggle_i:
                        toggle_o['val'] = False; toggle_p['val'] = False
                    nav.navButtonUI1 = toggle_i['val']; nav.navButtonUI2 = toggle_o['val']; nav.navButtonUI3 = toggle_p['val']
                if handleToggle(event, pygame.K_o, pressed_o, toggle_o):
                    if toggle_o:
                        toggle_i['val'] = False; toggle_p['val'] = False 
                    nav.navButtonUI1 = toggle_i['val']; nav.navButtonUI2 = toggle_o['val']; nav.navButtonUI3 = toggle_p['val']
                if handleToggle(event, pygame.K_p, pressed_p, toggle_p):
                    if toggle_p:
                        toggle_i['val'] = False; toggle_o['val'] = False
                        nav_display.use_nav_videos(True)
                    else:
                        nav_display.reset_to_main_videos()
                    nav.navButtonUI1 = toggle_i['val']; nav.navButtonUI2 = toggle_o['val']; nav.navButtonUI3 = toggle_p['val']
                    
                    # star map
                if handleToggle(event, pygame.K_l, pressed_l,  toggle_l):
                    if toggle_l:
                        toggle_sCol['val'] = False; toggle_quo['val'] = False
                    sm.ButtonUI1 = toggle_l['val']; sm.ButtonUI2 = toggle_sCol['val']; sm.ButtonUI3 = toggle_quo['val']
                if handleToggle(event, pygame.K_SEMICOLON, pressed_sCol, toggle_sCol):
                    if toggle_sCol:
                        toggle_l['val'] = False; toggle_quo['val'] = False
                    sm.ButtonUI1 = toggle_l['val']; sm.ButtonUI2 = toggle_sCol['val']; sm.ButtonUI3 = toggle_quo['val']
                if handleToggle(event, pygame.K_QUOTE, pressed_quo, toggle_quo):
                    if toggle_quo:
                        toggle_l['val'] = False; toggle_sCol['val'] = False
                    sm.ButtonUI1 = toggle_l['val']; sm.ButtonUI2 = toggle_sCol['val']; sm.ButtonUI3 = toggle_quo['val']

                # eng console
                    # probes
                if handleToggle(event, pygame.K_q, pressed_q, toggle_q):
                    if toggle_q:
                        toggle_w['val'] = False
                    engC.ButtonUI1 = toggle_q['val']; engC.ButtonUI2 = toggle_w['val']
                if handleToggle(event, pygame.K_w, pressed_w, toggle_w):
                    if toggle_w:
                        toggle_q['val'] = False
                    engC.ButtonUI1 = toggle_q['val']; engC.ButtonUI2 = toggle_w['val']
                
                # combat console
                    # main display
                if handleToggle(event, pygame.K_d, pressed_d, toggle_d):
                    combatC.actMenu = toggle_d['val']
                if handleToggle(event, pygame.K_f, pressed_f, toggle_f):
                    combatC.actGrid = toggle_f['val']
                if handleToggle(event, pygame.K_g, pressed_g, toggle_g):
                    combatC.actHeading = toggle_g['val']
                if handleToggle(event, pygame.K_h, pressed_h, toggle_h):
                    combatC.actTarget = toggle_h['val']
                if handleToggle(event, pygame.K_j, pressed_j, toggle_j):
                    combatC.actLine = toggle_j['val']

                    # target data
                if handleToggle(event, pygame.K_RSHIFT, pressed_rShift, toggle_rShift):
                    combatC.targetBoard = toggle_rShift['val']




            # non-toggle keys
                # eng console
                    # velocity
            if event.type == pygame.KEYDOWN:
                if event.key == K_z:
                    if engC.k < 10:
                        engC.vHypUp = True; engC.vHypDown = False
                        engC.kVal-=i; engC.vHypBar.append(k+1)
                        k+=1; engC.k += 1.0
                    engC.energy_usage+=5
                if event.key == K_x:
                    if engC.k > 0:
                        engC.vHypUp = False; engC.vHypDown = True
                        engC.kVal+=i; engC.vHypBar.pop()
                        k-=1; engC.k -= 1.0
                    engC.energy_usage-=5
                if event.key == K_c:
                    if engC.l < 10:
                        engC.vSpcUp = True; engC.vSpcDown = False
                        engC.lVal-=i; engC.vSpcBar.append(l+1)
                        l+=1; engC.l += 1.0
                    engC.energy_usage+=3
                if event.key == K_v:
                    if engC.l > 0:
                        engC.vSpcDown = True; engC.vSpcUp = False
                        engC.lVal+=i; engC.vSpcBar.pop()
                        l-=1; engC.l -= 1.0
                    engC.energy_usage-=3

                    # damage - ship display
                if event.key == K_F1:
                    engC.CycleDamage.append(1)
                    engC.CycleDamage.pop(0)
                if event.key == K_F2:
                    engC.CycleDamage.append(2)
                    engC.CycleDamage.pop(0)
                if event.key == K_F3:
                    engC.CycleDamage.append(3)
                    engC.CycleDamage.pop(0)
                if event.key == K_F4:
                    engC.CycleDamage.append(4)
                    engC.CycleDamage.pop(0)
                
                # combat console
                    # weapon selection
                if event.key == K_RIGHT:
                    combatC.weaponIndex = (combatC.weaponIndex + 1) % len(combatC.weapons)
                if event.key == K_LEFT:
                    combatC.weaponIndex = (combatC.weaponIndex - 1) % len(combatC.weapons)

                    # shield mode
                if event.key == K_m:
                    combatC.shldAuto = True
                    combatC.shldManual = False
                    combatC.shldBattleEntry = False
                    combatC.shldMaximum = False
                if event.key == K_COMMA:
                    combatC.shldAuto = False
                    combatC.shldManual = True
                    combatC.shldBattleEntry = False
                    combatC.shldMaximum = False 
                if event.key == K_PERIOD:
                    combatC.shldAuto = False
                    combatC.shldManual = False
                    combatC.shldBattleEntry = True
                    combatC.shldMaximum = False
                if event.key == K_SLASH:
                    combatC.shldAuto = False
                    combatC.shldManual = False
                    combatC.shldBattleEntry = False
                    combatC.shldMaximum = True
                
                
                if event.key == K_9:
                    commC.messageButton = True
                    commC.reportsButton = False
                    commC.comboButton = False
                if event.key == K_0:
                    commC.messageButton = False
                    commC.reportsButton = True
                    commC.comboButton = False
                if event.key == K_MINUS:
                    commC.messageButton = False
                    commC.reportsButton = False
                    commC.comboButton = True

                # main display
                    # for this part use up&down arrow keys for the zoom in/out 


                if event.key == K_n:
                    pri.play_video()
                    pri.showCircles = True
                    #if display.playing == DeepSpace: #also add in changes for the mode (default is hyperspace)
                    #   display.showCircles = False 
# with toggle system, it is possible to rework this video playing stuff in the primary display in a way that it allows it to cycle through videos better also is now possible to make it so that circles of orbit in navigation show only when a specific video is playing i mean you can use the index of a video in a list, use if statement obviously to check index of viedeo then change variable for oribital circles 
        nav_display.update(events)
        #ncd.surf.blit()
        pri.update(events)

 
