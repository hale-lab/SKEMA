import Rhino.Geometry as rg

# define a wall object, this is only for straight wall.
class Wall:
    #constructor attributes for "wall" object.
    def __init__(self, id, base_curve, base_level, height):
        self.id = str(id)
        self.level = str(base_level)
        self.length = base_curve.GetLength()
        self.height = height
        self.area = self.length * self.height

    #method to make wall from input curve extrusion
    def makeWall(self, base_curve):
        wall_curves = base_curve.DuplicateSegments()

        wall_3d = []
        for wall_curve in wall_curves:
            if wall_curve.IsPlanar():
                wall_3d.append(rg.Extrusion.Create(wall_curve, self.height, False))
            else :
                print("Wall is not planar!")
        return wall_3d

# create new wall instance.
wall = Wall(_id, _input, _level, _height)
wall_ = wall.makeWall(_input)

# OUTPUT variables.
identifier_ = wall.id
length_ = wall.length
area_ = wall.area
