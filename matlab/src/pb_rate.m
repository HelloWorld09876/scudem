function s = pb_rate(t, q)
tau = t - q(5);
a = exp(q(3) * tau);
b = exp(q(4) * tau);
s = (q(3) * a + q(4) * b) ./ (a + b);
end
