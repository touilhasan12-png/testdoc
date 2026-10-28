"""Render the TripoSR mesh in Blender; the mesh remains private."""
import bpy,os,json
from pathlib import Path
from mathutils import Vector
out=Path(os.environ['V5_OUT']);inp=Path(os.environ['V5_ROOT'])/'public/private'/'ship_triposr.glb'
if not inp.exists():raise RuntimeError('No TripoSR ship mesh in encrypted input')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(inp))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
if not objects:raise RuntimeError('No ship mesh imported')
coords=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
lo=Vector((min(v.x for v in coords),min(v.y for v in coords),min(v.z for v in coords)))
hi=Vector((max(v.x for v in coords),max(v.y for v in coords),max(v.z for v in coords)))
center=(lo+hi)*.5;s=4./max(hi-lo)
for o in objects:o.location-=center;o.scale*=s
bpy.ops.object.camera_add(location=(5.5,-7,4.0));cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=5.7;bpy.context.scene.camera=cam
for loc,energy,size in [((-3,-4,6),900,5),((4,3,4),500,4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);bpy.context.object.data.energy=energy;bpy.context.object.data.size=size
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=16;sc.render.film_transparent=True
sc.render.resolution_x=1024;sc.render.resolution_y=768;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.filepath=str(out/'ship_blender.png');bpy.ops.render.render(write_still=True)
(out/'blender_ship_status.json').write_text(json.dumps({'ok':True,'meshes':len(objects),'input':'TripoSR mesh','renderer':'Blender Cycles CPU','version':bpy.app.version_string},indent=2))
print('PASS Blender rendered the TripoSR mesh.',flush=True)
