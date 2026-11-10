function c = growth_child(sex, z, data_dir)
if nargin < 2, z = 0; end
code = 1 + strcmp(sex, 'girl');
[a_h, h] = centile(fullfile(data_dir, 'statage.csv'), code, z);
[a_w, w] = centile(fullfile(data_dir, 'wtage.csv'), code, z);
keep = a_h >= 3.95 & a_h <= 20.05;
a_h = a_h(keep); h = h(keep);
theta0 = 13.5 - 2 * (code == 2);
sse = @(q) sum((pb_height(a_h, q) - h).^2);
opts = optimset('MaxFunEvals', 4e4, 'MaxIter', 4e4, 'TolX', 1e-12, 'TolFun', 1e-12);
q = fminsearch(sse, [h(end), h(end) - 12, 0.1, 1.2, theta0], opts);
for k = 1:3
  q = fminsearch(sse, q, opts);
end
c.sex = sex;
c.pb = q;
c.rmse = sqrt(sse(q) / numel(h));
c.t = (4:0.005:20)';
rate = @(t, H) pb_rate(t, q) .* (q(1) - H);
[~, H] = ode45(rate, c.t, pb_height(4, q), odeset('RelTol', 1e-10, 'AbsTol', 1e-10));
c.H = H(:) / 100;
c.age_w = a_w;
c.w = w;
end

function [age, value] = centile(file, code, z)
d = dlmread(file, ',', 1, 0);
d = d(d(:, 1) == code, :);
[~, i] = sort(d(:, 2));
d = d(i, :);
age = d(:, 2) / 12;
L = d(:, 3); M = d(:, 4); S = d(:, 5);
value = M .* (1 + L .* S * z) .^ (1 ./ L);
end
