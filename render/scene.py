# مشهد ثلاثي الأبعاد: شخصيتان بمفاصل FK حقيقية، إحداهما تمشي والأخرى تلوّح.
# يُشغَّل داخل Blender بلا واجهة: blender -b -P render/scene.py -- --out frames
import bpy, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[argv.index("--out") + 1] if "--out" in argv else "frames"
os.makedirs(OUT, exist_ok=True)

FRAMES = 240          # 10 ثوانٍ عند 24 إطاراً في الثانية
FPS = 24
WALK_RATE = 0.112     # طور المشي لكل إطار
LEG_AMP = 0.35        # زاوية الساق (راديان)
ARM_AMP = 0.45        # زاوية الذراع أثناء المشي

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = FRAMES
scene.render.fps = FPS
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = "PNG"

# محرك خفيف وسريع مناسب للرسم المسطح الكرتوني
scene.render.engine = "BLENDER_WORKBENCH"
sh = scene.display.shading
sh.light = "STUDIO"
sh.color_type = "OBJECT"
sh.show_shadows = True
sh.shadow_intensity = 0.35
sh.background_type = "WORLD"
scene.render.film_transparent = False
scene.display.render_aa = "8"
world = bpy.data.worlds.new("sky")
world.color = (0.62, 0.86, 1.0)
scene.world = world

# ---------- أدوات بناء ----------
def set_color(o, rgb):
    o.color = (rgb[0], rgb[1], rgb[2], 1.0)
    return o

def sphere(name, r, loc, rgb, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=24, ring_count=12)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    return set_color(o, rgb)

def box(name, size, loc, rgb):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = size
    return set_color(o, rgb)

def limb(name, p1, p2, r, rgb):
    a, b = Vector(p1), Vector(p2)
    v = b - a
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=v.length, vertices=18,
                                        location=(a + b) / 2)
    o = bpy.context.object
    o.name = name
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = v.normalized().to_track_quat("Z", "Y")
    return set_color(o, rgb)

def pivot(name, loc, parent=None):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=loc, radius=0.08)
    e = bpy.context.object
    e.name = name
    if parent is not None:
        attach(e, parent)
    return e

def attach(child, parent):
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()

# ---------- بناء شخصية ----------
def build_character(prefix, hip_xyz, shirt, pants, hair, skin, shoe):
    x, y, z = hip_xyz
    hip = pivot(prefix + "_hip", (x, y, z))

    # الجذع والرأس (يتبعان الورك)
    torso = box(prefix + "_torso", (0.34, 0.26, 0.7), (x, y, z + 0.6), shirt)
    attach(torso, hip)
    pelvis = box(prefix + "_pelvis", (0.36, 0.28, 0.26), (x, y, z + 0.02), pants)
    attach(pelvis, hip)
    neck = limb(prefix + "_neck", (x, y, z + 0.92), (x + 0.02, y, z + 1.05), 0.07, skin)
    attach(neck, hip)
    head = sphere(prefix + "_head", 0.27, (x + 0.02, y, z + 1.35), skin)
    attach(head, hip)
    hair_o = sphere(prefix + "_hair", 0.285, (x - 0.07, y, z + 1.42), hair, scale=(1.0, 1.0, 0.85))
    attach(hair_o, hip)
    nose = sphere(prefix + "_nose", 0.07, (x + 0.27, y, z + 1.33), skin, scale=(1.0, 0.8, 0.8))
    attach(nose, hip)
    eye = sphere(prefix + "_eye", 0.035, (x + 0.2, y - 0.2, z + 1.4), (0.05, 0.05, 0.08))
    attach(eye, hip)

    legs, arms = {}, {}
    for s, side in (("L", -1), ("R", 1)):
        yy = y + side * 0.12
        hj = pivot(f"{prefix}_hipj{s}", (x, yy, z), hip)
        knee_pos = (x, yy, z - 0.85)
        ankle_pos = (x, yy, z - 1.72)
        limb(f"{prefix}_thigh{s}", (x, yy, z), knee_pos, 0.1, pants)
        attach(bpy.context.object, hj)
        kn = pivot(f"{prefix}_knee{s}", knee_pos, hj)
        limb(f"{prefix}_shin{s}", knee_pos, ankle_pos, 0.085, pants)
        attach(bpy.context.object, kn)
        an = pivot(f"{prefix}_ankle{s}", ankle_pos, kn)
        f = box(f"{prefix}_foot{s}", (0.34, 0.16, 0.1), (x + 0.08, yy, z - 1.82), shoe)
        attach(f, an)
        legs[s] = (hj, kn, an)

        sj = pivot(f"{prefix}_shoulder{s}", (x, y + side * 0.2, z + 1.0), hip)
        el_pos = (x + 0.02, y + side * 0.2, z + 0.5)
        hand_pos = (x + 0.06, y + side * 0.2, z + 0.2)
        limb(f"{prefix}_upper{s}", (x, y + side * 0.2, z + 1.0), el_pos, 0.075, shirt)
        attach(bpy.context.object, sj)
        ej = pivot(f"{prefix}_elbow{s}", el_pos, sj)
        limb(f"{prefix}_fore{s}", el_pos, hand_pos, 0.065, skin)
        attach(bpy.context.object, ej)
        hd = sphere(f"{prefix}_hand{s}", 0.075, hand_pos, skin)
        attach(hd, ej)
        arms[s] = (sj, ej)
    return hip, legs, arms

