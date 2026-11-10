function out = socket_loads(task, c, s, age, p, n)
if nargin < 6, n = 81; end
g = 9.81;
st = interface_state(c, s, age, p);
T = task.duration / p.speed_factor;
t = linspace(0, T, n)';
[q1, w1, a1] = min_jerk(task.shoulder * pi / 180, T, t);
[q2, w2, a2] = min_jerk(task.elbow * pi / 180, T, t);
phi = q1 + q2; dphi = w1 + w2; ddphi = a1 + a2;
L1 = st.body.upper_arm_length;
if strcmp(p.load_mode, 'fixed'), m_o = p.object_mass; else, m_o = p.object_fraction * st.body.mass; end
D = [p.prosthesis_mass, st.offset + p.prosthesis_com * s.length, p.prosthesis_mass * (p.prosthesis_gyration * s.length)^2;
     m_o, st.grip, 0];
axis = [sin(phi), -cos(phi)];
normal = [cos(phi), sin(phi)];
elbow_acc = L1 * (a1 .* [cos(q1), sin(q1)] + w1.^2 .* [-sin(q1), cos(q1)]);
axis_acc = ddphi .* normal + dphi.^2 .* [-sin(phi), cos(phi)];
F = zeros(n, 2);
M = zeros(n, 1);
for i = 1:rows(D)
  f = D(i, 1) * (elbow_acc + D(i, 2) * axis_acc - repmat([0, -g], n, 1));
  F = F + f;
  M = M + (D(i, 2) - st.offset) * (axis(:, 1) .* f(:, 2) - axis(:, 2) .* f(:, 1)) + D(i, 3) * ddphi;
end
V = sum(F .* normal, 2);
A = sum(F .* axis, 2);
L = st.engaged;
q0 = 4 * V / L - 6 * M / L^2;
qL = -2 * V / L + 6 * M / L^2;
out.moment_pressure = 2 * max(abs(q0), abs(qL)) / (pi * st.radius);
out.peak = st.fit_pressure + out.moment_pressure;
out.pull_out = max(0, -A);
out.state = st;
end

function [q, w, a] = min_jerk(range, T, t)
tau = min(max(t / T, 0), 1);
d = range(2) - range(1);
q = range(1) + d * (10 * tau.^3 - 15 * tau.^4 + 6 * tau.^5);
w = d * (30 * tau.^2 - 60 * tau.^3 + 30 * tau.^4) / T;
a = d * (60 * tau - 180 * tau.^2 + 120 * tau.^3) / T^2;
end

function r = rows(X)
r = size(X, 1);
end
