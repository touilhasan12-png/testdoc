"""Import real Iberian country polygons with BlenderGIS and export a 3D layer."""
import bpy, os, sys, json, traceback
from mathutils import Vector
from math import radians
from pathlib import Path

out=Path(os.environ['V5_OUT']); addon=Path(os.environ['BLENDERGIS_DIR']); shape=Path(os.environ['IBERIA_SHP']);sys.path.insert(0,str(addon.parent))
sys.path.append('/usr/lib/python3/dist-packages')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
import BlenderGIS
BlenderGIS.register()
result=bpy.ops.importgis.shapefile('EXEC_DEFAULT',filepath=str(shape),shpCRS='EPSG:4326',separateObjects=True)
objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and len(o.data.vertices)>2]
if not objects:raise RuntimeError('BlenderGIS imported no polygon meshes: '+repr(result))
coords=[o.matrix_world @ v.co for o in objects for v in o.data.vertices]
lo=Vector((min(p.x for p in coords),min(p.y for p in coords),min(p.z for p in coords)))
hi=Vector((max(p.x for p in coords),max(p.y for p in coords),max(p.z for p in coords)))
center=(lo+hi)*.5;scale=6./max(hi.x-lo.x,hi.y-lo.y)
mat=bpy.data.materials.new('Warm gold geographic land');mat.diffuse_color=(0.67,0.47,0.25,1.0)
for o in objects:
 for v in o.data.vertices:
  p=o.matrix_world@v.co;v.co=((p.x-center.x)*scale,(p.y-center.y)*scale,0)
 o.matrix_world.identity();o.data.materials.clear();o.data.materials.append(mat)
 solid=o.modifiers.new('Real 3D silhouette depth','SOLIDIFY');solid.thickness=.075
 bevel=o.modifiers.new('Coast bevel','BEVEL');bevel.width=.018;bevel.segments=2
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.export_scene.gltf(filepath=str(out/'iberia_blendergis.glb'),export_format='GLB',use_selection=True)
# A transparent studio render provides a second verifiable output from Blender.
bpy.ops.object.camera_add(location=(0,-5.6,7.6),rotation=(radians(35),0,0));cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=8.0
bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-2,-3,7));light=bpy.context.object;light.data.energy=500;light.data.size=7
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=8;scene.render.film_transparent=True
scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(out/'iberia_blendergis.png');bpy.ops.render.render(write_still=True)
(out/'blendergis_status.json').write_text(json.dumps({'ok':True,'objects':len(objects),'source':'Natural Earth 1:50m countries','import':'BlenderGIS shapefile','blender':bpy.app.version_string},indent=2))
print('PASS Blender + BlenderGIS: imported country polygons and exported 3D layer.',flush=True)
