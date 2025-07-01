
// Import mouse skull
translate([-15.3, -14.00, 1]) {
    rotate([-1.4, 90, 0])
        import("files/Mouse_Skull.stl");
}

// Load your STL
translate([0, 0, 1]) {
    import("MouseBoxEIB16.stl");
}

// Electrode holes
