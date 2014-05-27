#!/usr/bin/env python
"""
A simple example of an animated plot in matplotlib.  You can test the
speed of animation of various backends by running the script with the
'-dSomeBackend' flag

SC Aug 31 2005 mpl 0.83.2:
Here are some numbers from my system, where FPS is the frames rendered
per second

  GTK       29 FPS
  GTKAgg    18 FPS
  GTKCairo  15 FPS
  TkAgg     13 FPS
  QkAgg     13 FPS
"""
import time

import pylab as p

i=1

def on_click(event):
    global i
    line.set_ydata(p.sin(x+i/10.0))
    p.draw()
    i += 1

p.connect('button_press_event', on_click)

# turn interactive mode on for dynamic updates.  If you aren't in
# interactive mode, you'll need to use a GUI event handler/timer.
p.ion()

tstart = time.time()                 # for profiling
x = p.arange(0, 2*p.pi, 0.01)        # x-array
line, = p.plot(x, p.sin(x))

raw_input()

print 'FPS:' , 200/(time.time()-tstart)
