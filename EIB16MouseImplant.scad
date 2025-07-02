
difference() {
// Import your STL model
import("BlankMouseImplant.stl");

// Hole from [4.2, -0.36, 3.75] to [1.3, 0.0, 1]
translate([1.1555, 0.0179, 0.8629])
rotate(a = 46.7395, v = [0.1232, 0.9924, -0.0000])
    cylinder(h = 5.2127, r = 0.23, $fn=60);
translate([1.3000, 0.0000, 0])
        cylinder(h = 1, r = 0.23+0.05, $fn=60);
// Hole from [-4.2, 0.36, 3.75] to [-1.3, 0.0, 1]
translate([-1.1555, -0.0179, 0.8629])
rotate(a = 46.7395, v = [-0.1232, -0.9924, 0.0000])
    cylinder(h = 5.2127, r = 0.23, $fn=60);
translate([-1.3000, 0.0000, 0])
        cylinder(h = 1, r = 0.23+0.05, $fn=60);
// Hole from [0.21, 4.15, 3.75] to [0.3, 4.2, 1]
translate([0.3065, 4.2036, 0.8001])
rotate(a = 2.1441, v = [0.4856, -0.8742, -0.0000])
    cylinder(h = 3.9519, r = 0.23, $fn=60);
translate([0.3000, 4.2000, 0])
        cylinder(h = 1, r = 0.23+0.05, $fn=60);
// Hole from [-0.92, 4.15, 3.75] to [-0.3, 4.2, 1]
translate([-0.2560, 4.2035, 0.8049])
rotate(a = 12.7451, v = [0.0804, -0.9968, -0.0000])
    cylinder(h = 4.0195, r = 0.23, $fn=60);
translate([-0.3000, 4.2000, 0])
        cylinder(h = 1, r = 0.23+0.05, $fn=60);
// Hole from [1.34, 4.15, 3.75] to [2, 2.5, 1]
translate([2.0403, 2.3992, 0.8320])
rotate(a = 32.8713, v = [-0.9285, -0.3714, 0.0000])
    cylinder(h = 4.4742, r = 0.23, $fn=60);
translate([2.0000, 2.5000, 0])
        cylinder(h = 1, r = 0.23+0.05, $fn=60);
// Hole from [-2.05, 4.15, 3.75] to [-2, 2.5, 1]
translate([-1.9969, 2.3971, 0.8285])
rotate(a = 30.9754, v = [-0.9995, -0.0303, 0.0000])
    cylinder(h = 4.4074, r = 0.23, $fn=60);
translate([-2.0000, 2.5000, 0])
        cylinder(h = 1, r = 0.23+0.05, $fn=60);
// Hole from [0.92, -4.15, 3.75] to [1, -3.5, 1]
translate([1.0057, -3.4540, 0.8054])
rotate(a = 13.3953, v = [0.9925, -0.1222, -0.0000])
    cylinder(h = 4.0269, r = 0.23, $fn=60);
translate([1.0000, -3.5000, 0])
        cylinder(h = 1, r = 0.23+0.05, $fn=60);
// Hole from [-0.21, -4.15, 3.75] to [-1, -3.5, 1]
translate([-1.0538, -3.4557, 0.8126])
rotate(a = 20.4058, v = [0.6354, 0.7722, -0.0000])
    cylinder(h = 4.1341, r = 0.23, $fn=60);
translate([-1.0000, -3.5000, 0])
        cylinder(h = 1, r = 0.23+0.05, $fn=60);

}
