
difference() {
// Import your STL model
import("MouseBoxEIB16.stl");

// Hole from [1.58, 4.2, 3.75] to [2, 2, 0]
translate([2.0962, 1.4963, -0.8585])
rotate(a = 30.8483, v = [-0.9823, -0.1875, 0.0000])
    cylinder(h = 5.5679, r = 0.4, $fn=60);
// Hole from [4.2, -0.9, 3.75] to [2, -2, 0]
translate([1.5094, -2.2453, -0.8362])
rotate(a = 33.2614, v = [-0.4472, 0.8944, -0.0000])
    cylinder(h = 5.6847, r = 0.4, $fn=60);
// Hole from [2, -4.2, 3.75] to [1.5, -3.2, 0]
translate([1.3722, -2.9444, -0.9583])
rotate(a = 16.6015, v = [0.8944, 0.4472, -0.0000])
    cylinder(h = 5.1131, r = 0.4, $fn=60);

}
