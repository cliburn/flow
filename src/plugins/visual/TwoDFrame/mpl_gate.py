"""
This is an example to show how to build cross-GUI applications using
matplotlib event handling to interact with objects on the canvas

Adpated from http://matplotlib.sourceforge.net/examples/poly_editor.py
"""
import matplotlib
# matplotlib.use('WX')

from matplotlib.artist import Artist
try:
    from matplotlib.patches import Line2D
except ImportError:
    from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Rectangle #, Line2D
# from matplotlib.numerix.mlab import amin
# from matplotlib.numerix import sqrt, nonzero, equal, array, dot, float as Float, take
from numpy import sqrt, nonzero, equal, array, dot, float as Float, take
from numpy import amin
from matplotlib.mlab import dist_point_to_segment
from scipy import vectorize
from numpy import logical_not, logical_xor, logical_and, transpose

class acRectangle(Rectangle):
    """Just a rectangle that returns vertices in anti-clockwise order."""
    def __init__(self, *args, **kwargs):
        Rectangle.__init__(self, *args, **kwargs)

    def get_verts(self):
        """Return the vertices of the rectangle, in anticlockwise order."""
        x, y = self.get_x(), self.get_y()
        return ((x, y), (x+self.get_width(), y), 
                (x+self.get_width(), y+self.get_height()),
                (x, y+self.get_height()))

class PolygonInteractor(object):
    """
    An polygon editor.
    """

    showverts = True
    epsilon = 5  # max pixel distance to count as a vertex hit

    def __init__(self, parent, ax, poly):
        if poly.figure is None:
            raise RuntimeError('You must first add the polygon to a figure or canvas before defining the interactor')
        self.parent = parent
        self.ax = ax
        canvas = poly.figure.canvas
        self.poly = poly
        if not hasattr(self.poly, 'verts'):
            self.poly.verts = list(self.poly.get_verts())
        x, y = zip(*(self.poly.verts + self.poly.verts[:1]))
        # xpts = list(x) + [x[0]]
        # ypts = list(y) + [y[0]]
        self.line = Line2D(x, y, color='r', marker='o', markerfacecolor='r', animated=True)
        # self._update_line(poly)

        cid = self.poly.add_callback(self.poly_changed)
        self._ind = None # the active vert

        canvas.mpl_connect('draw_event', self.draw_callback)
        canvas.mpl_connect('button_press_event', self.button_press_callback)
        # canvas.mpl_connect('key_press_event', self.key_press_callback)
        canvas.mpl_connect('button_release_event', self.button_release_callback)
        canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
        self.canvas = canvas
        self.inside = False

    def PointInPoly(self, pt):
        """Return True if pt is in polygon defined by verts, False otherwise. Verts are in anticlockwise order.
        Adapted from http://www.acm.org/tog/GraphicsGems/gemsiv/ptpoly_haines/ptinpoly.c"""
        verts = self.poly.verts
        nverts = len(verts)
        v0 = verts[-2]
        v1 = verts[-1]
        yflag0 = v0[1] >= pt[1]
        inside = False        
        for j in range(nverts):
            yflag1 = v1[1] >= pt[1]
            if yflag0 != yflag1:
                if (((v1[1] - pt[1]) * (v0[0] - v1[0]) >= 
                     (v1[0] - pt[0]) * (v0[1] - v1[1])) == yflag1):
                    inside = not inside
            yflag0 = yflag1
            v0 = v1
            v1 = verts[j]
        return inside

    def PointsInPoly(self, pts):
        """Return True if pt is in polygon defined by verts, False otherwise. Verts are in anticlockwise order.
        Adapted from http://www.acm.org/tog/GraphicsGems/gemsiv/ptpoly_haines/ptinpoly.c"""
        verts = self.poly.verts
        nverts = len(verts)
        v0 = verts[-2]
        v1 = verts[-1]
        yflag0 = v0[1] >= pts[1,:]

        inside = array([0]*pts.shape[1], 'bool')
        for j in range(nverts):
            yflag1 = v1[1] >= pts[1,:]
            candidates = yflag0 != yflag1
            flips = (((v1[1] - pts[1,:]) * (v0[0] - v1[0]) >= 
                      (v1[0] - pts[0,:]) * (v0[1] - v1[1])) == yflag1)
            inside[logical_and(candidates, flips)] = logical_not(inside[logical_and(candidates, flips)])
            yflag0 = yflag1
            v0 = v1
            v1 = verts[j]
        return inside


    def draw_callback(self, event):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def poly_changed(self, poly):
        'this method is called whenever the polygon object is called'
        # only copy the artist props to the line (except visibility)
        vis = self.line.get_visible()
        Artist.update_from(self.line, poly)
        self.line.set_visible(vis)  # don't use the poly visibility state

    def get_ind_under_point(self, event):
        'get the index of the vertex under point if within epsilon tolerance'
        x, y = zip(*self.poly.verts)
        xt, yt = array(x), array(y)
        ax = self.ax.axis()
        scalex, scaley = \
            event.x/(event.xdata-ax[0]), event.y/(event.ydata-ax[2])

        # display coords
        # API changed for new versions of matplotlib
        # xt, yt = self.poly.get_transform().numerix_x_y(x, y)
        # xt, yt = self.poly.get_transform().transform(array(self.poly.verts)).T
        d = sqrt((scalex*(xt-event.xdata))**2 + (scaley*(yt-event.ydata))**2)
        indseq = nonzero(equal(d, amin(d)))
        ind = indseq[0]

        if d[ind]>=self.epsilon:
            ind = None

        return ind

    def button_press_callback(self, event):
        'whenever a mouse button is pressed'
        x, y = event.xdata, event.ydata

        if self.showverts and event.inaxes and event.button == 1:
            self._ind = self.get_ind_under_point(event)
        if self._ind:
            return

        # allow a drag if click within gate
        if self.PointInPoly((x, y)):
            self.inside = True
            self.start = x, y
            return

    def button_release_callback(self, event):
        'whenever a mouse button is released'
        # first do drag event
        if self.inside:
            self.inside = False
            x, y = event.xdata, event.ydata
            translate = array([x, y]) - self.start
            for i in range(len(self.poly.verts)):
                self.poly.verts[i] = tuple(array(self.poly.verts[i]) + translate)
            linepts = self.poly.verts + self.poly.verts[:1]
            self.line.set_data(zip(*linepts))

            self.canvas.restore_region(self.background)
            self.ax.draw_artist(self.poly)
            self.ax.draw_artist(self.line)
            self.canvas.blit(self.ax.bbox)
            # self.canvas.draw()
            self.parent.draw()
