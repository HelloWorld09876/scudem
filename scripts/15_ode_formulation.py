"""The socket-growth problem as a system of ODEs with a failure event (see src/pedsocket/slow_ode.py).

Verification done here:
  1. the ODE state (strain, fit pressure, radius, length, height) equals the algebraic model of interface_state() along a whole socket life;
  2. the event time equals socket_lifetime() (found by scanning and bisection) for 20 child/fitting-age combinations,
     for both failure modes (pressure for the standard fit, suspension for some patient-specific fits);
  3. a closed-form 'girth budget' brackets the lifetime;
  4. the time-scale separation behind the quasi-steady treatment of arm motion.
"""
import numpy as np
import matplotlib.pyplot as plt

from common import BASE, BOY, CHILDREN, FIT_AGE
from pedsocket import body_at, design_socket, interface_state
from pedsocket.lifetime import min_fit_strain, socket_lifetime
from pedsocket.plotting import LIMIT, record, save
from pedsocket.prosthesis import strain_for_pressure
from pedsocket.slow_ode import SECONDS_PER_YEAR, girth_budget, integrate_socket

BETA = BASE.soft_tissue_fraction

# --- 1. State agreement along one socket life ---------------------------------------------------------------------------
res = integrate_socket(BOY, FIT_AGE, BASE)
socket = design_socket(BOY, FIT_AGE, BASE)
alg = [interface_state(BOY, socket, float(t), BASE) for t in res.t]
alg_strain = np.array([a.tissue_strain for a in alg])
alg_fit = np.array([a.fit_pressure for a in alg])
alg_radius = np.array([a.radius for a in alg])
alg_len = np.array([a.residual_length for a in alg])
alg_h = np.array([100.0 * a.body.height for a in alg])
err = dict(
    height_rel=np.abs(res.y[0] - alg_h) / alg_h,
    length_rel=np.abs(res.y[1] - alg_len) / alg_len,
    radius_rel=np.abs(res.y[2] - alg_radius) / alg_radius,
    strain_abs=np.abs(res.y[3] - alg_strain),
    fit_pressure_rel=np.abs(res.y[4] - alg_fit) / np.maximum(alg_fit, 1.0),
)
for k, v in err.items():
    print(f"  max {k:16s} {v.max():.2e}")

# --- 2. Event time vs the original lifetime search ------------------------------------------------------------------------
rows, worst_gap = [], 0.0
for child in CHILDREN:
    for age in (5.0, 6.0, 8.0, 10.0, 12.0):
        for mode in ("standard", "patient-specific"):
            strain = None if mode == "standard" else min_fit_strain(child, age, BASE)
            ode = integrate_socket(child, age, BASE, strain)
            ref = socket_lifetime(child, age, BASE, strain)
            a, b = ode.months, ref.months
            same_end = (np.isnan(a) and np.isnan(b)) or (np.isfinite(a) and np.isfinite(b))
            gap = abs(a - b) if (np.isfinite(a) and np.isfinite(b)) else (0.0 if same_end else np.inf)
            worst_gap = max(worst_gap, gap)
            rows.append(dict(sex=child.sex, fit_age=age, fit=mode, ode_months=None if np.isnan(a) else a,
                             search_months=None if np.isnan(b) else b, ode_cause=ode.event, search_cause=ref.cause))
# Low skin-liner friction (0.30 instead of 0.50) makes suspension, not pressure, the limiting mode for some fits.
for child in CHILDREN:
    for age in (6.0, 8.0, 10.0):
        slip = BASE.updated(friction=0.30)
        strain = min_fit_strain(child, age, slip)
        ode, ref = integrate_socket(child, age, slip, strain), socket_lifetime(child, age, slip, strain)
        a, b = ode.months, ref.months
        gap = abs(a - b) if (np.isfinite(a) and np.isfinite(b)) else (0.0 if np.isnan(a) == np.isnan(b) else np.inf)
        worst_gap = max(worst_gap, gap)
        rows.append(dict(sex=child.sex, fit_age=age, fit="patient-specific, friction 0.30", ode_months=None if np.isnan(a) else a,
                         search_months=None if np.isnan(b) else b, ode_cause=ode.event, search_cause=ref.cause))
# A standard 5% fit with very low friction cannot hold the prosthesis on even on day one: the suspension event fires at once.
for child in CHILDREN:
    slip = BASE.updated(friction=0.12)
    ode, ref = integrate_socket(child, 8.0, slip), socket_lifetime(child, 8.0, slip)
    rows.append(dict(sex=child.sex, fit_age=8.0, fit="standard, friction 0.12", ode_months=ode.months, search_months=ref.months,
                     ode_cause=ode.event, search_cause=ref.cause))
    worst_gap = max(worst_gap, abs(ode.months - ref.months))
n_susp = sum(r["ode_cause"] == "suspension" for r in rows)
n_same_cause = sum((r["ode_cause"] or "none") == r["search_cause"] for r in rows)
print(f"  {len(rows)} lifetimes: largest |ODE event - search| = {worst_gap:.3f} months; same failure mode in {n_same_cause}/{len(rows)}; "
      f"{n_susp} suspension failures")

