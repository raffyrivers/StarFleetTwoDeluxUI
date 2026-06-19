# Star Fleet II Delux UI Showcase

## Notes
as of  7/15/25 there is no mouse control for this code, 
mouse control needs to be added for buttons 
ex. 'Combat Console' --> 'Shields' --> 'Auto', 'Manual', 'Battle Entry', 'Maximum'
and other buttons in consoles
for this version of the demo, UIs/GUIs are activated (displayed) via keybind, check initializations of panels or very bottom of panel for if statemnt blocks

## Requirements
```
python 3.12.*
pip3
ffmpeg
git 
```

<b> Ffmpeg needs to be installed manually on Windows ([INSTALL HERE](https://www.ffmpeg.org/download.html)) </b>

## Installation

```
git clone https://github.com/raffyrivers/StarFleetTwoDeluxUI.git

# Change directory
cd StarFleetTwoDeluxUI

# pip install -r requirements.txt

# Then run :)
python main.py 

```

## Installation in virtual environment
 
```

git clone https://github.com/raffyrivers/StarFleetTwoDeluxUI.git

# Change directory
cd StarFleetTwoDeluxUI

# Be sure to run python3.12 only!!!!
python -m venv /path/to/venvfolder

source /path/to/venvfolder/bin/activate

pip install -r requirements.txt

python main.py
```