#             sz = array(self.parent.parent.GetClientSize()) + \
#                 self.parent.parent.offset
#             self.parent.parent.SetClientSize(sz)
#             self.parent.parent.offset *= -1

            return

        if not self.showverts: return
        if event.button != 1: return
        self._ind = None
        self.parent.draw()
#         sz = array(self.parent.parent.GetClientSize()) + \
#             self.parent.parent.offset
#         self.parent.parent.SetClientSize(sz)
#         self.parent.parent.offset *= -1

    def motion_notify_callback(self, event):
        'on mouse movement'
        if not self.showverts: return
        if self._ind is None: return
        if event.inaxes is None: return
        if event.button != 1: return
        x,y = event.xdata, event.ydata
        self.poly.verts[self._ind] = x,y
        
        linepts = self.poly.verts + self.poly.verts[:1]
        # self.line.set_data(zip(*self.poly.verts))
        self.line.set_data(zip(*linepts))

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

if __name__ == '__main__':
#     from pylab import *
# 
#     fig = figure()
#     # circ = CirclePolygon((.5, .5), .5, animated=True)
#     rect = acRectangle((11.25, 11.25), 5.5, 5.5, animated=True)
# 
#     ax = subplot(111)
#     # ax.add_patch(circ)
#     ax.add_patch(rect)
#     # circ.set_visible(False)
#     rect.set_visible(False)
#     # p = PolygonInteractor(ax, circ)
#     p = PolygonInteractor(ax, rect)
# 
#     ax.add_line(p.line)
#     ax.set_title('Click and drag a point to move it')
#     ax.set_xlim((10,21))
#     ax.set_ylim((10,21))
#     show()
# 
    pts = array([[1.001,1],[0.5,0.5]]).T
    print '>', PointsInPoly([[0,0], [1,0], [1,1], [0,1]], pts)