def key(o, frame, rot=None, loc=None):
    if rot is not None:
        o.rotation_euler = rot
        o.keyframe_insert("rotation_euler", frame=frame)
    if loc is not None:
        o.location = loc
        o.keyframe_insert("location", frame=frame)

# ---------- الأرض والكاميرا والإضاءة ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -0.12))
ground = bpy.context.object
set_color(ground, (0.55, 0.85, 0.5))

bpy.ops.object.camera_add(location=(0, -17.5, 2.0), rotation=(math.radians(84), 0, 0))
cam = bpy.context.object
cam.data.lens = 52
scene.camera = cam

# ---------- الشخصيتان ----------
walker, wl, wa = build_character("walker", (-3.6, 0, 1.8),
                                 (0.97, 0.45, 0.12), (0.12, 0.23, 0.55),
                                 (0.25, 0.12, 0.04), (0.99, 0.85, 0.72), (0.1, 0.1, 0.12))
waver, rl, ra = build_character("waver", (3.2, 0, 1.8),
                                (0.5, 0.2, 0.9), (0.1, 0.35, 0.3),
                                (0.07, 0.07, 0.08), (0.95, 0.8, 0.66), (0.1, 0.1, 0.12))
waver.rotation_euler = (0, 0, math.pi)   # يواجه الاتجاه المعاكس

# ---------- حركة المشي للشخصية الأولى ----------
for f in range(1, FRAMES + 1):
    scene.frame_set(f)
    t = f - 1
    ph = WALK_RATE * t
    progress = t / (FRAMES - 1)
    x = -3.6 + 5.0 * progress
    bob = 0.03 * abs(math.sin(ph))
    key(walker, f, loc=(x, 0, 1.8 + bob))
    for s, side in (("L", 1), ("R", -1)):
        p = ph + (0 if s == "L" else math.pi)
        hj, kn, an = wl[s]
        thigh = -LEG_AMP * math.sin(p)
        shin = thigh + (-0.9 * max(0.0, math.cos(p)) * 0.6)
        key(hj, f, rot=(0, thigh, 0))
        key(kn, f, rot=(0, shin - thigh, 0))   # الركبة نسبةً للفخذ
        key(an, f, rot=(0, -shin, 0))          # تبقى القدم مسطحة على الأرض
        sj, ej = wa[s]
        arm = ARM_AMP * math.sin(p + math.pi) * 0.9
        key(sj, f, rot=(0, arm, 0))
        key(ej, f, rot=(0, -0.45 - 0.2 * max(0.0, math.cos(p)), 0))

# ---------- التلويح للشخصية الثانية ----------
for f in range(1, FRAMES + 1):
    scene.frame_set(f)
    t = f / FPS
    sj, ej = ra["R"]
    key(sj, f, rot=(0, 2.7 + 0.25 * math.sin(t * 9), 0))
    key(ej, f, rot=(0, -0.35 + 0.5 * math.sin(t * 9 + 1), 0))
    for s in ("L",):
        hj, kn, an = rl[s]
        key(hj, f, rot=(0, 0.03 * math.sin(t * 3), 0))
    key(waver, f, loc=(3.2, 0, 1.8 + 0.02 * math.sin(t * 2)))

# ---------- الإخراج ----------
scene.frame_set(1)
for f in range(1, FRAMES + 1):
    scene.frame_set(f)
    scene.render.filepath = os.path.join(OUT, f"frame_{f:04d}.png")
    bpy.ops.render.render(write_still=True)
    print("rendered", f, flush=True)
