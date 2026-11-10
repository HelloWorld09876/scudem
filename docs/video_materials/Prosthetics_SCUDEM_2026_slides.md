<!-- Revised slide text for the SCUDEM video (second pass, Nov 10). Images are not included.
What changed in the second pass:
- Slide 3: growth-plate share 80-85 % (Pritchett 1991).
- Slide 12: new picture figures/fig16_headroom_law.png and new text (tolerance-free lifetime + clinic comparison).
- Slide 14: new picture figures/fig17_closure_probability.png and new text (600-scenario closure probability).
- Slide 17: 31 tests, ODE event check, Octave. Slides 19 and 20: one line each.
- The speaker notes are regenerated from docs/video_materials/Video_recording_script.md.
First pass (kept): slide 14 added; pictures fig02, fig05, fig07, fig09, fig11 as before.
-->

## Slide 1

SCUDEM XI 2026 · TEAM 26126 · PROBLEM A:

PEDIATRIC PROSTHETICS When does a child outgrow a prosthetic socket?

A growth-coupled model of the transradial limb–socket interface Betgeri Aditya Nikhil · Sujal Patial · Rakshit Maheshwari BITS Pilani, Dubai Campus, Dubai, United Arab Emirates Coach:

Padmanabhan Seshaiyer George Mason University, Fairfax, Virginia, United States

> **Speaker Notes:**
> A, 0:00. Hi, we're Team 26126 from BITS Pilani, Dubai Campus. I'm Aditya, with Sujal and Rakshit. Our coach is Professor Padmanabhan Seshaiyer from George Mason University. This is our take on SCUDEM Problem A, pediatric prosthetics.

---

## Slide 2

Two questions about a growing child A socket is shaped to the arm on the day it is made.

The child keeps growing.

When must the socket be replaced?

When is the change so big that a new socket of the same design is not enough?

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> A, 0:16. A prosthetic arm can change a child's life. But the socket is shaped to the arm on the day it's made, and the child keeps growing. So: when must the socket be replaced? And when is the change so big that a new socket of the same design isn't enough?

---

## Slide 3

The child's arm and prosthesis 80–85 % of forearm length growth comes from the wrist-end growth plates, which this child lacks.

So the limb gets wider much faster than longer: the socket problem is mostly about girth.

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> S, 0:40. We looked at a below-elbow, or transradial, prosthesis: a residual limb in a rigid socket, carrying the hand. One fact shapes everything. About 80 to 85 percent of forearm growth in length comes from growth plates at the wrist end, and this child doesn't have them. So the limb gets wider much faster than longer. The socket problem is mostly about girth.

---

## Slide 4

Assumptions Motion in one plane Shoulder fixed; the arm moves in the sagittal plane, as the problem asks.

Body scales with growth Segment lengths ∝ height, masses ∝ body mass (CDC 2000 data).

Tissue stiffens when squeezed p = (E/B)(e^(Bε) − 1): exponential soft-tissue law.

When to replace Peak pressure above 100 kPa (our judgment call), or friction can no longer hold the prosthesis on.

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> S, 1:08. Our main assumptions. The arm moves in one plane, as the problem asks. Body segments scale with height and weight. Soft tissue gets stiffer the harder you squeeze it. And a socket has to be replaced when peak pressure passes 100 kilopascals, or when friction can't hold it on. That 100 is a judgment call. We'll come back to it.

---

## Slide 5

Our approach: a ladder of models

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> R, 1:36. We built the answer as a ladder: growth, then a static model, a dynamic lifting model, growth coupling, a replacement policy, and finally the rest of the body. Each step is checked against the one below.

---

## Slide 6

Growth model dH/dt = s(t) · (h₁ − H) Preece–Baines ODE, fitted to CDC data to within 0.28 cm

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> R, 1:54. Growth comes first. We use the Preece–Baines model, written as a differential equation: growth speed depends on how far the child still has to grow, and a rate switches from a childhood value to a puberty value. That switch is the growth spurt. Fitted to CDC data, it's within 0.28 centimetres.

---

## Slide 7

Model 0: the static socket Pressure goes with 1 / (engaged length)².

Short residual limbs are fragile.

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> A, 2:17. Model zero is the simplest case: holding an object still. Its weight tries to rotate the prosthesis downward, so the socket pushes up on the limb near the elbow and down near the end. Assume the load varies linearly, and force and moment balance give the edge loads. Peak pressure comes out at about twelve times the moment, over pi r L squared. So pressure goes with one over the engaged length squared, and short residual limbs are fragile.

