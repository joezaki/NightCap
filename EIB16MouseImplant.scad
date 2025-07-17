
difference() {
// Import your STL model
import("BlankMouseImplantv3.stl");

// Hole from [4.2, -0.36, 4.75] to [1.3, 0.0, -1.5]
translate([1.2205, 0.0099, 2.0000])
rotate(a = 46.7395, v = [0.1232, 0.9924, -0.0000])
    cylinder(h = 5.2127, r = 0.34, $fn=60);
translate([1.3000, 0.0000, 0])
        cylinder(h = 2.232, r = 0.34, $fn=60);
// Hole from [-4.2, 0.36, 4.75] to [-1.3, 0.0, -1.5]
translate([-1.2205, -0.0099, 2.0000])
rotate(a = 46.7395, v = [-0.1232, -0.9924, 0.0000])
    cylinder(h = 5.2127, r = 0.34, $fn=60);
translate([-1.3000, 0.0000, 0])
        cylinder(h = 2.232, r = 0.34, $fn=60);
// Hole from [0.21, 4.15, 4.75] to [0.4, 4.2, -2.5]
translate([0.4076, 4.2020, 2.0000])
rotate(a = 4.0865, v = [0.2545, -0.9671, -0.0000])
    cylinder(h = 3.9570, r = 0.34, $fn=60);
translate([0.4000, 4.2000, 0])
        cylinder(h = 2.232, r = 0.34, $fn=60);
// Hole from [-0.92, 4.15, 4.75] to [-0.4, 4.2, -2.5]
translate([-0.3796, 4.2020, 2.0000])
rotate(a = 10.7559, v = [0.0957, -0.9954, -0.0000])
    cylinder(h = 3.9992, r = 0.34, $fn=60);
translate([-0.4000, 4.2000, 0])
        cylinder(h = 2.232, r = 0.34, $fn=60);
// Hole from [1.34, 4.15, 4.75] to [2, 2.5, -3.5]
translate([2.0222, 2.4446, 2.0000])
rotate(a = 32.8713, v = [-0.9285, -0.3714, 0.0000])
    cylinder(h = 4.4742, r = 0.34, $fn=60);
translate([2.0000, 2.5000, 0])
        cylinder(h = 2.232, r = 0.34, $fn=60);
// Hole from [-2.05, 4.15, 4.75] to [-2, 2.5, -3.5]
translate([-1.9983, 2.4434, 2.0000])
rotate(a = 30.9754, v = [-0.9995, -0.0303, 0.0000])
    cylinder(h = 4.4074, r = 0.34, $fn=60);
translate([-2.0000, 2.5000, 0])
        cylinder(h = 2.232, r = 0.34, $fn=60);
// Hole from [0.92, -4.15, 4.75] to [1, -3.5, -2]
translate([1.0031, -3.4747, 2.0000])
rotate(a = 13.3953, v = [0.9925, -0.1222, -0.0000])
    cylinder(h = 4.0269, r = 0.34, $fn=60);
translate([1.0000, -3.5000, 0])
        cylinder(h = 2.232, r = 0.34, $fn=60);
// Hole from [-0.21, -4.15, 4.75] to [-1, -3.5, -2]
translate([-1.0296, -3.4756, 2.0000])
rotate(a = 20.4058, v = [0.6354, 0.7722, -0.0000])
    cylinder(h = 4.1341, r = 0.34, $fn=60);
translate([-1.0000, -3.5000, 0])
        cylinder(h = 2.232, r = 0.34, $fn=60);
// Ground hole from [4.15, 1.14, 4.75] to [3, 1, -1.8]
translate([2.9576, 0.9948, 2.0000])
rotate(a = 22.8442, v = [-0.1208, 0.9927, -0.0000])
    cylinder(h = 4.1841, r = 0.4, $fn=60);
translate([3.0000, 1.0000, 0])
    cylinder(h = 2.232, r = 0.4, $fn=60);

}
