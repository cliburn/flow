from pylab import *
import numpy.random as random

ion()
ax = subplot(111)
data = random.normal(5, 2, (1000, 2))
dots, = ax.plot(data[:,0], data[:,1], 'o')

draw()

ax.axhline(5, c='r', animated=True)
ax.axvline(5, c='r')

def on_move(event):
    # get the x and y pixel coords
    x, y = event.x, event.y

    if event.inaxes:
        print 'data coords', event.xdata, event.ydata

def on_click(event):
    x, y = event.xdata, event.ydata

    if event.inaxes and event.button==1:
        print 'data coords', event.xdata, event.ydata

    line1 = axhline(y, c='r')
    line2 = axvline(x, c='r')

    ax.lines = [dots, line1, line2]

    q1 = len(data[(data[:,0]<x)*(data[:,1]<y)])
    q2 = len(data[(data[:,0]<x)*(data[:,1]>y)])
    q3 = len(data[(data[:,0]>x)*(data[:,1]<y)])
    q4 = len(data[(data[:,0]>x)*(data[:,1]>y)])

    ax.set_title('bottom left=%d, top left=%d, top right=%d, bottom right=%d' % (q1, q2, q3, q4))

    draw()

connect('button_press_event', on_click)

raw_input()
