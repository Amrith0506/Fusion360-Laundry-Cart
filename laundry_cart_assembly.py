#Author: Copilot
#Description: Fusion 360 Python API script to create a complete C3 Automatic Laundry Sorting Cart assembly
#All dimensions in mm

import adsk.core
import adsk.fusion
import traceback
from mathutils import Vector3 as Vec3

class LaundryCartAssembly:
    def __init__(self):
        self.app = adsk.core.Application.get()
        self.ui = self.app.userInterface
        self.design = adsk.fusion.Design.cast(self.app.activeProduct)
        self.rootComp = self.design.rootComponent
        self.components = []
        
    def create_component(self, name):
        """Create a new component in the assembly"""
        occurence = self.rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp = occurence.component
        comp.name = name
        self.components.append((name, comp))
        return comp
    
    def create_box(self, comp, name, width, depth, height, x_offset=0, y_offset=0, z_offset=0):
        """Create a box/rectangular solid"""
        sketches = comp.sketches
        xy_plane = comp.xYConstructionPlane
        sketch = sketches.add(xy_plane)
        
        lines = sketch.sketchCurves.sketchLines
        lines.addTwoPointRectangle(
            adsk.core.Point3D.create(-width/2 + x_offset, -depth/2 + y_offset, 0),
            adsk.core.Point3D.create(width/2 + x_offset, depth/2 + y_offset, 0)
        )
        sketch.isVisible = False
        
        extrudes = comp.features.extrudeFeatures
        profile = sketch.profiles.item(0)
        extent = adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(height))
        extrude = extrudes.addSimple(profile, extent, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extrude.name = name
        return extrude.bodies.item(0)
    
    def create_cylinder(self, comp, name, radius, height, x_offset=0, y_offset=0, z_offset=0):
        """Create a cylinder"""
        sketches = comp.sketches
        xy_plane = comp.xYConstructionPlane
        sketch = sketches.add(xy_plane)
        
        circles = sketch.sketchCurves.sketchCircles
        circle = circles.addByCenterAndRadius(
            adsk.core.Point3D.create(x_offset, y_offset, 0),
            radius
        )
        sketch.isVisible = False
        
        extrudes = comp.features.extrudeFeatures
        profile = sketch.profiles.item(0)
        extent = adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(height))
        extrude = extrudes.addSimple(profile, extent, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extrude.name = name
        return extrude.bodies.item(0)
    
    def create_frame(self):
        """Create the main frame structure (steel tubing)"""
        frame_comp = self.create_component("Frame_Structure")
        
        # Frame dimensions
        length = 1200
        width = 500
        height = 800
        tube_size = 30  # 30mm square tube
        
        # Base frame - front left vertical
        self.create_box(frame_comp, "Frame_FL_Vertical", tube_size, tube_size, height, 
                       -length/2 + 50, -width/2 + 50, 0)
        
        # Base frame - front right vertical
        self.create_box(frame_comp, "Frame_FR_Vertical", tube_size, tube_size, height,
                       length/2 - 50, -width/2 + 50, 0)
        
        # Base frame - back left vertical
        self.create_box(frame_comp, "Frame_BL_Vertical", tube_size, tube_size, height,
                       -length/2 + 50, width/2 - 50, 0)
        
        # Base frame - back right vertical
        self.create_box(frame_comp, "Frame_BR_Vertical", tube_size, tube_size, height,
                       length/2 - 50, width/2 - 50, 0)
        
        # Horizontal rails - length-wise
        self.create_box(frame_comp, "Frame_Long_Rail_1", length - 100, tube_size, tube_size,
                       0, -width/2, height/2)
        self.create_box(frame_comp, "Frame_Long_Rail_2", length - 100, tube_size, tube_size,
                       0, width/2, height/2)
        
        # Cross rails - width-wise
        self.create_box(frame_comp, "Frame_Cross_Rail_1", tube_size, width - 100, tube_size,
                       -length/2, 0, height/2)
        self.create_box(frame_comp, "Frame_Cross_Rail_2", tube_size, width - 100, tube_size,
                       length/2, 0, height/2)
        
        return frame_comp
    
    def create_loading_tray(self):
        """Create the loading tray (top component) - 400x300x200mm"""
        tray_comp = self.create_component("Loading_Tray")
        
        # Tray body (slanted slightly)
        self.create_box(tray_comp, "Tray_Bottom", 400, 300, 5, 0, 0, 0)
        self.create_box(tray_comp, "Tray_Side_Left", 5, 300, 100, -200, 0, 50)
        self.create_box(tray_comp, "Tray_Side_Right", 5, 300, 100, 200, 0, 50)
        self.create_box(tray_comp, "Tray_Front", 400, 5, 50, 0, -150, 25)
        
        return tray_comp
    
    def create_conveyor_rollers(self):
        """Create the conveyor roller assembly"""
        roller_comp = self.create_component("Conveyor_Rollers")
        
        # Main conveyor roller (Ø40mm, 300mm long)
        roller_radius = 20  # 40mm diameter
        roller_length = 300
        
        # Create 3 conveyor rollers
        for i, y_pos in enumerate([-120, 0, 120]):
            self.create_cylinder(roller_comp, f"Roller_{i+1}", roller_radius, 
                                roller_length, 0, y_pos, 150)
        
        return roller_comp
    
    def create_sorting_gate(self):
        """Create the sorting gate mechanism"""
        gate_comp = self.create_component("Sorting_Gate")
        
        # Gate plate (250x200mm)
        self.create_box(gate_comp, "Gate_Plate", 250, 200, 8, 0, 0, 250)
        
        # Gate support frame
        self.create_box(gate_comp, "Gate_Support_Left", 10, 200, 100, -130, 0, 250)
        self.create_box(gate_comp, "Gate_Support_Right", 10, 200, 100, 130, 0, 250)
        self.create_box(gate_comp, "Gate_Support_Bottom", 250, 10, 50, 0, -110, 200)
        
        return gate_comp
    
    def create_storage_bins(self):
        """Create 3 storage bins (compartments) - 300x300x250mm each"""
        bins_comp = self.create_component("Storage_Bins")
        
        # Bin positions (left, center, right)
        positions = [
            (-350, 0, "Bin_Shirts_Blue"),
            (0, 0, "Bin_Pants_Green"),
            (350, 0, "Bin_Towels_Yellow")
        ]
        
        for x_pos, y_pos, bin_name in positions:
            # Bin body
            self.create_box(bins_comp, f"{bin_name}_Body", 280, 280, 250, x_pos, y_pos, 100)
            
            # Bin front panel
            self.create_box(bins_comp, f"{bin_name}_Front", 280, 8, 250, x_pos, -150, 100)
            
            # Bin back panel
            self.create_box(bins_comp, f"{bin_name}_Back", 280, 8, 250, x_pos, 150, 100)
            
            # Bin side panels
            self.create_box(bins_comp, f"{bin_name}_Left", 8, 280, 250, x_pos - 146, y_pos, 100)
            self.create_box(bins_comp, f"{bin_name}_Right", 8, 280, 250, x_pos + 146, y_pos, 100)
        
        return bins_comp
    
    def create_wheels(self):
        """Create 4 wheels (swivel casters) - Ø100mm"""
        wheels_comp = self.create_component("Wheels")
        
        wheel_positions = [
            (-550, -220, "Wheel_FL"),
            (550, -220, "Wheel_FR"),
            (-550, 220, "Wheel_BL"),
            (550, 220, "Wheel_BR")
        ]
        
        wheel_radius = 50  # 100mm diameter
        wheel_width = 40
        
        for x, y, wheel_name in wheel_positions:
            # Wheel rim
            self.create_cylinder(wheels_comp, f"{wheel_name}_Rim", wheel_radius, 
                                wheel_width, x, y, 30)
            
            # Wheel axle (shaft)
            self.create_cylinder(wheels_comp, f"{wheel_name}_Axle", 6, wheel_width + 20, 
                                x, y, 25)
            
            # Wheel bracket (swivel mount)
            self.create_box(wheels_comp, f"{wheel_name}_Bracket", 40, 40, 80, x, y, 60)
        
        return wheels_comp
    
    def create_handles(self):
        """Create push handles on both sides"""
        handles_comp = self.create_component("Handles")
        
        # Left handle
        handle_radius = 8  # 16mm diameter tubing
        self.create_cylinder(handles_comp, "Handle_Left_Vertical", handle_radius, 400, 
                            -600, -240, 400)
        self.create_cylinder(handles_comp, "Handle_Left_Top", handle_radius, 200,
                            -500, -240, 750)
        
        # Right handle  
        self.create_cylinder(handles_comp, "Handle_Right_Vertical", handle_radius, 400,
                            600, -240, 400)
        self.create_cylinder(handles_comp, "Handle_Right_Top", handle_radius, 200,
                            500, -240, 750)
        
        # Cross brace for handles
        self.create_box(handles_comp, "Handle_Cross_Brace", 1200, 15, 15, 0, -240, 600)
        
        return handles_comp
    
    def create_fasteners(self):
        """Create nuts, bolts, and fastening hardware"""
        fasteners_comp = self.create_component("Fasteners")
        
        # M6 Bolts at frame corners (12 bolts)
        bolt_positions = [
            (-575, -225, 50), (-575, -225, 400),
            (575, -225, 50), (575, -225, 400),
            (-575, 225, 50), (-575, 225, 400),
            (575, 225, 50), (575, 225, 400),
            # Additional frame connection points
            (-575, 0, 200), (575, 0, 200),
            (0, -225, 300), (0, 225, 300)
        ]
        
        bolt_radius = 3  # M6 = 6mm diameter
        bolt_height = 30
        
        for i, (x, y, z) in enumerate(bolt_positions):
            self.create_cylinder(fasteners_comp, f"Bolt_M6_{i+1}", bolt_radius, 
                                bolt_height, x, y, z)
            # Washer (flat disc)
            self.create_cylinder(fasteners_comp, f"Washer_{i+1}", 6, 2, x, y, z + 15)
            # Hex nut (simplified as cylinder)
            self.create_cylinder(fasteners_comp, f"Nut_M6_{i+1}", 4, 8, x, y, z + 25)
        
        return fasteners_comp
    
    def create_control_panel(self):
        """Create the control panel with buttons and display"""
        panel_comp = self.create_component("Control_Panel")
        
        # Panel base
        self.create_box(panel_comp, "Panel_Base", 200, 100, 15, -500, -200, 650)
        
        # Display screen area (simplified)
        self.create_box(panel_comp, "Display_Screen", 150, 60, 5, -500, -200, 670)
        
        # Button 1 (Load)
        self.create_cylinder(panel_comp, "Button_Load", 12, 20, -550, -230, 700)
        
        # Button 2 (Sort)
        self.create_cylinder(panel_comp, "Button_Sort", 12, 20, -500, -230, 700)
        
        # Button 3 (Stop)
        self.create_cylinder(panel_comp, "Button_Stop", 12, 20, -450, -230, 700)
        
        return panel_comp
    
    def create_assembly(self):
        """Main function to create the complete assembly"""
        try:
            # Create all major components
            frame = self.create_frame()
            tray = self.create_loading_tray()
            rollers = self.create_conveyor_rollers()
            gate = self.create_sorting_gate()
            bins = self.create_storage_bins()
            wheels = self.create_wheels()
            handles = self.create_handles()
            fasteners = self.create_fasteners()
            panel = self.create_control_panel()
            
            # Position components relative to frame
            # (Already positioned during creation via offset parameters)
            
            self.ui.messageBox("C3 Laundry Cart Assembly Created Successfully!\n\n" +
                             "Assembly contains:\n" +
                             "- Frame Structure\n" +
                             "- Loading Tray\n" +
                             "- Conveyor Rollers (3x)\n" +
                             "- Sorting Gate Mechanism\n" +
                             "- Storage Bins (3x)\n" +
                             "- Wheels & Casters (4x)\n" +
                             "- Push Handles\n" +
                             "- Fasteners (Bolts, Nuts, Washers)\n" +
                             "- Control Panel\n\n" +
                             "All components are separate bodies ready for assembly!")
            
        except Exception as e:
            self.ui.messageBox(f"Error creating assembly: {str(e)}\n{traceback.format_exc()}")

def run(context):
    try:
        cart = LaundryCartAssembly()
        cart.create_assembly()
    except Exception as e:
        adsk.core.Application.get().userInterface.messageBox(
            f"Failed to create laundry cart: {str(e)}\n{traceback.format_exc()}"
        )