---

## Slide 8

Model 0: scaling laws (exact within the model) p ∝ (MH)⁻½ same 0.5 kg object: pressure falls p ∝ (M/H)⁺½ object grows with child: pressure rises −0.500 / +0.500 both exponents confirmed by the code

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> S, 2:54. That gives two scaling laws. For the same bottle at every age, pressure in a new socket falls as mass times height to the power minus a half: bigger kids cope better. But if objects grow with the child, that part rises as mass over height to the power plus a half. The code confirms both exponents. Keep this tug of war in mind.

---

## Slide 9

Model 1: four lifting actions M(q) q̈ + C(q, q̇) + G(q) = τ Lagrange equations · minimum-jerk paths · Newton–Euler socket loads

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> S, 3:23. Model one lets the arm move. We made four simple actions: a hold, a slow curl, a fast curl and a lift to a shelf, with minimum-jerk paths, which is close to how people move. Lagrange's equations give the joint torques, and Newton–Euler on the prosthesis gives the load at the socket.

---

## Slide 10

Speed, not weight, drives the load fast curl, colour = socket pressure 43 kPa holding 0.5 kg still 77 kPa same object, fast curl Π < 0.3: a curl loads the socket like the hold. Above that, load climbs roughly 1:1 with Π (straight-line fit 0.64 + 1.00 Π, R² = 0.998, misses the flat start)

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> S, 3:48. Here's what surprised us. With the same half-kilogram object, a fast curl gives 77 kilopascals and just holding it gives 43. Speed, not weight, is the danger. A dimensionless number, pi, compares inertial load to gravity. Below about 0.3, a curl loads the socket like the hold. Above that, pressure climbs roughly one for one with pi.

---

## Slide 11

Model 2: two ways a socket is outgrown

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> R, 4:14. Model two freezes the socket and lets the child grow. We write it as a system of differential equations for length, girth, tissue strain and pressure, and the socket's life ends at the first event where pressure hits the tolerance. It fails in two ways. In a cylindrical socket the fatter limb gets squeezed, and because tissue stiffens, the squeeze grows exponentially. In a tapered socket the limb gets pushed out instead. That relieves the squeeze but shortens the engaged length, and then lifting pressure takes over.

---

## Slide 12

How long a socket lasts, without assuming a tolerance [picture: fig16_headroom_law.png] Peak pressure +25 % after 11–26 months (ages 6–12, both sexes, both sockets) 21.6 months cylindrical, 16.7 months tapered (boy fitted at 8, 100 kPa) Clinics (Cambodia, lower limb): replaced every 16.4 ± 9.9 months

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> R, 4:54. Nobody has measured a pressure tolerance in children, so we report something that doesn't need one: how fast peak pressure rises. Twenty-five percent above day one takes 11 to 26 months across ages and sexes. With our 100 kilopascals, a boy fitted at eight gets 21.6 months in a cylindrical socket and 16.7 in a tapered one. Clinics in Cambodia replace every 16 months on average, so we're in the right range.

---

## Slide 13

The fit window closes (in our baseline) 13.9 y boys: a new socket can no longer cope 14.6 y girls 2–3 y earlier for large (90th centile) children

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> A, 5:27. SLOW DOWN HERE. Now the point of substantial change. Remember the tug of war: the prosthesis part of the pressure falls with growth, the object part rises. The safety margin of a brand-new socket shrinks to zero at 13.9 years for boys and 14.6 for girls, in our baseline. After that, no socket of this design stays under the tolerance. Refitting isn't enough; the design must change. For larger children it's two to three years earlier, so screening should follow body size and limb length, not age alone.

---

## Slide 14

How firm is 13.9 years? [picture: fig17_closure_probability.png; fig14 optional as a second panel]

Object 2.5 % of body mass → about 10 y; 1.5 % or 125 kPa → no closure before 18

600 random scenarios: closure before 18 in 58–88 %

Driven by load share of body mass and residual-limb length

A condition to screen for, not an age.

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> A, 6:06. How much should you trust 13.9? Not too much. An object of 2.5 percent of body mass instead of 2 moves closure to about 10 years. A lighter object, or 125 kilopascals, and it doesn't happen before 18. So we ran 600 random scenarios. Closure happens before 18 in 58 to 88 percent of them, depending on how the residual limb grows, and mostly when the everyday load is a big share of body mass. So it's a condition to screen for, not an age.

