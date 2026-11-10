function e = min_fit_strain(c, fit_age, p)
w = worst_case(c, design_socket(c, fit_age, p), fit_age, p);
area = 2 * pi * w.state.radius * w.state.engaged;
needed = p.suspension_safety * w.pull_out / (p.friction * area);
e = log1p(needed * p.tissue_stiffening / p.tissue_modulus) / p.tissue_stiffening;
end
