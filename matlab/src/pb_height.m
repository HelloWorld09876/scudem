function h = pb_height(t, q)
tau = t - q(5);
h = q(1) - 2 * (q(1) - q(2)) ./ (exp(q(3) * tau) + exp(q(4) * tau));
end
