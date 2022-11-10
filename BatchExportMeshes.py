bl_info = {
    "name": "Batch Export Meshes",
    "author": "Justin Heffron",
    "version": (1, 0),
    "blender": (3, 1, 2),
    "location": "File>Export>Batch Export Meshes",
    "description": "Batch exports selected meshes and armatures. Options for moving objects to world origin, file format, and file name prefix.",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
import os.path
import mathutils


# the class for the export window

# done with help from: https://blender.stackexchange.com/questions/14738/use-filemanager-to-select-directory-instead-of-file
# answer provided by user: neomonkeus
# licensesd under CC BY-SA 3.0 (compatible with GPLv3)

class BatchExport(bpy.types.Operator, ExportHelper):
    """Batch exports selected meshes to a chosen directory"""
    
    bl_idname = "export.batch_export_meshes"
    bl_label = "Batch Export Meshes"
    
    filename_ext = "."
    use_filter_folder = True
    
    # should the exporter move meshes to 0,0,0 before exporting?
    freeze_locations: BoolProperty(
        name="Freeze Locations",
        description="Should the exporter set the locations of meshes to world origin (0,0,0) before exporting?",
        default=True,
    )
    
    # the prefix appended to the front of object names in the exported files
    mesh_name_prefix: StringProperty(
        name="Prefix",
        default="SM_",
        maxlen=255, 
    )
    
    # the file format of the exported objects
    file_type: EnumProperty(
        name="File Type",
        description="The file type for the exported meshes",
        items=(
            ('FBX', "FBX", ""),
            ('GLTF', "GLTF", ""),
            ('OBJ', "OBJ", ""),
            ('DAE', "DAE", ""),
        ),
        default='FBX',
    )
    
    def execute(self, context):
        directory = self.properties.filepath
        
        # removes the file part from the full filepath
        last_slash = directory.rfind('\\')
        if(last_slash != -1):
            directory = directory[:last_slash]
        
        if not os.path.isdir(directory):
            self.report({'WARNING'}, "Please select a valid path")
        else:
            batch_export_meshes(context, directory, self.freeze_locations, self.file_type, self.mesh_name_prefix)
        return{'FINISHED'}
        
        
# the function which handles the exporting (modified and expanded from blender template file)        
def batch_export_meshes(context, directory, freeze_locations, file_type, mesh_name_prefix):
    
    # if no directory is provided (somehow), use location of blend file itself
    basedir = ""
    if not directory or directory == "":
        basedir = os.path.dirname(bpy.data.filepath)
    else:
        basedir = directory

    if not basedir:
        raise Exception("Blend file is not saved")

    view_layer = bpy.context.view_layer

    obj_active = view_layer.objects.active
    selection = bpy.context.selected_objects

    bpy.ops.object.select_all(action='DESELECT')

    for obj in selection:
        # only export meshes and armature (lights, cameras, etc don't need exported)
        if obj.type != "MESH" and obj.type != "ARMATURE":
            continue
        
        obj.select_set(True)
        
        # save location in case we freeze location so we can move it back after exporting
        saved_location = obj.location.copy()
        
        # if we freeze location, set object to world origin
        if(freeze_locations):
            obj.location = mathutils.Vector((0,0,0))

        # some exporters only use the active object
        view_layer.objects.active = obj

        name = bpy.path.clean_name(obj.name)
        
        # if a mesh prefix was provided, append that now
        if mesh_name_prefix:
            name = str(mesh_name_prefix) + name 
        
        fn = os.path.join(basedir, name)

        # export based on chosen file type
        match file_type:
            case 'FBX':
                bpy.ops.export_scene.fbx(filepath=fn + ".fbx", use_selection=True)
            case 'OBJ':
                bpy.ops.export_scene.obj(filepath=fn + ".obj", use_selection=True)
            case 'GLTF':
                bpy.ops.export_scene.gltf(filepath=fn + ".gltf", use_selection=True, export_format='GLTF_SEPARATE')
            case 'DAE':
                bpy.ops.export_scene.fbx(filepath=fn + ".dae", use_selection=True)
    
        obj.select_set(False)

        # in case we moved actor to world origin, set it back
        obj.location = saved_location


    view_layer.objects.active = obj_active

    for obj in selection:
        obj.select_set(True)    

# the function called from the file>export menu
def call_batch_export(self, context):
    self.layout.operator(BatchExport.bl_idname, text = "Batch Export Meshes")
    
def register():
    bpy.utils.register_class(BatchExport)
    bpy.types.TOPBAR_MT_file_export.append(call_batch_export)
    
def unregister():
    bpy.utils.unregister_class(BatchExport)
    bpy.types.TOPBAR_MT_file_export.remove(call_batch_export)
    
if __name__ == "__main__":
    register()