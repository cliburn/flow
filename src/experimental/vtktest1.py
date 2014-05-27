from pylab import *
from vtk_pylab import *

def func3(x,y):
  return (1- x/2 + x**5 + y**3)*exp(-x**2-y**2)

dx, dy = 0.025, 0.025
x = arange(-3.0, 3.0, dx)
y = arange(-3.0, 3.0, dy)
X, Y = meshgrid(x,y)
Z = func3(X,Y)

font = {'fontname'   : 'Times',
        'color'      : 'r',
        'fontweight' : 'normal',
        'fontsize'   : 10}

#figure(figsize=(6,4))

if 1:
    ax = subplot(221)
    title('mesh using VTK', font, fontsize=14, color='r')
    text(80, 0.65, 'rf. pcolor_demo', font, color='w')
    mesh(X,Y,Z, 0)
    vtkRotX(-45)
    vtkRender()
    vtkImage()
    imshow(im,None)
    axis('off')

if 1:
    ax = subplot(222)
    title('mesh colored using VTK', font, fontsize=14, color='r')
    text(80, 0.65, 'rf. pcolor_demo', font, color='w')
    vtkClear()
    mesh(X,Y,Z, 1)
#    vtkRotX(-45)
    vtkRender()
    vtkImage()
    imshow(im,None)
    axis('off')

if 1:
    ax = subplot(223)
    title('plot3 using VTK', font, fontsize=14, color='r')
    vtkClear()
    dt = pi/50.0
    t = arange(0.0, 10*pi, dt)
    plot3(sin(t),cos(t),t)
    vtkRotX(-70)
    vtkPerspective(0)
#    grid(0)
    vtkRender()
    vtkImage()
    imshow(im,None)
    axis('off')

#savefig('vtkfig1')
show()
