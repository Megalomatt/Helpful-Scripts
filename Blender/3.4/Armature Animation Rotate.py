"""

Blender 3.4 Armature Animation Rotate

This script was created to deal with the rotation of animations downloaded from Mixamo.
It creates a duplicate armature that contains both the original animation and a new animation
rotated by a number of degrees (default is 180) which are saved to an NLA strip.
This allows the orientation to be set in advance for export to a game engine.

To use, enter Object mode and select the Armature you wish to have another orientation of.
Go to the Scripting tab and create a new script, copy paste this script and set the desired ROTATION 
Press the Play button and a new armature is created.

Notes:
    Longer animations take longer to process. As this script was designed to work with Mixamo
    armatures your milage may vary with other armatures. Providing they have bones and a single
    Action (that has not been pushed down) it will likely work OK.
    
"""

import bpy
from math import radians

ROTATION = 180

# Get the armature object
parent_armature_obj = bpy.context.active_object

# Exit early if the selected object is not an armature
if parent_armature_obj.type != 'ARMATURE':
    # Display an error message as a pop-up window
    def show_error_message(message):
        def draw(self, context):
            self.layout.label(text=message)

        bpy.context.window_manager.popup_menu(draw, title="Error", icon='ERROR')

    show_error_message("The selected object is not an armature.")
else:

    # Get armature object's data
    parent_armature_data = parent_armature_obj.data

    # Duplicate the armature object and its data
    bake_armature_obj      = parent_armature_obj.copy()
    bake_armature_obj.data = parent_armature_obj.data.copy()
    bake_armature_obj.name = 'Bake'

    # Duplicate the armature object and its data again
    updated_armature_obj      = parent_armature_obj.copy()
    updated_armature_obj.data = parent_armature_obj.data.copy()
    updated_armature_obj.name = 'Updated'

    # Add the duplicate armature objects to the scene
    bpy.context.collection.objects.link(bake_armature_obj)
    bpy.context.collection.objects.link(updated_armature_obj)

    # Save the original animation to the NLA
    original_action = updated_armature_obj.animation_data.action
    track           = updated_armature_obj.animation_data.nla_tracks.new()
    track.name      = parent_armature_obj.name + '-original'
    strip           = track.strips.new('original', int(original_action.frame_range[0]), original_action)
    strip.name      = 'original'


    # Store the number of frames of the animation as a variable
    animation_length = int(parent_armature_obj.animation_data.action.frame_range[1])

    # Iterate over the bones in the duplicate armature
    for bone in bake_armature_obj.pose.bones:
        # Rotations
        # Create a copy rotation constraint for the bone
        copy_rotation_constraint = bone.constraints.new(type='COPY_ROTATION')
        # Set the target to the matching bone in the original armature
        copy_rotation_constraint.target    = parent_armature_obj
        copy_rotation_constraint.subtarget = bone.name
        # Set the influence of the constraint to 1.0
        copy_rotation_constraint.influence = 1.0
        
        # Transforms
        # Create a copy location constraint for the bone
        copy_location_constraint = bone.constraints.new(type='COPY_LOCATION')
        # Set the target to the matching bone in the original armature
        copy_location_constraint.target    = parent_armature_obj
        copy_location_constraint.subtarget = bone.name
        # Set the influence of the location constraint to 1.0
        copy_location_constraint.influence = 1.0

    # Delete the animation data for the duplicate armature
    bake_armature_obj.animation_data_clear()

    # Select the 'Parent' armature and rotate it by ROTATION degrees in the z axis
    parent_armature_obj.rotation_euler.z += radians(ROTATION)

    # Select the 'Bake' armature and go into pose mode
    bake_armature_obj.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')

    # Bake the animation, renaming the action to the rotation amount
    bpy.ops.nla.bake(
        frame_start        = 1,
        frame_end          = animation_length,
        visual_keying      = True,
        clear_constraints  = True,
        use_current_action = True,
        bake_types         = {'POSE'}
    )
    
    rotated_action = bake_armature_obj.animation_data.action

    # Push the actions down
    track      = updated_armature_obj.animation_data.nla_tracks.new()
    track.name = parent_armature_obj.name + '-' + str(ROTATION)
    strip      = track.strips.new(str(ROTATION), int(rotated_action.frame_range[0]), rotated_action)
    strip.name = str(ROTATION)
    updated_armature_obj.animation_data.action = None

    # Select the 'Parent' armature and rotate it back to how it was before
    bpy.ops.object.mode_set(mode = 'OBJECT')
    parent_armature_obj.rotation_euler.z += radians(-ROTATION)

    # Remove the temporary 'Bake' armature from the scene
    bpy.ops.object.select_all(action = 'DESELECT')
    bake_armature_obj.select_set(True)
    bpy.ops.object.delete()
    
    # Update the name of the remaining armature
    updated_armature_obj.name = parent_armature_obj.name + '-updated'