# --- 3. Closed-form girth budget -----------------------------------------------------------------------------------------
eps0 = socket.fit_strain
lift0, liftT = res.lift[0], res.lift[-1]
radius_ratio = res.y[2] / res.y[2][0]
identity_gap = np.max(np.abs(radius_ratio - (1 - BETA * eps0) / (1 - BETA * res.y[3])))       # (1 - beta e) r = const
budget0, budgetT = girth_budget(BASE, eps0, lift0), girth_budget(BASE, eps0, liftT)
def time_to_ratio(target):
    return 12 * (np.interp(target, np.maximum.accumulate(radius_ratio), res.t) - FIT_AGE)     # months; clamps at the event
t_hi, t_lo = time_to_ratio(budget0), time_to_ratio(budgetT)
girth_rate = float(np.log(radius_ratio[-1]) / (res.t[-1] - res.t[0]))
print(f"  conserved quantity (1-beta e) r: max drift {identity_gap:.1e}")
print(f"  girth budget: {100 * (budget0 - 1):.1f}% growth with day-one lift, {100 * (budgetT - 1):.1f}% with end-of-life lift; "
      f"mean girth growth {100 * girth_rate:.1f} %/yr -> lifetime between {t_hi:.1f} and {t_lo:.1f} months (ODE event {res.months:.2f})")

# --- 4. Time scales -----------------------------------------------------------------------------------------------------
t_arm = BASE.task("Fast curl").duration                    # s
t_growth = (res.event_age - FIT_AGE) * SECONDS_PER_YEAR      # s, one socket life
separation = t_arm / t_growth
print(f"  time-scale ratio  arm motion / one socket life = {t_arm:.1f} s / {t_growth:.2e} s = {separation:.1e}")

# --- Figure ------------------------------------------------------------------------------------------------------------------
months = 12 * (res.t - FIT_AGE)
tol = BASE.pressure_tolerance / 1e3
fig, ax = plt.subplots(1, 3, figsize=(17, 4.9))
ax[0].stackplot(months, res.lift / 1e3, res.y[4] / 1e3, colors=["#93c5fd", "#fdba74"], alpha=0.9,
                labels=["$p_{lift}(t)$ from the fast arm model", "$p_{fit}(t)$ from the ODE"])
ax[0].plot(months, (res.lift + res.y[4]) / 1e3, "k", lw=2)
ax[0].plot(months[::12], alg_fit[::12] / 1e3 + res.lift[::12] / 1e3, "o", ms=4, mfc="white", mec="k", label="algebraic model")
ax[0].axhline(tol, color=LIMIT, ls="--", lw=1.2)
ax[0].axvline(res.months, color=LIMIT, lw=1.2)
ax[0].text(res.months - 0.4, 6, f"event: p = p_tol\nat {res.months:.1f} months", ha="right", color=LIMIT, fontsize=9)
ax[0].set(xlabel="months since fitting (boy, fitted at 8)", ylabel="peak pressure (kPa)", ylim=(0, 130),
          title="Growth ODE, failure as an event")
ax[0].legend(fontsize=8.5, loc="upper left")

e_star = np.array([float(strain_for_pressure(BASE.pressure_tolerance - l, BASE)) for l in res.lift])
allowed = (1 - BETA * eps0) / (1 - BETA * e_star)
ax[1].plot(months, 100 * (radius_ratio - 1), color="#c2410c", lw=2.4, label="girth growth so far, $r(t)/r_0-1$")
ax[1].plot(months, 100 * (allowed - 1), color="#1f5fa8", lw=2.4, ls="--", label="girth growth the socket can absorb")
ax[1].axvline(res.months, color=LIMIT, lw=1.2)
ax[1].set(xlabel="months since fitting", ylabel="girth growth (%)", ylim=(0, 8),
          title=f"Girth budget: {100 * (budget0 - 1):.1f}–{100 * (budgetT - 1):.1f}% of growth ends a 5%-fit socket")
ax[1].legend(fontsize=8.5, loc="upper left")

for k, (name, c) in {"height_rel": ("height", "#4b5563"), "length_rel": ("residual length", "#15803d"),
                     "radius_rel": ("radius", "#c2410c"), "strain_abs": ("strain (abs.)", "#7c3aed"),
                     "fit_pressure_rel": ("fit pressure", "#1f5fa8")}.items():
    ax[2].semilogy(months, np.maximum(err[k], 1e-16), color=c, lw=1.8, label=name)
ax[2].set(xlabel="months since fitting", ylabel="|ODE − algebraic model|  (relative)", ylim=(1e-16, 1e-3),
          title=f"Verification: agreement to {max(v.max() for v in err.values()):.0e}")
ax[2].legend(fontsize=8.5, loc="upper left", ncol=2)
save(fig, "fig18_ode_formulation")

record("15_ode_formulation", dict(
    state_errors={k: float(v.max()) for k, v in err.items()}, lifetimes=rows, worst_gap_months=float(worst_gap),
    n_lifetimes=len(rows), n_same_cause=int(n_same_cause), n_suspension=int(n_susp),
    event_months=res.months, conserved_drift=float(identity_gap),
    budget_day_one_pct=100 * (budget0 - 1), budget_end_pct=100 * (budgetT - 1), girth_rate_pct_per_year=100 * girth_rate,
    bracket_months=[t_hi, t_lo], time_scale_ratio=separation, arm_time_s=t_arm, life_s=t_growth))
