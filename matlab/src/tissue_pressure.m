function pr = tissue_pressure(strain, p)
pr = p.tissue_modulus / p.tissue_stiffening * expm1(p.tissue_stiffening * max(strain, 0));
end
