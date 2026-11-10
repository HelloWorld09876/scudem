# When does a child outgrow a prosthetic socket?

**SCUDEM XI 2026 · Problem A: Pediatric Prosthetics · Team 26126**
Betgeri Aditya Nikhil, Sujal Patial, Rakshit Maheshwari (BITS Pilani, Dubai Campus, Dubai, UAE)
Coach: Padmanabhan Seshaiyer (George Mason University, Fairfax, Virginia, USA)

Picture a child with a below-elbow (transradial) prosthesis picking up a bottle. The socket was made to fit the arm on one particular day. The arm keeps growing, and the child keeps lifting things. We built a model to answer two questions: when does the socket have to be replaced, and when has the child grown so much that a replacement is no longer enough and the *design* needs to change?

The short version of what we found is in the table further down. One caution first: the second answer (the "window closure" age) depends on a few assumptions we could not pin down from data, and it moves by several years when you change them. We say so in the paper and show how much (scripts 11, 12 and 14; figures 14, 15 and 17). Please read that number as a rough guide and not as a measurement. The routine-replacement answer is now stated in a form that does not depend on the unmeasured pressure tolerance (script 13, figure 16), and it is compared with published clinical and anthropometric data (script 16, figure 19).

## Quick start

```bash
pip install -r requirements.txt
python -m pytest             # 31 tests of the physics and the data
python scripts/run_all.py    # all figures and results, about 6 minutes
```

To run just one step, give its number, for example `python scripts/run_all.py 04`. Every run also refreshes the numbers used in the paper (`scripts/export_numbers.py`, which writes `paper/generated/numbers.tex`), so the text and the results can't drift apart.

To build the paper: `cd paper && latexmk -pdf main.tex`.

There is also a separate MATLAB/Octave version of the core model, written independently, so the two can be compared. Run it after the Python pipeline:

```matlab
>> cd matlab
>> crosscheck
```

Run in GNU Octave 7+ on 10 Nov 2026 it agrees with the Python to within 3×10⁻⁴ (relative) on ten key quantities. Run it yourself before saying "MATLAB agrees" in the video.

## What's where

```
config/baseline.toml      every parameter, with notes on which ones are measured and which are assumed
data/raw/                 CDC 2000 stature-for-age and weight-for-age tables (LMS form)
src/pedsocket/            the model
  growth.py               Preece–Baines growth equation, fitted to the CDC curves
  body.py                 arm and forearm sizes from height and weight
  prosthesis.py           the socket, cylindrical or tapered
  kinematics.py           smooth arm movements (minimum jerk) and the dynamic number Π
  dynamics.py             the two-link arm: equations of motion and the loads on the socket
  interface.py            from socket loads to pressure on the limb; slipping ("pistoning")
  analytic.py             Model 0: the hold-still case in closed form, plus scaling laws
  lifetime.py             how long a socket lasts, replacement schedules, window closure
  slow_ode.py             Model 2 as a system of ODEs with failure as a solver event; girth budget
  msk.py                  Model 3: effect on the rest of the body
  uncertainty.py          random sampling of the uncertain inputs (Latin hypercube)
scripts/01_… to 16_…      one script per question we asked, in order
tests/                    automated checks
matlab/                   the independent MATLAB version, for cross-checking
paper/                    the technical report (LaTeX)
diagrams/                 the four explanation diagrams (LaTeX/TikZ sources and images)
figures/, results/        everything the scripts produce
```

## How the model is built

We started with the simplest thing we could solve exactly and added one idea at a time.

| Layer | What it does | Script |
|---|---|---|
| Growth | Height follows a growth equation fitted to the CDC curves (typical error 0.28 cm) | 01 |
| Model 0 | Holding an object still. A hand calculation gives the socket pressure and two scaling laws | 02 |
| Model 1 | The arm moves: four lifting actions, equations of motion, and one dimensionless number Π that says how "fast" a movement is | 03 |
| Model 2 | The child grows inside a fixed socket. Two ways to fail: the limb gets squeezed, or the socket rides up | 04 |
| Policy | Replacement schedules, loose-fit "growth allowance", and the window-closure age | 05, 06 |
| Uncertainty | Change each input by ±25 %, then 400 random combinations at once | 07 |
| Model 3 | What a too-short prosthesis does to reach and posture | 08 |
| Checks | Energy conservation, replaying the motion, the pistoning equation | 09 |
| Animation | The two GIFs used in the video | 10 |
| How firm is the closure age? | Re-run window closure under other reasonable assumptions | 11 |
| Hidden assumptions | Movement time that grows with size (κ); object share and tolerance as one ratio | 12 |
| Headroom law | The peak-pressure path of a frozen socket, which does not depend on the tolerance; lifetime for any tolerance | 13 |
| Closure probability | 600 random scenarios, including object share and κ, under two readings of residual-limb growth | 14 |
| ODE formulation | Model 2 written as ODEs with failure as an event; conserved quantity and girth budget; checked against the algebraic model | 15 |
| Validation | Comparison with clinical replacement intervals, children's pain thresholds, measured arm/wrist growth and growth-plate shares | 16 |

