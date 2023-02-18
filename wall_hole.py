import Rhino.Geometry as rg

#perform boolean difference to cut hole through wall
wall_set = []
opening_set = []

for wall_srf in wall_srfs:
    wall_set.append(wall_srf.ToBrep())
for opening_srf in opening_srfs:
    opening_set.append(opening_srf.ToBrep())

host_set = rg.Brep.JoinBreps(wall_set, 1.00)

wall_fixed = []
for host in host_set:
    target_wall = host
    for opening in opening_set:
        cut_hole = target_wall.Split(opening, 1.00)
        if len(cut_hole) > 1:
            target_wall = cut_hole[-1]
            print("cut hole in wall!")
        else:
            pass
            print("skip wall!")
    wall_fixed.append(target_wall)
    print("--end-of-turn--")
    