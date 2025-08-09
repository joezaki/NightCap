
difference() {
    // Base plate for surgical guide
    translate([-10, -10, 0])
        cube([20, 20, 2], center=false);

    // Electrode holes
    translate([1, 2, -1]) cylinder(h = 10, r = 0.5, $fn=50);
    translate([2, 3, -1]) cylinder(h = 10, r = 0.5, $fn=50);
    translate([2.5, 3.1, -1]) cylinder(h = 10, r = 0.5, $fn=50);
}

// Skull model (not part of difference)
translate([-15.3, -14.00, 1])
rotate([-1.4, 90, 0])
    import("files/Mouse_Skull.stl");