## Main results

| Question | Answer |
|---|---|
| Socket pressure at fitting, boy aged 8, 0.5 kg object: holding still / fast curl | 43.0 / 76.7 kPa. The movement matters more than the weight |
| How much does speed add? | Slow curls (Π below about 0.3) load the socket the same as holding still. For brisker movements the pressure ratio rises roughly as 0.64 + 1.00 Π. That line is only a fit (R² = 0.998); it misses the flat start by up to 0.30 |
| Socket life, boy fitted at 8: cylindrical / tapered | 21.6 / 16.7 months (at the assumed 100 kPa) |
| Months until peak pressure is 25 % above day one (no tolerance needed) | 19 cylindrical, 15 tapered for a boy fitted at 8; 11–26 across ages 6–12, both sexes, both sockets |
| Compared with clinics | Model median 17.5 months vs 16.4 ± 9.9 observed (Cambodia, lower limb, 62 casefiles). This tunes one parameter (the tolerance); it is a consistency check, not independent validation |
| Sockets needed from age 6 to 18, median boy: standard fit / growth-allowance fit | 6 / 5 |
| Window closure age, median boy / girl | 13.9 / 14.6 years in the baseline (soft, see below) |
| Closure in 600 random scenarios (boys) | happens before 18 in 58–88 % of them; median 14.3 or 9.9 years depending on how the residual limb grows |
| Window closure age, 90th-centile boy / girl | 11.8 / 11.4 years |
| Reach lost if the age-8 socket is never replaced, at age 12 | 4.0 cm, with about 5.3° of trunk lean |

### How much to trust the closure age

Not very much. The 13.9 years for boys comes with the baseline assumptions: an object of 2 % of body mass, a pressure tolerance of 100 kPa, a new socket that always leaves a residual limb of 45 % of the forearm, and a fast curl as the worst-case action. Small, plausible changes move it a lot:

- A heavier object moves it a long way: about 10 years at 2.5 % of body mass and about 7 at 3 %. A lighter one (1.5 %) never closes before 18.
- The pressure tolerance does the same: 75 kPa gives about 8 years, and 125 kPa means the window never closes before 18.
- Making the residual limb in each new socket follow the growth rule we use after fitting, instead of a flat 45 % of the forearm, brings it to roughly 10–12 years.
- Without the fast curl there is no closure at all. The hold, the slow curl and the lift to a shelf never get there, so the whole answer rides on that one movement.
- In the 400-sample random run, 14.5 % of samples are already closed at age 4, 33 % never close before 18, and the ones in between have a median of 11.5 years (90 % of them between 5.2 and 16.3). Only 11 % land within a year of the baseline.

What holds up better: closure comes earlier for larger children (11.8 and 11.4 years at the 90th centile), and across the random samples it is tied most closely to how much of the forearm the residual limb keeps. Figure 14 and the sensitivity section of the paper have the details.

## Limits worth knowing about

- The tissue values (how stiff the soft tissue is, how much pressure it tolerates) come from general biomechanics ideas, not from measurements on children. Treat the absolute pressures as illustrative and the trends as the result.
- We found no measured interface pressures for children's residual limbs. The clinic replacement data we compare with (Ghidini et al. 2025) are for lower-limb loss, and matching their mean fixes only one parameter, the tolerance.
- Modelled girth growth (+44 % for boys from 6 to 17) is a little above measured upper-arm (+39 %) and wrist (+29 %) growth, which makes our lifetimes somewhat short. Real residual-limb volume changes (up to 60 % a year reported) are far larger than growth alone.
- Our proximal growth share φ = 0.25 is above the 5–20 % implied by Pritchett (1991); lower values change the lifetime by about 1–2 months.
- The growth ODE describes the CDC curve (0.28 cm in-sample) but does not predict the growth spurt out of sample (1.9–6.4 cm).
- Nine of the ten checks in the verification table are automated tests. The tenth (pistoning) is a script, `scripts/09_verification.py`.
- Motion is planar, as the problem asks. Real children also rotate and twist.

## Use of AI tools

We used Claude (Anthropic) for a large part of this work: building the model, writing the code and tests, producing the figures, drafting the report, script and slides, and later reviewing and editing wording. The details, including which model was used when, are in our separate "Report on Use of AI Tools". The team chose the problem, directed the work and is responsible for the content. Any result you rely on should be re-run with the commands above.
