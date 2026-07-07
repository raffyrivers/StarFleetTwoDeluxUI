import os
import pygame
import importlib.util

os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()

root = r'c:\Users\gnf20\VS Code\StarFleetTwoDeluxUI'
spec = importlib.util.spec_from_file_location('main', os.path.join(root, 'main.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

cockpit = module.Cockpit()
cockpit.render([])
print('render ok')
