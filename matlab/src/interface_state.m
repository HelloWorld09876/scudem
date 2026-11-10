function st = interface_state(c, s, age, p)
b = body_at(c, age, p);
residual = s.residual0 + p.proximal_growth_share * (b.forearm_length - s.forearm0);
bottom = max(0, residual - s.depth);
r = b.radius;
interference = r - s.radius;
offset = bottom;
tan_a = tan(p.taper_deg * pi / 180);
if strcmp(p.socket_shape, 'tapered') && interference > 0
  thickness = p.soft_tissue_fraction * r;
  wedge = p.friction * cos(p.taper_deg * pi / 180) + sin(p.taper_deg * pi / 180);
  excess = @(z) tissue_pressure((interference - z * tan_a) / thickness, p) - ...
                p.donning_force / (2 * pi * r * (residual - z) * wedge);
  if excess(bottom) > 0
    upper = min(interference / tan_a, 0.95 * residual);
    if excess(upper) > 0
      offset = upper;
    else
      offset = fzero(excess, [bottom, upper], optimset('TolX', 1e-12));
    end
  end
  interference = interference - offset * tan_a;
end
st.body = b;
st.residual = residual;
st.offset = offset;
st.ride_up = offset - bottom;
st.engaged = residual - offset;
st.radius = r;
st.strain = interference / (p.soft_tissue_fraction * r);
st.fit_pressure = tissue_pressure(st.strain, p);
st.grip = offset + s.length;
end
