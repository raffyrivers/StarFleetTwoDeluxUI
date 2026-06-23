# Star Fleet II Deluxe Cockpit UI

A pygame command screen modeled on the Krellan battlecruiser interface from
Star Fleet II Deluxe. Fourteen console panels show navigation, science, combat,
engineering, strategic, security, and communication readouts. Every on-screen
button responds to both mouse clicks and a keyboard shortcut.

## Running

```
pip install -r requirements.txt
python main.py
```

The window opens fullscreen. Press F11 to switch to a window, Esc to quit.

Video playback is optional. If pyvidplayer2 and ffmpeg are not installed, the
primary and navigation displays render an animated starfield and everything
else works the same.

## Layout

The interface draws to a fixed 1920x1080 canvas and scales to the display with
letterboxing, so the proportions hold on any screen size. Mouse coordinates are
mapped back through that scale, so clicks land on the right button regardless of
resolution.

Panels:

- Navigation Console: orbital display, system map, nav view selector
- Science Console: long and short range scope
- Primary Display: main viewscreen
- Status Indicators: ten alert lamps and target distance
- Navigation: current course and target readout
- Star Map: mercator, nav, and war map selector
- Computer Display: mission query and ship status
- Data: ship stores and complement
- Combat Console: weapons, shields, and fire grid
- Strategic Command Console: fleet orders and order queue
- Engineering Console: probe control, damage, energy
- Communication Console: message feed
- Security Console: deck status and prisoner roster
- Commanders Log: standing orders

## Controls

```
Esc            close help or quit
F1 / Ctrl+H    toggle control help
F11            toggle fullscreen and windowed
Mouse click    activate any button
1-8            latch top alert indicators
i o p          navigation console views
l ; '          star map views
q w            engineering probe views
z x            raise and lower hyperspace velocity
c v            raise and lower normal space velocity
F2-F5          set ship damage level 1-4
Ctrl+1-4       fallback damage keys for keyboards with media F-keys
d f g h j      combat overlays
m , . /        shield modes
Left Right     select weapon
9 0 -          communication feed
n              cycle primary display clip
Right Shift    target board
SNAP button    save current cockpit screenshot to snapshots/
```

If pressing an F-key changes system volume or mute, the keyboard is sending a
media key instead of a function key. Use Fn+F-key, enable Fn Lock/F-lock, or use
the Ctrl fallback shortcuts above.

## Files

```
main.py       window, scaling, input routing, frame loop
cockpit.py    panel layout and per panel build and draw
widgets.py    Panel, Button, Text, Display, StatusBar
video.py      video displays with starfield fallback
state.py      ship state
core.py       palette, fonts, asset loading, text fitting
assets/       images and video clips
snapshots/    local screenshots, ignored by git
```

Ship values (24 torpedoes, 4000 power units, 1000 tons supplies, 150 shock
troops, c-factor 8 hyperspace) follow the Star Fleet II training manual.
