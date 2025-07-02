
difference() {
import("BlankDepthGuide.stl");


translate([1.3000, 0.0000, -1.5000])
    cylinder(h = 10, r = 0.23 +0.05, $fn=60);

translate([-1.3000, 0.0000, -1.5000])
    cylinder(h = 10, r = 0.23 +0.05, $fn=60);

translate([0.3000, 4.2000, -2.5000])
    cylinder(h = 10, r = 0.23 +0.05, $fn=60);

translate([-0.3000, 4.2000, -2.5000])
    cylinder(h = 10, r = 0.23 +0.05, $fn=60);

translate([2.0000, 2.5000, -3.5000])
    cylinder(h = 10, r = 0.23 +0.05, $fn=60);

translate([-2.0000, 2.5000, -3.5000])
    cylinder(h = 10, r = 0.23 +0.05, $fn=60);

translate([1.0000, -3.5000, -2.0000])
    cylinder(h = 10, r = 0.23 +0.05, $fn=60);

translate([-1.0000, -3.5000, -2.0000])
    cylinder(h = 10, r = 0.23 +0.05, $fn=60);

translate([3.0000, 1.0000, -1.8000])
    cylinder(h = 10, r = 0.35 +0.05, $fn=60);

}
