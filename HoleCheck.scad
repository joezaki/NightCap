
difference() {
// Import your STL model
import("HoleCheckBlank.stl");

// Hole check from [6, 6.0, 3.75] to [6, 6.0, 0]
translate([6.0000, 6.0000, 0])
    cylinder(h = 3.75, r = 0.1, $fn=60);
// Hole check from [6, 4.5, 3.75] to [6, 4.5, 0]
translate([6.0000, 4.5000, 0])
    cylinder(h = 3.75, r = 0.16, $fn=60);
// Hole check from [6, 3.0, 3.75] to [6, 3.0, 0]
translate([6.0000, 3.0000, 0])
    cylinder(h = 3.75, r = 0.22, $fn=60);
// Hole check from [6, 1.5, 3.75] to [6, 1.5, 0]
translate([6.0000, 1.5000, 0])
    cylinder(h = 3.75, r = 0.28, $fn=60);
// Hole check from [6, 0.0, 3.75] to [6, 0.0, 0]
translate([6.0000, 0.0000, 0])
    cylinder(h = 3.75, r = 0.33999999999999997, $fn=60);
// Hole check from [6, -1.5, 3.75] to [6, -1.5, 0]
translate([6.0000, -1.5000, 0])
    cylinder(h = 3.75, r = 0.4, $fn=60);
// Hole check from [6, -3.0, 3.75] to [6, -3.0, 0]
translate([6.0000, -3.0000, 0])
    cylinder(h = 3.75, r = 0.45999999999999996, $fn=60);
// Hole check from [6, -4.5, 3.75] to [6, -4.5, 0]
translate([6.0000, -4.5000, 0])
    cylinder(h = 3.75, r = 0.52, $fn=60);
// Hole check from [6, -6.0, 3.75] to [6, -6.0, 0]
translate([6.0000, -6.0000, 0])
    cylinder(h = 3.75, r = 0.58, $fn=60);
// Hole from [4, 6, 3.75] to [4, 6, 0.5]
translate([4.0000, 6.0000, 0.5000])
rotate(a = 0.0000, v = [-1.0000, 0.0000, 0.0000])
    cylinder(h = 4.4500, r = 0.28, $fn=60);
translate([4.0000, 6.0000, 0])
        cylinder(h = 0.5+0.2, r = 0.28, $fn=60);
// Hole from [4, 5, 3.75] to [4, 4, 0.5]
translate([4.0000, 4.0000, 0.5000])
rotate(a = 17.1027, v = [-1.0000, -0.0000, 0.0000])
    cylinder(h = 4.6004, r = 0.28, $fn=60);
translate([4.0000, 4.0000, 0])
        cylinder(h = 0.5+0.2, r = 0.28, $fn=60);
// Hole from [4, 4, 3.75] to [4, 2, 0.5]
translate([4.0000, 2.0000, 0.5000])
rotate(a = 31.6075, v = [-1.0000, -0.0000, 0.0000])
    cylinder(h = 5.0161, r = 0.28, $fn=60);
translate([4.0000, 2.0000, 0])
        cylinder(h = 0.5+0.2, r = 0.28, $fn=60);
// Hole from [4, 3, 3.75] to [4, 0, 0.5]
translate([4.0000, 0.0000, 0.5000])
rotate(a = 42.7094, v = [-1.0000, -0.0000, 0.0000])
    cylinder(h = 5.6230, r = 0.28, $fn=60);
translate([4.0000, 0.0000, 0])
        cylinder(h = 0.5+0.2, r = 0.28, $fn=60);
// Hole from [4, 2, 3.75] to [4, -2, 0.5]
translate([4.0000, -2.0000, 0.5000])
rotate(a = 50.9061, v = [-1.0000, -0.0000, 0.0000])
    cylinder(h = 6.3539, r = 0.28, $fn=60);
translate([4.0000, -2.0000, 0])
        cylinder(h = 0.5+0.2, r = 0.28, $fn=60);
// Hole from [4, 1, 3.75] to [4, -4, 0.5]
translate([4.0000, -4.0000, 0.5000])
rotate(a = 56.9761, v = [-1.0000, -0.0000, 0.0000])
    cylinder(h = 7.1634, r = 0.28, $fn=60);
translate([4.0000, -4.0000, 0])
        cylinder(h = 0.5+0.2, r = 0.28, $fn=60);
// Hole from [2, 6, 3.75] to [2, 6, 0.5]
translate([2.0000, 6.0000, 0.3000])
rotate(a = 0.0000, v = [-1.0000, 0.0000, 0.0000])
    cylinder(h = 4.4500, r = 0.23, $fn=60);
translate([2.0000, 6.0000, 0])
        cylinder(h = 0.5, r = 0.23+0.05, $fn=60);
// Hole from [2, 5, 3.75] to [2, 4, 0.5]
translate([2.0000, 3.9412, 0.3088])
rotate(a = 17.1027, v = [-1.0000, -0.0000, 0.0000])
    cylinder(h = 4.6004, r = 0.23, $fn=60);
translate([2.0000, 4.0000, 0])
        cylinder(h = 0.5, r = 0.23+0.05, $fn=60);
// Hole from [2, 4, 3.75] to [2, 2, 0.5]
translate([2.0000, 1.8952, 0.3297])
rotate(a = 31.6075, v = [-1.0000, -0.0000, 0.0000])
    cylinder(h = 5.0161, r = 0.23, $fn=60);
translate([2.0000, 2.0000, 0])
        cylinder(h = 0.5, r = 0.23+0.05, $fn=60);
// Hole from [2, 3, 3.75] to [2, 0, 0.5]
translate([2.0000, -0.1357, 0.3530])
rotate(a = 42.7094, v = [-1.0000, -0.0000, 0.0000])
    cylinder(h = 5.6230, r = 0.23, $fn=60);
translate([2.0000, 0.0000, 0])
        cylinder(h = 0.5, r = 0.23+0.05, $fn=60);
// Hole from [2, 2, 3.75] to [2, -2, 0.5]
translate([2.0000, -2.1552, 0.3739])
rotate(a = 50.9061, v = [-1.0000, -0.0000, 0.0000])
    cylinder(h = 6.3539, r = 0.23, $fn=60);
translate([2.0000, -2.0000, 0])
        cylinder(h = 0.5, r = 0.23+0.05, $fn=60);
// Hole from [2, 1, 3.75] to [2, -4, 0.5]
translate([2.0000, -4.1677, 0.3910])
rotate(a = 56.9761, v = [-1.0000, -0.0000, 0.0000])
    cylinder(h = 7.1634, r = 0.23, $fn=60);
translate([2.0000, -4.0000, 0])
        cylinder(h = 0.5, r = 0.23+0.05, $fn=60);
// Hole from [0, 6.0, 3.75] to [0, 3.0, 0.5]
translate([0.0000, 3.0000, 0.5000])
rotate(a = 42.7094, v = [-1.0000, -0.0000, 0.0000])
    cylinder(h = 5.6230, r = 0.1, $fn=60);
translate([0.0000, 3.0000, 0])
        cylinder(h = 0.5+0.2, r = 0.1, $fn=60);
// Hole from [0, 4.5, 3.75] to [0, 1.5, 0.5]
translate([0.0000, 1.5000, 0.5000])
rotate(a = 42.7094, v = [-1.0000, -0.0000, 0.0000])
    cylinder(h = 5.6230, r = 0.16, $fn=60);
translate([0.0000, 1.5000, 0])
        cylinder(h = 0.5+0.2, r = 0.16, $fn=60);
// Hole from [0, 3.0, 3.75] to [0, 0.0, 0.5]
translate([0.0000, 0.0000, 0.5000])
rotate(a = 42.7094, v = [-1.0000, -0.0000, 0.0000])
    cylinder(h = 5.6230, r = 0.22, $fn=60);
translate([0.0000, 0.0000, 0])
        cylinder(h = 0.5+0.2, r = 0.22, $fn=60);
// Hole from [0, 1.5, 3.75] to [0, -1.5, 0.5]
translate([0.0000, -1.5000, 0.5000])
rotate(a = 42.7094, v = [-1.0000, -0.0000, 0.0000])
    cylinder(h = 5.6230, r = 0.28, $fn=60);
translate([0.0000, -1.5000, 0])
        cylinder(h = 0.5+0.2, r = 0.28, $fn=60);
// Hole from [0, 0.0, 3.75] to [0, -3.0, 0.5]
translate([0.0000, -3.0000, 0.5000])
rotate(a = 42.7094, v = [-1.0000, -0.0000, 0.0000])
    cylinder(h = 5.6230, r = 0.33999999999999997, $fn=60);
translate([0.0000, -3.0000, 0])
        cylinder(h = 0.5+0.2, r = 0.33999999999999997, $fn=60);
// Hole from [0, -1.5, 3.75] to [0, -4.5, 0.5]
translate([0.0000, -4.5000, 0.5000])
rotate(a = 42.7094, v = [-1.0000, -0.0000, 0.0000])
    cylinder(h = 5.6230, r = 0.4, $fn=60);
translate([0.0000, -4.5000, 0])
        cylinder(h = 0.5+0.2, r = 0.4, $fn=60);

}
