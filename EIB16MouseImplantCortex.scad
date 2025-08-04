
difference() {
// Import your STL model
import("BlankMouseImplantShapedv3.stl");

// Hole from [0.21, 4.15, 4.75] to [0.4, 4.2, -2.5]
translate([0.4000, 4.2000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);
// Hole from [-0.92, 4.15, 4.75] to [-0.4, 4.2, -2.5]
translate([-0.4000, 4.2000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);
// Hole from [1.34, 4.15, 4.75] to [1.5, 3.2, -1.5]
translate([1.5000, 3.2000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);
// Hole from [-2.05, 4.15, 4.75] to [-1.5, 3.2, -1.5]
translate([-1.5000, 3.2000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);
// Hole from [4.2, -0.36, 4.75] to [3, 1, -1.8]
translate([3.0000, 1.0000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);
// Hole from [-4.2, 3.75, 4.75] to [-3, 1, -1.8]
translate([-3.0000, 1.0000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);
// Hole from [2.05, -4.15, 4.75] to [1.5, -0.7000000000000002, -0.8]
translate([1.5000, -0.7000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);
// Hole from [-1.34, -4.15, 4.75] to [-1.5, -0.7000000000000002, -0.8]
translate([-1.5000, -0.7000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);
// Hole from [4.2, -3.75, 4.75] to [2.5, -1.5, -1.2]
translate([2.5000, -1.5000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);
// Hole from [-4.2, 0.36, 4.75] to [-2.5, -1.5, -1.2]
translate([-2.5000, -1.5000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);
// Hole from [4.2, -1.49, 4.75] to [4, -0.5, -2.2]
translate([4.0000, -0.5000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);
// Hole from [-4.2, 2.62, 4.75] to [-4, -0.5, -2.2]
translate([-4.0000, -0.5000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);
// Hole from [4.2, -2.62, 4.75] to [1.3, 0.19999999999999996, -1.5]
translate([1.3000, 0.2000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);
// Hole from [-4.2, 1.49, 4.75] to [-1.3, 0.19999999999999996, -1.5]
translate([-1.3000, 0.2000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);
// Hole from [0.92, -4.15, 4.75] to [0.5, 0.8, -3]
translate([0.5000, 0.8000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);
// Hole from [-0.21, -4.15, 4.75] to [-0.5, 0.8, -3]
translate([-0.5000, 0.8000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);
// Hole from [-4.15, -1.14, 4.75] to [-1, -3.5, -1.5]
translate([-1.0000, -3.5000, 0])
        cylinder(h = 5, r = 0.34, $fn=60);

}

// Label: A7
translate([1.2000, 4.2000, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("A7", size = 0.4, halign = "center", valign = "center");

// Label: A6
translate([-0.0939, 4.9391, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("A6", size = 0.4, halign = "center", valign = "center");

// Label: B1
translate([2.3000, -0.7000, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("B1", size = 0.4, halign = "center", valign = "center");

// Label: B4
translate([-0.7000, -0.7000, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("B4", size = 0.4, halign = "center", valign = "center");

// Label: A11
translate([2.0391, 0.5061, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("A11", size = 0.4, halign = "center", valign = "center");

// Label: A2
translate([-1.3000, 1.0000, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("A2", size = 0.4, halign = "center", valign = "center");

// Label: B2
translate([1.0657, 1.3657, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("B2", size = 0.4, halign = "center", valign = "center");

// Label: B3
translate([-0.1939, 1.5391, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("B3", size = 0.4, halign = "center", valign = "center");

// Label: A8
translate([2.3000, 3.2000, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("A8", size = 0.4, halign = "center", valign = "center");

// Label: A5
translate([-0.7000, 3.2000, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("A5", size = 0.4, halign = "center", valign = "center");

// Label: A12
translate([3.3000, -1.5000, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("A12", size = 0.4, halign = "center", valign = "center");

// Label: A1
translate([-1.7000, -1.5000, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("A1", size = 0.4, halign = "center", valign = "center");

// Label: A9
translate([3.8000, 1.0000, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("A9", size = 0.4, halign = "center", valign = "center");

// Label: A4
translate([-2.2609, 1.3061, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("A4", size = 0.4, halign = "center", valign = "center");

// Label: A10
translate([3.4343, 0.0657, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("A10", size = 0.4, halign = "center", valign = "center");

// Label: A3
translate([-3.2000, -0.5000, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("A3", size = 0.4, halign = "center", valign = "center");

// Label: GNDA1
translate([0.4000, -3.5000, 4.65])  // raised slightly above implant
    linear_extrude(height = 0.2)
    text("GNDA1", size = 0.4, halign = "center", valign = "center");

