% crosscheck.m: does an independent MATLAB version of the model agree with the Python one?
%
% The functions in matlab/src are a separate re-implementation (not a translation tool), written to catch coding mistakes in
% the Python. This script runs them for the headline quantities and prints them next to the numbers Python saved in results/.
% Run scripts/run_all.py first so results/ is up to date, then run this file from MATLAB.
%
% What it covers: the growth fit, the four peak pressures at age 8, both socket lifetimes, and both window-closure ages.
% What it does not cover: the Monte Carlo, the musculoskeletal extension, the verification checks and the closure
% sensitivity study. Those are only in Python.

clear; clc;
here = fileparts(mfilename('fullpath'));
addpath(fullfile(here, 'src'));
root = fileparts(here);
data_dir = fullfile(root, 'data', 'raw');
results = fullfile(root, 'results');

p = default_params();
tapered = p; tapered.socket_shape = 'tapered';
growing = p; growing.load_mode = 'scaled';
boy = growth_child('boy', 0, data_dir);
girl = growth_child('girl', 0, data_dir);

py = struct();
py.growth = jsondecode(fileread(fullfile(results, '01_growth.json')));
py.tasks = jsondecode(fileread(fullfile(results, '03_lifting_dynamics.json')));
py.life = jsondecode(fileread(fullfile(results, '04_socket_over_growth.json')));
py.closure = jsondecode(fileread(fullfile(results, '06_window_closure.json')));

s8 = design_socket(boy, 8, p);
fields = {'Static hold', 'Slow curl', 'Fast curl', 'Lift to shelf'};
task_keys = fieldnames(py.tasks.tasks);
rows = {};
rows(end + 1, :) = {'PB fit RMSE, boy (cm)', boy.rmse, py.growth.boy.rmse_cm};
rows(end + 1, :) = {'PB fit RMSE, girl (cm)', girl.rmse, py.growth.girl.rmse_cm};
for k = 1:numel(p.tasks)
  r = socket_loads(p.tasks(k), boy, s8, 8, p);
  rows(end + 1, :) = {sprintf('%s peak pressure (kPa)', fields{k}), max(r.peak) / 1e3, py.tasks.tasks.(task_keys{k}).peak_pressure_kPa};
end
rows(end + 1, :) = {'Lifetime, cylindrical (months)', 12 * socket_lifetime(boy, 8, p), py.life.cylindrical.lifetime_months};
rows(end + 1, :) = {'Lifetime, tapered (months)', 12 * socket_lifetime(boy, 8, tapered), py.life.tapered.lifetime_months};
rows(end + 1, :) = {'Window closure, boy (years)', window_closure_age(boy, growing), py.closure.boy_50th};
rows(end + 1, :) = {'Window closure, girl (years)', window_closure_age(girl, growing), py.closure.girl_50th};

fprintf('\n%-36s %12s %12s %10s\n', 'quantity', 'MATLAB', 'Python', 'rel. diff');
fprintf('%s\n', repmat('-', 1, 74));
worst = 0;
for i = 1:size(rows, 1)
  d = abs(rows{i, 2} - rows{i, 3}) / max(abs(rows{i, 3}), 1e-12);
  worst = max(worst, d);
  fprintf('%-36s %12.4f %12.4f %10.1e\n', rows{i, 1}, rows{i, 2}, rows{i, 3}, d);
end
fprintf('%s\nlargest relative difference: %.1e\n', repmat('-', 1, 74), worst);
