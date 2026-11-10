function b = body_at(c, age, p)
b.height = interp1(c.t, c.H, age, 'pchip');
b.mass = interp1(c.age_w, c.w, age, 'pchip');
b.upper_arm_length = p.f_upper_arm_length * b.height;
b.forearm_length = p.f_forearm_length * b.height;
b.hand_length = p.f_hand_length * b.height;
b.upper_arm_mass = p.f_upper_arm_mass * b.mass;
b.forearm_mass = p.f_forearm_mass * b.mass;
b.grip = b.forearm_length + 0.5 * b.hand_length;
b.radius = p.atrophy_ratio * sqrt(b.forearm_mass / (p.tissue_density * pi * b.forearm_length));
end
