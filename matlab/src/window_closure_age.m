function a_c = window_closure_age(c, p)
margin = @(a) 1 - getfield(worst_case(c, design_socket(c, a, p, min_fit_strain(c, a, p)), a, p), 'ssi');
ages = 4:0.25:18;
a_c = NaN;
if margin(ages(1)) <= 0
  a_c = ages(1);
  return
end
for i = 2:numel(ages)
  if margin(ages(i)) <= 0
    lo = ages(i - 1); hi = ages(i);
    for k = 1:12
      mid = 0.5 * (lo + hi);
      if margin(mid) > 0, lo = mid; else, hi = mid; end
    end
    a_c = hi;
    return
  end
end
end
