function s = design_socket(c, fit_age, p, fit_strain)
if nargin < 4 || isempty(fit_strain), fit_strain = p.fit_strain; end
b = body_at(c, fit_age, p);
s.fit_age = fit_age;
s.fit_strain = fit_strain;
s.residual0 = p.residual_fraction * b.forearm_length;
s.forearm0 = b.forearm_length;
s.depth = s.residual0 + p.distal_clearance;
s.radius = b.radius * (1 - fit_strain * p.soft_tissue_fraction);
s.length = b.grip;
end
