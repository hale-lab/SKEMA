import Rhino.Geometry as rg
import math

#function to define swing 2d system movement / translation.
def swing_translation(leaf_size, opening_ratio):
    #find the swing interval domain, make 2d swing line only for swing type
    swing_domain = rg.Arc(rg.Plane.WorldXY, leaf_size, math.radians(90) * opening_ratio)
    swing_line = rg.ArcCurve(swing_domain)

    #get points to construct the swing module.
    swing_startPt = rg.Point3d(0, 0, 0)
    swing_endPt = swing_line.PointAtEnd

    return swing_startPt, swing_endPt, swing_line

#function to define awning 2d system movement / translation.
def awning_translation(hinge_type, leaf_size, opening_ratio):
    #find the awning interval domain, condition for top / bottom hung.
    startPt = rg.Point3d(0, 0, 0)
    endPt = rg.Point3d(0, 0, leaf_size)

    if hinge_type == "bottom hung" :
        awning_domain = rg.Arc(rg.Plane.WorldYZ, startPt, leaf_size, math.radians(90) * (1.00 - opening_ratio))
        awning_startPt = startPt
    else :
        awning_domain = rg.Arc(rg.Plane.WorldYZ, endPt, leaf_size, math.radians(-90) * (1.00 - opening_ratio))
        awning_startPt = endPt

    #get end point to construct the swing module.
    awning_line = rg.ArcCurve(awning_domain)
    awning_endPt = awning_line.PointAtEnd

    return awning_startPt, awning_endPt

#function to define folding 2d system movement / translation.
def fold_translation(leaf_size, opening_ratio):
    #find the folding interval domain    
    fold_domain = rg.Arc(rg.Plane.WorldXY, leaf_size, math.radians(90))

    #get s, m and e points to construct the folding module.
    fold_startPt = rg.Point3d(0, 0, 0)
    fold_midPt = fold_domain.PointAt(opening_ratio)

    #find the opening angle.
    #define the base plane.
    plane = rg.Plane.WorldXY

    #calculate hypotenuse
    x = (fold_midPt - plane.Origin) * plane.XAxis - (fold_startPt - plane.Origin) * plane.XAxis
    y = (fold_midPt - plane.Origin) * plane.YAxis - (fold_startPt - plane.Origin) * plane.YAxis
    hypotenuse = math.atan2(y, x)

    #then calc the cosine of the opening angle, to get the adjacent.
    adjacent = abs((math.cos(hypotenuse))) * leaf_size
    fold_endPt = rg.Point3d(adjacent * 2, 0, 0)

    return fold_startPt, fold_midPt, fold_endPt

#function to define sliding 2d system movement / translation.
def slide_translation(leaf_size, leaf_dup_n, opening_ratio):
    start_pt = rg.Point3d(0, 0, 0)
    end_pt = rg.Point3d(leaf_size * leaf_dup_n, 0, 0)
    dir = rg.Vector3d(end_pt.X - start_pt.X, end_pt.Y - start_pt.Y, end_pt.Z - start_pt.Z)
    translation = dir * (1.00 - opening_ratio)
    return translation

#function to mirror panels, if operation is double or multiple panels.
def mirror_panel(width, panel_group):
    #create mirror plane and move to object ctr, mirror transform object.
    planeYZ = rg.Plane.WorldYZ
    to_ctr = rg.Transform.Translation(rg.Vector3d(width/2, 0, 0))
    planeYZ.Transform(to_ctr)
    mirror = rg.Transform.Mirror(planeYZ)
            
    #then mirror the fold system.
    mirrored_group = []
    for panel in panel_group:
        mirrored_panel = panel.DuplicateShallow()
        mirrored_panel.Transform(mirror)
        mirrored_group.append(mirrored_panel)
            
    return mirrored_group

