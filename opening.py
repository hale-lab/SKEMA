import sys

#create a function to add path to rhino library, if not exist.
def check_path(script_path):
    if not script_path in sys.path:
        sys.path.append(script_path)
    print(sys.path)

check_path("/Users/benny/Documents/Project/SKEMA")

from opening_RC import Opening

# 1. create new opening instance.
new_opening = Opening(_id)
# 2. setup basic sizes for the new opening instance.
new_opening.setup()
# 3. create the new opening instance frame
new_opening.makeFrame()
# 3. create the new opening instance hole
new_opening.makeHole()

# 5. define d/w operation type, to create the new opening instance panels.
if new_opening.operation == "swingSgl" or new_opening.operation == "swingDbl":
    new_opening.makeSwing(_opening_ratio)
elif new_opening.operation == "slidingSgl" or new_opening.operation == "slidingDbl":
    new_opening.makeSliding(_opening_ratio)
elif new_opening.operation == "foldingSgl" or new_opening.operation == "foldingDbl":
    new_opening.makeFolding(_opening_ratio)
elif new_opening.operation == "awningTH" or new_opening.operation == "awningBH":
    new_opening.makeAwning(_opening_ratio)
else:
    pass

# 6. place the new opening instance onto correct project locations.
new_opening.place(_flip, _location)

# OUTPUT variables.
openingType_ = new_opening.operation
openingFrame_ = new_opening.frame_3d
openingPanel_ = new_opening.panel_3d
opening2D_ = new_opening.panel_2d
opening3D_ = new_opening.frame_3d + new_opening.panel_3d

# ADDITIONAL STEPS TO CUT HOLES ONTO HOST WALLS.
openingInWall_ = new_opening.hole_3d

# ADDITIONAL STEPS TO EXPORT CREATED OPENING INTO BEM.
aperture_ = new_opening.exportBEM()