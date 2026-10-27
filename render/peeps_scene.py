# Open Peeps (CC0) ثنائية الأبعاد، محرّكة داخل Blender.
# الشخصيات تبقى مسطحة في مستوى واحد، والكاميرا متعامدة (Orthographic) فلا يظهر أي عمق.
import bpy, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[argv.index("--out") + 1] if "--out" in argv else "frames"
FRAMES = int(argv[argv.index("--frames") + 1]) if "--frames" in argv else 240
HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.preferences.addon_enable(module="io_curve_svg")

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
sh.show_object_outline = False
world = bpy.data.worlds.new("sky")
world.color = (0.75, 0.9, 1.0)
scene.world = world
scene.display.render_aa = "8"

# كاميرا متعامدة تنظر إلى الأمام: لا منظور، فتبدو الشخصيات مسطحة
bpy.ops.object.camera_add(location=(0, -20, 1.5), rotation=(math.radians(90), 0, 0))
cam = bpy.context.object
cam.data.type = "ORTHO"
cam.data.ortho_scale = 8.0
scene.camera = cam

# الأرض: شريط أخضر أمام الشخصيات
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.6))
ground = bpy.context.object
ground.scale = (60, 1, 0.6)
ground.color = (0.55, 0.85, 0.5, 1)

def import_peep(path, name, x):
    before = set(bpy.data.objects)
    bpy.ops.import_curve.svg(filepath=path)
    curves = [o for o in bpy.data.objects if o not in before and o.type == "CURVE"]
    for o in curves:
        o.data.dimensions = "2D"
        o.data.fill_mode = "BOTH"
        o.data.extrude = 0.0
    bpy.ops.object.select_all(action="DESELECT")
    for o in curves:
        o.select_set(True)
    bpy.context.view_layer.objects.active = curves[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = name
    # الشخصية تُدار بمحور ثابت، ونحدد مركزها الهندسي بالضبط
    obj.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.view_layer.update()
    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    h = max(v.z for v in bb) - min(v.z for v in bb)
    k = 3.0 / h
    obj.scale = (k, k, k)
    bpy.context.view_layer.update()
    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    cx = (max(v.x for v in bb) + min(v.x for v in bb)) / 2
    cy = (max(v.y for v in bb) + min(v.y for v in bb)) / 2
    minz = min(v.z for v in bb)
    obj.location = (x - cx, -cy, -minz)
    bpy.context.view_layer.update()
    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    print(name, "x:", round(min(v.x for v in bb), 2), round(max(v.x for v in bb), 2),
          "y:", round(min(v.y for v in bb), 2), round(max(v.y for v in bb), 2),
          "z:", round(min(v.z for v in bb), 2), round(max(v.z for v in bb), 2), flush=True)
    obj.color = (1, 1, 1, 1)
    return obj

p1 = import_peep(os.path.join(HERE, "assets", "peep1.svg"), "peep1", -3.2)
p2 = import_peep(os.path.join(HERE, "assets", "peep2.svg"), "peep2", 0.0)
p3 = import_peep(os.path.join(HERE, "assets", "peep3.svg"), "peep3", 3.2)

# حركة 2D: قفزة خفيفة وتمايل، وانزلاق الشخصية الأولى إلى مكانها
base1 = p1.location.copy()
for f in range(1, FRAMES + 1):
    t = f - 1
    scene.frame_set(f)
    hop = abs(math.sin(t * 0.25)) * 0.12
    p1.location = (base1.x + max(0.0, 1.0 - t / 45.0) * -4.0, base1.y, base1.z + hop)
    p1.keyframe_insert("location", frame=f)
    p1.rotation_euler = (math.radians(90), 0, math.radians(3) * math.sin(t * 0.08))
    p1.keyframe_insert("rotation_euler", frame=f)
    p2.location.z = p2.location.z
    p3.location = (p3.location.x, p3.location.y, p3.location.z + 0.06 * abs(math.sin(t * 0.2)))
    p3.keyframe_insert("location", frame=f)

scene.frame_set(1)
for f in range(1, FRAMES + 1):
    scene.frame_set(f)
    scene.render.filepath = os.path.join(OUT, f"frame_{f:04d}.png")
    bpy.ops.render.render(write_still=True)
    print("rendered", f, flush=True)
