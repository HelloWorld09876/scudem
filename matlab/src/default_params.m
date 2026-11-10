function p = default_params()
p.f_upper_arm_length = 0.186;
p.f_forearm_length = 0.146;
p.f_hand_length = 0.108;
p.f_upper_arm_mass = 0.028;
p.f_forearm_mass = 0.016;
p.f_hand_mass = 0.006;
p.upper_arm_com = 0.436;
p.upper_arm_gyration = 0.322;
p.tissue_density = 1100;
p.residual_fraction = 0.45;
p.proximal_growth_share = 0.25;
p.atrophy_ratio = 0.90;
p.soft_tissue_fraction = 0.40;
p.tissue_modulus = 100e3;
p.tissue_stiffening = 6.0;
p.friction = 0.5;
p.pressure_tolerance = 100e3;
p.prosthesis_mass = 0.40;
p.prosthesis_com = 0.55;
p.prosthesis_gyration = 0.30;
p.distal_clearance = 0.005;
p.fit_strain = 0.05;
p.suspension_safety = 1.25;
p.socket_shape = 'cylindrical';
p.taper_deg = 4.0;
p.donning_force = 60.0;
p.load_mode = 'fixed';
p.object_mass = 0.5;
p.object_fraction = 0.02;
p.speed_factor = 1.0;
p.tasks = struct('name', {'Static hold', 'Slow curl', 'Fast curl', 'Lift to shelf'}, ...
                 'shoulder', {[0 0], [5 20], [5 20], [10 100]}, ...
                 'elbow', {[90 90], [10 130], [10 130], [30 30]}, ...
                 'duration', {1.0, 1.2, 0.5, 1.2});
end