---

## Slide 15

A cheaper policy:

6 → 5 sockets (median boy; no change for the median girl) Fit each socket as loose as safely possible (a growth allowance): one fewer fabrication and one fewer clinic journey per childhood.

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> R, 6:45. Simulating every socket from age six to eighteen, a standard tight fit takes six sockets for a median boy. Fitting each one as loose as is safe, a growth allowance, takes five. For the median girl it makes no difference. In a remote area, one fewer socket is one less fabrication and one less long journey.

---

## Slide 16

Model 3: beyond the socket 4.0 cm reach deficit at age 12 if never replaced 5.3° trunk lean to reach the same target < 2 cm deficit when replaced on schedule

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> S, 7:11. Model three looks beyond the socket. The prosthesis length is fixed while the other arm grows. If the socket fitted at eight is never replaced, by twelve the prosthetic arm is four centimetres short, and the child leans the trunk about five degrees to compensate. These are trends to watch, not injury predictions.

---

## Slide 17

Verification:

31 automated tests 10⁻¹¹ energy drift, free swing 4×10⁻¹⁶ Lagrange vs Newton–Euler, N·m 0.001 month ODE failure event vs direct search (28 cases) independent MATLAB code, run in Octave (show only after crosscheck.m agrees)

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> R, 7:36. How do we know the maths is right? 31 automated tests. A freely swinging arm conserves energy to about one part in a hundred billion. Two ways of computing the elbow torque agree to machine precision. The differential-equation event matches a direct search to a thousandth of a month. And a separate MATLAB version, run in Octave, matches the Python.

---

## Slide 18

Uncertainty:

400 Monte Carlo samples 17.5 → 21.1 mo median lifetime with a patient-specific fit ρ = −0.78 fitting-day pressure predicts lifetime 24 % fail on day one with the fast curl; 33 % never close before 18 Limb length is the strongest driver of the closure age

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> R, 8:04. Some inputs, like tissue stiffness, are uncertain, so we ran 400 random parameter sets. A patient-specific fit raises the median socket life from 17.5 to 21.1 months, and the pressure on fitting day predicts how long a socket lasts. So: measure pressure during a brisk lift at fitting, and let the model schedule the next review.

---

## Slide 19

Answers to the problem Load = moment / L² Fast motion raises it, roughly in step with Π.

Growth acts through girth The residual limb barely lengthens.

Replace 17–22 months after fitting (boy fitted at 8), close to clinic records Redesign at window closure: ≈ age 14 in our baseline, but whether it happens depends on load and limb.

An outgrown arm loads the trunk 4 cm short by 12 means ≈ 5° of lean.

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> A, 8:30. To answer the problem. Socket load is a moment over the engaged length squared, and fast movement raises it. Growth acts mostly through girth. For a boy fitted at eight, routine replacement comes 17 to 22 months after fitting, close to what clinics see. The fit window closes around 14 in our baseline, but whether it closes at all depends on the load and the limb. That needs a redesign, not a refit.

---

## Slide 20

Strengths and limitations Strengths Real CDC growth data, 0.28 cm fit Scaling laws that follow exactly from the model Clear rule for speed: flat below Π ≈ 0.3, then roughly linear 31 tests, an ODE event check and an independent MATLAB/Octave check Limitations and next steps Tissue values and the 100 kPa tolerance are assumptions: calibrate with pressure sensors Clinic comparison data are lower-limb Closure age depends on load, tolerance and limb growth Adult body proportions Idealised socket: model it in 3D Add bone overgrowth of the residual limb

Team 26126 · SCUDEM XI 2026 · Problem A:

Pediatric Prosthetics

> **Speaker Notes:**
> R, 9:04. We're happy with the real growth data, the scaling laws, a clear rule for speed, and a lot of checking. We're less sure about the tissue values and the 100 kilopascal tolerance, which are assumptions, not child measurements, and the clinic data we compared with are for legs. We also use adult proportions and an idealised socket. Next: pressure sensors, and a 3D socket.

---

## Slide 21

Thank you Code, data and full report are public: scan the QR code. [github.com/____/scudem-2026-team26126] Team 26126 · Aditya · Sujal · Rakshit [QR code]

> **Speaker Notes:**
> A, 9:33. All our code, data and the full report are public: scan the QR code. Thanks for watching! All three: Thank you!

---
