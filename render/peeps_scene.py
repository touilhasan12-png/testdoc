# Open Peeps (CC0) داخل Blender: تُستورد ملفات SVG كمنحنيات، تُملأ وتُبسط، ثم تُحرّك وتُرندر.
import bpy, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[argv.index("--out") + 1] if "--out" in argv else "frames"
FRAMES = int(argv[argv.index("--frames") + 1]) if "--frames" in argv else 240
HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
try:
    bpy.ops.preferences.addon_enable(module="io_curve_svg")
except Exception as e:
    print("addon enable failed:", e)

scene = bpy.context.scene
scene.frame_start, scene.frame_end = 1, FRAMES
scene.render.fps = 24
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
scene.render.image_settings.file_format = "PNG"
scene.render.engine = "BLENDER_WORKBENCH"
sh = scene.display.shading
sh.light = "FLAT"
sh.color_type = "OBJECT"
sh.background_type = "WORLD"
sh.show_shadows = False
world = bpy.data.worlds.new("sky")
world.color = (0.75, 0.9, 1.0)
scene.world = world
scene.display.render_aa = "8"

def import_svg(path):
    before = set(bpy.data.objects)
    bpy.ops.import_curve.svg(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    return new

def make_peep(path, name, x):
    objs = import_svg(path)
    curves = [o for o in objs if o.type == "CURVE"]
    print(name, "imported curves:", len(curves), "other:", [o.type for o in objs if o.type != "CURVE"])
    for o in curves:
        o.data.dimensions = "2D"
        o.data.fill_mode = "BOTH"
        o.data.extrude = 0.01
    bpy.ops.object.select_all(action="DESELECT")
    for o in curves:
        o.select_set(True)
    bpy.context.view_layer.objects.active = curves[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = name
    # ضبط الحجم: ارتفاع الشخصية 2.4 وحدة، وقدماها على الأرض
    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    h = max(v.z for v in bb) - min(v.z for v in bb) or max(v.y for v in bb) - min(v.y for v in bb)
    s = 2.4 / h
    obj.scale = (s, s, s)
    bpy.context.view_layer.update()
    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    minz = min(v.z for v in bb)
    obj.location = (x, 0, -minz)
    obj.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.view_layer.update()
    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    print(name, "bbox z:", min(v.z for v in bb), max(v.z for v in bb), "y:", min(v.y for v in bb), max(v.y for v in bb))
    obj.color = (1, 1, 1, 1)
    return obj

ground = None
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
ground = bpy.context.object
ground.color = (0.5, 0.85, 0.55, 1)

bpy.ops.object.camera_add(location=(0, -12, 1.4), rotation=(math.radians(90), 0, 0))
cam = bpy.context.object
cam.data.lens = 50
scene.camera = cam

p1 = make_peep(os.path.join(HERE, "assets", "peep1.svg"), "peep1", -3.0)
p2 = make_peep(os.path.join(HERE, "assets", "peep2.svg"), "peep2", 3.0)

# حركة بسيطة: دخول من الجانب وارتداد وتمايل
for f in range(1, FRAMES + 1):
    scene.frame_set(f)
    t = (f - 1) / FRAMES
    p1.location.x = -6.0 + 3.0 * min(1.0, t * 2)
    p1.location.z = p1.location.z
    p1.keyframe_insert("location", frame=f)
    p2.location.x = 6.0 - 3.0 * min(1.0, t * 2)
    p2.keyframe_insert("location", frame=f)
    p1.rotation_euler.z = 0.04 * math.sin(f * 0.2)
    p1.keyframe_insert("rotation_euler", frame=f)

scene.frame_set(1)
for f in range(1, FRAMES + 1):
    scene.frame_set(f)
    scene.render.filepath = os.path.join(OUT, f"frame_{f:04d}.png")
    bpy.ops.render.render(write_still=True)
    print("rendered", f, flush=True)
