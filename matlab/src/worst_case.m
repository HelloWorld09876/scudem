function w = worst_case(c, s, age, p)
w.peak = 0;
w.pull_out = 0;
w.task = '';
for k = 1:numel(p.tasks)
  r = socket_loads(p.tasks(k), c, s, age, p);
  if max(r.peak) > w.peak
    w.peak = max(r.peak);
    w.task = p.tasks(k).name;
  end
  w.pull_out = max(w.pull_out, max(r.pull_out));
end
w.state = r.state;
w.ssi = w.peak / p.pressure_tolerance;
area = 2 * pi * r.state.radius * r.state.engaged;
w.suspension = p.friction * r.state.fit_pressure * area / max(w.pull_out, 1e-12);
w.failed = w.ssi > 1 || w.suspension < 1;
end
