#!/usr/bin/env python3
""" Experimenting with CNC machining toolpaths. """

import sys

import ezdxf
import matplotlib.pyplot as plt    # type: ignore

import dxf
import geometry


def print_entity(entity: ezdxf.entities.DXFGraphic, indent: int = 0):
    """ Display some debug information about a DXF file. """
    dxf_attributes = ["start", "end", "center", "radius", "count"]
    collection_attributes = ["points"]
    other_attributes = ["virtual_entities"]

    padding = " " * indent
    print(f"{padding}{entity}")
    print(f"{padding}  type: {entity.dxftype()}")

    for attribute in dxf_attributes:
        if hasattr(entity.dxf, attribute):
            print(f"{padding}  {attribute}: {getattr(entity.dxf, attribute)}")

    for attribute in collection_attributes:
        if hasattr(entity, attribute):
            generator = getattr(entity, attribute)
            with generator() as collection:
                print(f"{padding}  {attribute}: {collection}")

    for attribute in other_attributes:
        if hasattr(entity, attribute):
            got = getattr(entity, attribute)
            print(f"{padding}  {attribute}: {list(got())}")

def main(argv):
    if len(argv) < 2:
        print("Incorrect command line arguments.")
        print(f"Use:\n   {argv[0]} FILENAME [STEP_sIZE]")
        sys.exit(0)
    filename = argv[1]

    try:
        dxf_data = ezdxf.readfile(filename)
    except IOError:
        print(f'Not a DXF file or a generic I/O error.')
        sys.exit(2)
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted DXF file.')
        sys.exit(3)

    if len(argv) > 2:
        step_size = float(argv[2])
    else:
        step_size = 1

    print(f"{filename=}\n{step_size=}\n")

    modelspace = dxf_data.modelspace()

    #print()
    #for entity in modelspace:
    #    print_entity(entity)
    #    print()

    shape = dxf.dxf_to_polygon(modelspace)

    # Display shape to be cut
    x, y = shape.exterior.xy
    plt.plot(x, y, c="blue", linewidth=2)

    for interior in shape.interiors:
        x, y = interior.xy
        plt.plot(x, y, c="orange", linewidth=2)

    # Generate tool path.
    toolpath = geometry.ToolPath(shape, step_size, geometry.ArcDir.CW, generate = True)
    timeslice = 20  # ms
    for index, arc_count in enumerate(toolpath._get_arcs(timeslice)):
        #print(index, arc_count)

        # You have access to toolpath.path here.
        # Draw what's there so far; it will ot change position in the buffer.
        pass

    # Call toolpath.calculate_path() to scrap the existing and regenerate toolpath.

    # Display voronoi edges.
    for vertex, edges in toolpath.voronoi.vertex_to_edges.items():
        for edge_index in edges:
            edge = toolpath.voronoi.edges[edge_index]
            x = []
            y = []
            for point in edge.coords:
                x.append(point[0])
                y.append(point[1])
            plt.plot(x, y, c="red", linewidth=2)
            plt.plot(x[0], y[0], 'x', c="red")
            plt.plot(x[-1], y[-1], 'x', c="red")

    # Display path.
    for element in toolpath.path:
        if type(element).__name__ == "Arc":
            x, y = element.path.xy
            if element.debug:
                plt.plot(x, y, c=element.debug, linewidth=1)
            else:
                plt.plot(x, y, c="green", linewidth=1)
            #plt.plot(element.origin.x, element.origin.y, "o")

        elif type(element).__name__ == "Line":
            #continue
            x, y = element.path.xy
            if element.safe:
                #plt.plot(x, y, linestyle='--', c="blue", linewidth=1)
                pass
            else:
                plt.plot(x, y, c="orange", linewidth=1)

    #plt.plot(toolpath.start_point.x, toolpath.start_point.y, 'o', c="black")
    #for arc_centre, edge_count in toolpath.voronoi.dilated_vertexes.items():
    #    if edge_count > 10:
    #        plt.plot(arc_centre[0], arc_centre[1], 'o', c="black")

    plt.gca().set_aspect('equal')
    plt.show()

if __name__ == "__main__":
    main(sys.argv)
