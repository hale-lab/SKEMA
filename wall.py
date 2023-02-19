import Rhino.Geometry as rg

# define a wall object, this is only for straight wall.
class Wall:
    #constructor attributes for "wall" object.
    def __init__(self, base_curve, base_level, height):
        self.curve = base_curve
        self.level = str(base_level)
        self.height = height

    #method to make wall from input curve extrusion
    def makeWall(self):
        wall_set = []

        #note that polyline cannot be extruded, explode first into curve segments
        wall_curves = self.curve.DuplicateSegments()

        for wall_curve in wall_curves:
            if wall_curve.IsPlanar():
                wall = rg.Extrusion.Create(wall_curve, self.height, False)
                wall = wall.ToBrep()
                wall_set.append(wall)
            else :
                print("Wall is not planar!")

        walls = rg.Brep.JoinBreps(wall_set, 1.00)

        return walls
    
    #perform boolean difference to cut hole through wall
    def makeWallHole(self, walls, openings):
        opening_set = []
        walls_hole = []

        for opening in openings:
            opening_set.append(opening.ToBrep())

        for wall in walls:
            target_wall = wall
            for opening in opening_set:
                cut_hole = target_wall.Split(opening, 1.00)
                if len(cut_hole) > 1:
                    target_wall = cut_hole[-1]
                    #print("cut hole in wall!")
                else:
                    pass
                    #print("skip wall!")
            walls_hole.append(target_wall)
        #print("--end-of-turn--")
        return walls_hole

# create new wall instance.
wall_ = []
length_ = []
area_ = []
for i in range(0, len(_input)):
    wall = Wall(_input[i], _level, _height)
    # check for openings input, to create hole in walls.
    if _opening:
        wall_.append(wall.makeWallHole(wall.makeWall(), _opening))
        wall_[i] = wall_[i][0]
    else:
        wall_.append(wall.makeWall())
        wall_[i] = wall_[i][0]
    #calculate length and area
    length_.append(_input[i].GetLength())
    area_.append(rg.AreaMassProperties.Compute(wall_[i]).Area)

