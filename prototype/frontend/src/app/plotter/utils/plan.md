# Plotter Implementation Plan
## Configuration Attributes
- x-domain
- y-domain

## Initial Config
- x-domain : `-50 <= x <= 50`
- y-domain : `-50 <= y <= 50`

The Grid will be drawn with the help of x and y domains

## Thickness Vs Zooming factor
The thickness and zooming factor change linearly so the relationship can be found by creating two test points and creating a line
by using two points line equation<br>

(x1, y1) and (x2, y2)<br><br>

x -> **Zooming factor**<br>
y -> **Thickness of the lines**<br><br>

The spacing factor is invariable albeit the thickness will vary<br>

## Transformation
Transforming the points from x, y domain to canvas domain (i.e) {canvas.width, canvas.height}

## Operation Available

* Panning
* Zooming

While drawing the canvas, the panning depends on the zoom factor.<br>

## Architecture of Plotter
* Drawing (redraw/draw)
* Panning
* Zooming

Panning and Zooming changes x and y domain which fires the redraw function<br>


## Drawing(draw) 
This function will erase the whole canvas wherever called, and start to draw<br>

### Grid Drawing
The grid will be drawn by `x and y domain values` <br>

Mapping the domain values to the canvas domain to draw the lines of the grid<br>

Ex: consider,<br>
x and y domain - x => `(-50, 50), y =>(-50, 50)`<br>
canvas domain - x => `(0, 500), y => (0, 500)`<br>

We will create a linear function which maps the x, y domain of the function to the canvas domain <br>
(i.e) function domain --> canvas domain.<br>

Whenever the domain changes the remapping between them will happen and grid will be drawn.<br>

### Function Drawing
`Step 1` : Talking sample points from the function with even intervals.<br>
`Step 2` : The taken sample points are in the function domain it require changing to the canvas domain.<br>
`Step 3` : Draw lines between those sample points.<br>

## Zooming

### Choosing anchor
An **anchor** is a 2D coordinate in the current **canvas domain function domain**.<br>
Soon After the anchor is chosen, We need to reduce the x, y domain to have some value and after this the x, y domain values will be reduced by constant value.<br>

## Panning
Whenever the user drag he will start from a point in the canvas and end at someother point in that canvas
In so doing i got the start and end point this is the desired values of panning however this must be in the opposite because they are used to the comtemporary graphing tools
