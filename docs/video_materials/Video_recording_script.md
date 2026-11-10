# Team 26126 · Video recording script

Nov 10, 2026 · @Sujal

## How to use this script

Read at a relaxed 135 words a minute, with a short breath between slides, the whole thing runs about 9:43, so you have a little under twenty seconds of slack under the 10:00 limit. It is 1,256 spoken words split between the three of you: Aditya 426, Sujal 348, Rakshit 482. If you run long, cut the sentences marked (optional) on slides 9 and 15 first (about 10 seconds).

- **A** = Aditya, **S** = Sujal, **R** = Rakshit. Swap names freely. Whoever can't be in the room can record his parts as voice-over and send the audio.
- Each block shows the slide number, roughly when it starts, and the words. Things in [brackets] are actions, not speech.
- Say the numbers slowly and point at the figure while you talk about it.
- Don't memorise it word for word. Say it the way you'd explain it to a friend, as long as the numbers stay the same.
- If you run long, cut a sentence marked (optional), never a result.
- Second-pass changes (Nov 10): slide 3 (growth-plate share), 11 (ODE sentence), 12 (new figure `fig16_headroom_law.png` and new text), 14 (new figure `fig17_closure_probability.png` and new text), 17 (31 tests, ODE check, Octave), 19 and 20 (one clause each). The optional sentences on slides 10 and 18 were removed to keep the time. If you already recorded, see "If you already recorded" at the end.
- Slide 14 from the first pass used `fig14_closure_sensitivity.png`; it can stay on screen as a second panel, but the words now go with `fig17`.
- Rehearse once with a stopwatch before you record. The hard limit is 10:00.

## Part 1: opening (0:00 to 1:53)

**Slide 1 · 0:00 · A** [title slide on screen, all three faces visible]

"Hi, we're Team 26126 from BITS Pilani, Dubai Campus. I'm Aditya, with Sujal and Rakshit. Our coach is Professor Padmanabhan Seshaiyer from George Mason University. This is our take on SCUDEM Problem A, pediatric prosthetics."

**Slide 2 · 0:16 · A**

"A prosthetic arm can change a child's life. But the socket is shaped to the arm on the day it's made, and the child keeps growing. So: when must the socket be replaced? And when is the change so big that a new socket of the same design isn't enough?"

**Slide 3 · 0:40 · S** [anatomy diagram]

"We looked at a below-elbow, or transradial, prosthesis: a residual limb in a rigid socket, carrying the hand. One fact shapes everything. About 80 to 85 percent of forearm growth in length comes from growth plates at the wrist end, and this child doesn't have them. So the limb gets wider much faster than longer. The socket problem is mostly about girth."

**Slide 4 · 1:08 · S** [assumptions]

"Our main assumptions. The arm moves in one plane, as the problem asks. Body segments scale with height and weight. Soft tissue gets stiffer the harder you squeeze it. And a socket has to be replaced when peak pressure passes 100 kilopascals, or when friction can't hold it on. That 100 is a judgment call. We'll come back to it."

**Slide 5 · 1:36 · R** [model ladder]

"We built the answer as a ladder: growth, then a static model, a dynamic lifting model, growth coupling, a replacement policy, and finally the rest of the body. Each step is checked against the one below."

## Part 2: the models (1:54 to 5:26)

**Slide 6 · 1:54 · R** [growth figure]

"Growth comes first. We use the Preece–Baines model, written as a differential equation: growth speed depends on how far the child still has to grow, and a rate switches from a childhood value to a puberty value. That switch is the growth spurt. Fitted to CDC data, it's within 0.28 centimetres."

**Slide 7 · 2:17 · A** [free-body diagram]

"Model zero is the simplest case: holding an object still. Its weight tries to rotate the prosthesis downward, so the socket pushes up on the limb near the elbow and down near the end. Assume the load varies linearly, and force and moment balance give the edge loads. Peak pressure comes out at about twelve times the moment, over pi r L squared. So pressure goes with one over the engaged length squared, and short residual limbs are fragile."

**Slide 8 · 2:54 · S** [scaling laws]

"That gives two scaling laws. For the same bottle at every age, pressure in a new socket falls as mass times height to the power minus a half: bigger kids cope better. But if objects grow with the child, that part rises as mass over height to the power plus a half. The code confirms both exponents. Keep this tug of war in mind."

**Slide 9 · 3:23 · S** [four actions, animation]

"Model one lets the arm move. We made four simple actions: a hold, a slow curl, a fast curl and a lift to a shelf, with minimum-jerk paths, *which is close to how people move* (optional). Lagrange's equations give the joint torques, and Newton–Euler on the prosthesis gives the load at the socket."

**Slide 10 · 3:48 · S** [collapse figure]

"Here's what surprised us. With the same half-kilogram object, a fast curl gives 77 kilopascals and just holding it gives 43. Speed, not weight, is the danger. A dimensionless number, pi, compares inertial load to gravity. Below about 0.3, a curl loads the socket like the hold. Above that, pressure climbs roughly one for one with pi."

**Slide 11 · 4:14 · R** [two mechanisms]

"Model two freezes the socket and lets the child grow. We write it as a system of differential equations for length, girth, tissue strain and pressure, and the socket's life ends at the first event where pressure hits the tolerance. It fails in two ways. In a cylindrical socket the fatter limb gets squeezed, and because tissue stiffens, the squeeze grows exponentially. In a tapered socket the limb gets pushed out instead. That relieves the squeeze but shortens the engaged length, and then lifting pressure takes over."

**Slide 12 · 4:54 · R** [headroom figure, fig16]

