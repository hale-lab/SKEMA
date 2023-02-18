import Rhino
import Rhino.Geometry as rg
import ghpythonlib.treehelpers as tree
import scriptcontext as sc

#create a function to partition a list
def PartitionList(list, segment):
    list = [list[i : i + segment] for i in range(0, len(list), segment)]
    return list

# set context to Rhino document (or if you want to access RhinoDoc functions)
sc.doc = Rhino.RhinoDoc.ActiveDoc

#variables
ref_blocks = []
name = []
count = []
id_ = []
location_ = []

#get block geometry from Rhino document.
docs_blocks = sc.doc.InstanceDefinitions.GetList(False)

#get d/w referenced blocks from the document.
for ref_block in docs_blocks:
    if ref_block.Name[0] == 'D' and ref_block.UseCount() > 0:
        ref_blocks.append(ref_block.GetReferences(0))
        name.append(ref_block.Name)
        count.append(ref_block.UseCount())
    elif ref_block.Name[0] == 'W' and ref_block.UseCount() > 0:
        ref_blocks.append(ref_block.GetReferences(0))
        name.append(ref_block.Name)
        count.append(ref_block.UseCount())
    elif ref_block.Name[0] == 'O' and ref_block.UseCount() > 0:
        ref_blocks.append(ref_block.GetReferences(0))
        name.append(ref_block.Name)
        count.append(ref_block.UseCount())
    else:
        pass

#get referenced blocks names from the document.
for i in range(0, len(name)):
    for j in range(0, count[i]):
        id_.append(name[i])

id_ = tree.list_to_tree(PartitionList(id_, 1), True)

#explode and get geometries from docs referenced blocks.
for blockgroup in ref_blocks:
    for block in blockgroup:
        explode = block.Explode(False)
        geo = explode[0]
        xform = explode[-1]
        
        for i in range(0, len(geo)):
            geo[i].Geometry.Transform(xform[i])
            location_.append(geo[i].Geometry)

#filter by geometry type to get only points.
for item in location_:
    if item.ObjectType != rg.Point(rg.Point3d(0,0,0)).ObjectType:
        location_.remove(item)

#convert nested list to data tree.
location_ = tree.list_to_tree(PartitionList(location_, 2), True)

# set context back to GH document.
sc.doc = ghdoc
