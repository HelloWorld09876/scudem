function years = socket_lifetime(c, fit_age, p, fit_strain)
if nargin < 4, fit_strain = []; end
s = design_socket(c, fit_age, p, fit_strain);
failed = @(age) getfield(worst_case(c, s, age, p), 'failed');
previous = fit_age;
age = fit_age;
while age <= min(fit_age + 8, 20) + 1e-9
  if failed(age)
    if age == fit_age
      years = 0;
      return
    end
    lo = previous; hi = age;
    for k = 1:10
      mid = 0.5 * (lo + hi);
      if failed(mid), hi = mid; else, lo = mid; end
    end
    years = hi - fit_age;
    return
  end
  previous = age;
  age = age + 1 / 12;
end
years = NaN;
end