"Nobody has measured a pressure tolerance in children, so we report something that doesn't need one: how fast peak pressure rises. Twenty-five percent above day one takes 11 to 26 months across ages and sexes. With our 100 kilopascals, a boy fitted at eight gets 21.6 months in a cylindrical socket and 16.7 in a tapered one. Clinics in Cambodia replace every 16 months on average, so we're in the right range."

## Part 3: the answers (5:27 to 8:29)

**Slide 13 · 5:27 · A** [window closure, the key slide. Slow down here]

"Now the point of substantial change. Remember the tug of war: the prosthesis part of the pressure falls with growth, the object part rises. The safety margin of a brand-new socket shrinks to zero at 13.9 years for boys and 14.6 for girls, in our baseline. After that, no socket of this design stays under the tolerance. Refitting isn't enough; the design must change. For larger children it's two to three years earlier, so screening should follow body size and limb length, not age alone."

**Slide 14 · 6:06 · A** [closure probability figure, fig17]

"How much should you trust 13.9? Not too much. An object of 2.5 percent of body mass instead of 2 moves closure to about 10 years. A lighter object, or 125 kilopascals, and it doesn't happen before 18. So we ran 600 random scenarios. Closure happens before 18 in 58 to 88 percent of them, depending on how the residual limb grows, and mostly when the everyday load is a big share of body mass. So it's a condition to screen for, not an age."

**Slide 15 · 6:45 · R** [replacement schedule]

"Simulating every socket from age six to eighteen, a standard tight fit takes six sockets for a median boy. Fitting each one as loose as is safe, a growth allowance, takes five. For the median girl it makes no difference. *In a remote area, one fewer socket is one less fabrication and one less long journey.* (optional)"

**Slide 16 · 7:11 · S** [musculoskeletal]

"Model three looks beyond the socket. The prosthesis length is fixed while the other arm grows. If the socket fitted at eight is never replaced, by twelve the prosthetic arm is four centimetres short, and the child leans the trunk about five degrees to compensate. These are trends to watch, not injury predictions."

**Slide 17 · 7:36 · R** [verification. Say the last sentence only after you have run the Octave check and it agrees]

"How do we know the maths is right? 31 automated tests. A freely swinging arm conserves energy to about one part in a hundred billion. Two ways of computing the elbow torque agree to machine precision. The differential-equation event matches a direct search to a thousandth of a month. And a separate MATLAB version, run in Octave, matches the Python."

**Slide 18 · 8:04 · R** [Monte Carlo]

"Some inputs, like tissue stiffness, are uncertain, so we ran 400 random parameter sets. A patient-specific fit raises the median socket life from 17.5 to 21.1 months, and the pressure on fitting day predicts how long a socket lasts. So: measure pressure during a brisk lift at fitting, and let the model schedule the next review."

## Part 4: conclusion (8:30 to 9:43)

**Slide 19 · 8:30 · A** [answers]

"To answer the problem. Socket load is a moment over the engaged length squared, and fast movement raises it. Growth acts mostly through girth. For a boy fitted at eight, routine replacement comes 17 to 22 months after fitting, close to what clinics see. The fit window closes around 14 in our baseline, but whether it closes at all depends on the load and the limb. That needs a redesign, not a refit."

**Slide 20 · 9:04 · R** [strengths and limitations]

"We're happy with the real growth data, the scaling laws, a clear rule for speed, and a lot of checking. We're less sure about the tissue values and the 100 kilopascal tolerance, which are assumptions, not child measurements, and the clinic data we compared with are for legs. We also use adult proportions and an idealised socket. Next: pressure sensors, and a 3D socket."

**Slide 21 · 9:33 · A** [thank-you slide, QR code, all faces]

"All our code, data and the full report are public: scan the QR code. Thanks for watching!" [all three] "Thank you!"

## Recording and submission checklist

- ☐ First screen shows team 26126, Problem A and its title, and every name with institution, city and country (the rules require it)
- ☐ Quiet room, headset microphone, faces visible at least at the start and end
- ☐ One timed rehearsal, final cut under 10:00
- ☐ Slides 12 and 14 show the new figures (`fig16`, `fig17`); slides 10 and 13 use `fig05` and `fig09`
- ☐ Run `matlab/crosscheck.m` in Octave and confirm it agrees before you say the MATLAB line on slide 17 (cut that sentence if you haven't)
- ☐ Repository pushed to a public GitHub, link and QR code added to slide 21
- ☐ Every reference in the report checked against the real paper
- ☐ If you used any AI feature while editing the video (auto-captions, noise removal, a synthetic voice), list it in the AI report with the tool, version and where it was used
- ☐ Video uploaded to YouTube with visibility set to **Unlisted**
- ☐ SCUDEM Team Video Submission Form sent with the YouTube link
- ☐ The AI report submitted with the form, as a separate PDF titled "Report on Use of AI Tools"
- ☐ All of this done by about 8 PM Dubai time on Tuesday. The hard deadline is 3 PM EST, which is midnight Dubai time

## If you already recorded

Re-record only these three slides; everything else can stay:

1. **Slide 12** (most important): the old last sentence, "We haven't checked that against clinic data yet", is no longer true. Use the new slide 12 text.
2. **Slide 14**: the new text replaces the "flaw in our own baseline" sentences with the 600-scenario result.
3. **Slide 17**: "19 automated tests" is now 31.

If you can't re-record at all, the old video is still correct as an "as-assumed baseline"; nothing in it is contradicted by the new report except the test count and the "not checked against clinic data" sentence.
