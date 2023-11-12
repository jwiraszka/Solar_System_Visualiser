from random import random
import bpy

def create_sphere(radius, distance_to_sun, object_name):
    # instantiate a UV sphere with a given
    # radius, at distance from the sun (origin point)
    object = bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        location=(distance_to_sun, 0, 0),
        scale=(1, 1, 1)
    )
    
    # rename the object
    bpy.context.object.name = object_name
    # apply smoothing shader
    bpy.ops.object.shade_smooth()
    # return the object reference
    return bpy.context.object


def create_torus(radius, object_name):
    # instantiate a UV sphere with a given
    # radius, at distance of origin point (which is 0)
    object = bpy.ops.mesh.primitive_torus_add(
        location = (0, 0, 0),
        major_radius = radius,
        minor_radius = 0.1,
        major_segments = 60
    )
    
    # rename the object
    bpy.context.object.name = object_name
    # apply smoothing shader
    bpy.ops.object.shade_smooth()
    # return the object reference
    return bpy.context.object


def create_emission_shader(color, strength, mat_name):
    # create the new material resource
    mat = bpy.data.materials.new(mat_name)
    # enable the node graph edition mode
    mat.use_nodes = True
    
    # clear all starter nodes
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # add the emission node
    node_emission = nodes.new(type="ShaderNodeEmission")
    # input[0] is colour
    node_emission.inputs[0].default_value = color
    # input[1] is the strength
    node_emission.inputs[1].default_value = strength
    
    # add the output node
    node_output = nodes.new(type ="ShaderNodeOutputMaterial")
    
    # link the two nodes
    links = mat.node_tree.links
    link = links.new(node_emission.outputs[0], node_output.inputs[0])
    
    # return the material reference
    return mat


def delete_object(name):
    # find object by name
    if name in bpy.data.objects:
        object = bpy.data.objects[name]
        object.select_set(True)
        bpy.ops.object.delete(use_global = False)


def find_3dview_space():
    # find 3D view panel 
    area = None
    for a in bpy.data.window_managers[0].windows[0].screen.areas:
        if a.type == "VIEW_3D":
            area = a
              
    return area.spaces[0] if area else bpy.context.space_data


# set up scene settings
def setup_scene():
    # set black background
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
    # use EEVEE render engine and enable bloom effect
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.use_bloom = True
    # set animation start/end/current frames
    scene.frame_start = START_FRAME
    scene.frame_end = END_FRAME
    scene.frame_current = START_FRAME
    # get current 3D view
    space = find_3dview_space()
    # apply rendered shading mode and hide all background markings
    space.shading.type = "RENDERED"
    space.overlay.show_floor = False
    space.overlay.show_axis_x = False
    space.overlay.show_axis_y = False
    space.overlay.show_cursor = False
    space.overlay.show_object_origins = False


# constancts for animation
START_FRAME = 1
END_FRAME = 200

# will keep trach of planet velocity
count = 3

# lists containing all planet details, not including the sun
planet_names = ["Mercury", "Venus", "Earth", "Mars",
                "Jupiter", "Saturn", "Uranus", "Neptune"]
                
planet_radius = [1, 4, 4, 2.5, 17, 13, 7, 6]

# setup scene settings
setup_scene()


# clean scene and planet materials
delete_object("Sun")

for name in range(len(planet_names)):
    delete_object(planet_names[name])
    delete_object("Radius-" + planet_names[name])

for m in bpy.data.materials:
    bpy.data.materials.remove(m)


ring_mat = create_emission_shader(
    (1, 1, 1, 1), 1, "RingMat"
)


for n in range(len(planet_names)):
    name = planet_names[n]
    # set radius
    for r in range(len(planet_radius)):
        if n == r:  
            radius = planet_radius[r]
    # set a random distance to the origin point:
    # - an initial offset of 70 to get out of the sun's sphere
    # - a shift depending on the index of the planet
    distance = 60 + n * 40 + (random() * 4  - 2)
    
    # initialise planet with these parameters and name
    planet = create_sphere(radius, distance, name)
    planet_count = n
    
      
    planet.data.materials.append(
        create_emission_shader(
            (random(), random(), 1, 1), 2, "Radius-" + name
        )
    )
    
    # add the radius righ display to showcase orbit of each planet
    ring = create_torus(distance, "Radius-" + name)
    ring.data.materials.append(ring_mat)
    
    
    # set planet as active object
    bpy.context.view_layer.objects.active = planet
    planet.select_set(True)
    # set object origin at world origin (where the sun is)
    bpy.ops.object.origin_set(type = "ORIGIN_CURSOR", center = "MEDIAN")
    
    
    # set up planet animation
    planet.animation_data_create()
    planet.animation_data.action = bpy.data.actions.new(name="RotationAction")
    fcurve = planet.animation_data.action.fcurves.new(
        data_path="rotation_euler", index = 2
    )
    k1 = fcurve.keyframe_points.insert(
        frame = START_FRAME,
        value = 0
    )
    k1.interpolation = "LINEAR"
    k2 = fcurve.keyframe_points.insert(
        frame = END_FRAME,
        value = (count + random() * 2) * 3.41
    )
    k2.interpolation = "LINEAR"
    count = count - 0.4
    
    

# add the sun sphere
sun = create_sphere(40, 0, "Sun")
sun.data.materials.append(
    create_emission_shader(
        (1, 0.66, 0.08, 1), 10, "SunMat"
    )
)


#deselect all objects
bpy.ops.object.select_all(action = "DESELECT")
