translate([0, 0, 0])
render() import("MouseBox_v1.stl");

// Alignment sphere
translate([0, 0, 2])
    sphere(r = 0.5, $fn = 40);