class Opening:
    #constructor attributes for opening template.
    def __init__(self, input_unit):
        #get DW unit specs information from ids
        check_unit = str.split(input_unit, "-")

        self.type = check_unit[0]
        self.operation = check_unit[1]
        self.size = str.split(check_unit[-1], "/")
        self.width = float(self.size[0]) / 100
        self.height = float(self.size[1]) / 100
        self.num_panels = int(self.size[-1])

        #for windows, add sill height information.
        if self.type == "W":
            self.offset = float(self.size[2]) / 100  
        else :
            self.offset = 0

    #method to prepare base opening sizing.
    def setup(self):
        self.opening_width = rg.LineCurve(rg.Point3d(0, 0, 0), rg.Point3d(self.width, 0, 0))
        self.opening_height = rg.LineCurve(rg.Point3d(0, 0, 0), rg.Point3d(0, 0, self.height)) 

    #method to create opening frame 3d geometry.
    def makeFrame(self):
        frame_side = self.opening_height.DuplicateCurve()
        frame_top = self.opening_width.DuplicateCurve()
        frame_side.Translate(self.width, 0, 0)
        frame_top.Translate(0, 0, self.height)

        frame = []
        if self.type == "W":
            make_frame = rg.Curve.JoinCurves([self.opening_width, self.opening_height, frame_side, frame_top])
            frame.append(make_frame[0])
        else :
            make_frame = rg.Curve.JoinCurves([self.opening_height, frame_side, frame_top])
            frame.append(make_frame[0])

        self.frame_3d = frame

    #method to create opening hole 3d geometry.
    def makeHole(self):
        hole = []
        make_hole = rg.Extrusion.Create(self.opening_width, self.height, False)
        hole.append(make_hole)
        self.hole_3d = hole

    #specific 'make' method to suit swing system.
    def makeSwing(self, opening_ratio):
        #check opening operation type.
        if self.operation == "swingDbl":
            self.num_panels = 2
            mirror = True
        else :
            self.num_panels = 1
            mirror = False

        #define the leaf size.
        swing_leaf_size = (self.width / self.num_panels)

        #construct swing module
        swing_start, swing_end, swing_line = swing_translation(swing_leaf_size, opening_ratio)
        swing_leaf = rg.LineCurve(swing_start, swing_end)
        swing_2d = [swing_leaf, swing_line]

        #build the swing system (swing 3d)
        swing_3d = []
        swing_3d.append(rg.Extrusion.Create(swing_leaf, self.height, False))

        #for double swing, mirror the swing system to the other side.
        if mirror is True:
            swing_2d_mirrored = mirror_panel(self.width, swing_2d)
            swing_3d_mirrored = mirror_panel(self.width, swing_3d)
            self.panel_2d = swing_2d + swing_2d_mirrored
            self.panel_3d = swing_3d + swing_3d_mirrored
        else :
            self.panel_2d = swing_2d
            self.panel_3d = swing_3d

    #specific 'make' method to suit double folding system.
    def makeFolding(self, opening_ratio):
        #check opening operation type.
        if self.operation == "foldingDbl":
            divisor = 4
            checkOddEven = (self.num_panels / 2) % 2
            mirror = True
        else :
            divisor = 2
            checkOddEven = self.num_panels % 2
            mirror = False
            
        #define the leaf size
        fold_leaf_size = (self.width / self.num_panels)
        
        #construct folding module from the s, m and e points.
        fold_2d = []
        fold_startPt, fold_midPt, fold_endPt = fold_translation(fold_leaf_size, opening_ratio)

        for i in range(0, int(math.ceil(self.num_panels / divisor))):
            startPt_n = rg.Point3d(fold_startPt.X + (i * fold_endPt.X), fold_startPt.Y, fold_startPt.Z)
            midPt_n = rg.Point3d(fold_midPt.X + (i * fold_endPt.X), fold_midPt.Y, fold_midPt.Z)
            endPt_n = rg.Point3d(fold_endPt.X + (i * fold_endPt.X), fold_endPt.Y, fold_endPt.Z)
            fold_leaf1 = rg.LineCurve(startPt_n, midPt_n)
            fold_leaf2 = rg.LineCurve(midPt_n, endPt_n)
            fold_2d.append(fold_leaf1)
            fold_2d.append(fold_leaf2)

        #check condition for odd/even n panel division, then build the folding system (folding 3d)
        fold_3d = []
        if checkOddEven == 0:
            for fold_leaf in fold_2d:
                fold_3d.append(rg.Extrusion.Create(fold_leaf, self.height, False))
        else :
            fold_2d.pop(-1)
            for fold_leaf in fold_2d:
                fold_3d.append(rg.Extrusion.Create(fold_leaf, self.height, False))

        #for double folding, mirror the fold system to the other side.
        if mirror is True:
            fold_2d_mirrored = mirror_panel(self.width, fold_2d)
            fold_3d_mirrored = mirror_panel(self.width, fold_3d)
            self.panel_2d = fold_2d + fold_2d_mirrored
            self.panel_3d = fold_3d + fold_3d_mirrored
        else :
            self.panel_2d = fold_2d
            self.panel_3d = fold_3d

    #specific 'make' method to suit double sliding system.
    def makeSliding(self, opening_ratio):
        #check opening operation type.
        if self.operation == "slidingDbl":
            divisor = 2
            mirror = True
        else :
            divisor = 1
            mirror = False

        #define leaf base geometry.
        slide_leaf_size = self.width / self.num_panels
        slide_leaf = rg.LineCurve(rg.Point3d(0, 0, 0), rg.Point3d(slide_leaf_size, 0, 0))

        #construct sliding module by leaf duplication according to num_panels.
        slide_2d = []
            #append the fixed leaf as first module.
        slide_2d.append(slide_leaf)
            #duplicate leaf to num_panels
        for i in range(1, int(math.ceil(self.num_panels / divisor))):
            slide_dup = slide_leaf.DuplicateCurve()
            slide_dup.Translate(slide_translation(slide_leaf_size, i, opening_ratio))
            #offset the module to account for leaf thickness.
            slide_dup_offset = slide_dup.Offset(rg.Plane.WorldXY, i * 0.025, 0, 0)
            slide_2d.append(slide_dup_offset[0])

        #build the sliding system from the modules (slide 3d).
        slide_3d = []
        for slide in slide_2d:
            slide_3d.append(rg.Extrusion.Create(slide, self.height, False))

        #for double sliding, mirror the fold system to the other side.
        if mirror is True:
            slide_2d_mirrored = mirror_panel(self.width, slide_2d)
            slide_3d_mirrored = mirror_panel(self.width, slide_3d)
            self.panel_2d = slide_2d + slide_2d_mirrored
            self.panel_3d = slide_3d + slide_3d_mirrored
        else :
            self.panel_2d = slide_2d
            self.panel_3d = slide_3d

    #specific 'make' method to suit awning system.
    def makeAwning(self, opening_ratio):
        #check opening operation type.
        if self.operation == "awningBH":
            self.num_panels = 1
            awning_hinge = "bottom hung"
        else :
            self.num_panels = 1
            awning_hinge = "top hung"

        #define the leaf size.
        awning_leaf_size = self.height

        #construct awning module
        awning_2d = []
        awning_2d.append(self.opening_width)
        awning_startPt, awning_endPt = awning_translation(awning_hinge, awning_leaf_size, opening_ratio)
        awning_leaf = rg.LineCurve(awning_startPt, awning_endPt)

        #build the awning system (awning 3d).
        awning_3d = []
        awning_3d.append(rg.Extrusion.Create(awning_leaf, self.width, False))

        self.panel_2d = awning_2d
        self.panel_3d = awning_3d

    #method to flip and place created 3d geometry onto target location.
    def place(self, flip_status, target_pts):
        #group the frame and panels as one unit
        if self.panel_3d:
            self.unit = self.frame_3d + self.hole_3d + self.panel_3d + self.panel_2d
        else :
            self.unit = self.frame_3d + self.hole_3d

        #create mirror plane and move to object ctr, mirror transform object.
        planeXZ = rg.Plane.WorldZX
        planeYZ = rg.Plane.WorldYZ
        to_ctr = rg.Transform.Translation(rg.Vector3d(self.width/2, 0, self.height/2))
        planeXZ.Transform(to_ctr)
        planeYZ.Transform(to_ctr)

        #create orient transform object.
        target = rg.LineCurve(target_pts[0], target_pts[1])
        base_plane = rg.Plane(rg.Point3d(0, 0, 0), self.opening_width.TangentAtEnd, self.opening_height.TangentAtEnd)
        target_plane = rg.Plane(target.PointAtStart, target.TangentAtEnd, rg.Vector3d(0, 0, 1))
        orient = rg.Transform.PlaneToPlane(base_plane, target_plane)

        for component in self.unit:
            #flip the unit first, if needed.
            if flip_status == 1:
                mirror = rg.Transform.Mirror(planeYZ)
                component.Transform(mirror)
            elif flip_status == 3: 
                mirror = rg.Transform.Mirror(planeXZ)
                component.Transform(mirror)
            elif flip_status == 2:
                mirror = rg.Transform.Mirror(planeXZ)
                component.Transform(mirror)
                mirror = rg.Transform.Mirror(planeYZ)
                component.Transform(mirror)
            else:
                pass
            
            #place unit to correct location, in preparation for exporting to aperture.
            component.Transform(orient)
            component.Translate(0, 0, self.offset)

    #method to export opening area(correctly scaled) as BEM aperture.
    def exportBEM(self):
        #find centroid from each opening.
        get_ctr = rg.AreaMassProperties.Compute(self.hole_3d)
        opening_ctr = get_ctr.Centroid

        #export to aperture for BEM usage.
        scale = rg.Transform.Scale(opening_ctr, 0.99)
        export = self.hole_3d[0].DuplicateShallow()
        export.Transform(scale)

        return export

