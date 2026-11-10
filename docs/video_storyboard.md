# Video storyboard (10:00 maximum)

This is the plan for the recording. The exact words are in `Video_recording_script.md`. The timings below come from that script: 21 slides, about 1,256 spoken words, roughly 9:43 at a relaxed 135 words a minute with a short breath between slides. That is an estimate and it is tight, so time a full read-through with a stopwatch before recording. If you run over, cut the sentences marked (optional) on slides 9 and 15 first.

Speakers: A = Aditya, S = Sujal, R = Rakshit.

| Start | Slide | Who | What we say and show | Picture |
|---|---|---|---|---|
| 0:00 | 1 Title | A | Team 26126, Problem A, everyone's name and institution, coach and his university, city and country (the rules want all of this on the first screen) | title slide, all three faces |
| 0:16 | 2 The question | A | A socket fits on day one and the child keeps growing. When must it be replaced, and when is replacing it not enough? | sketch of a child's arm |
| 0:40 | 3 The arm | S | Below-elbow prosthesis; no growth plates at the far end of the limb, so the limb grows from the elbow end | d1_anatomy |
| 1:08 | 4 Assumptions | S | One plane, scaling with height and weight, tissue that stiffens when squeezed, a pressure limit for replacement | text only |
| 1:36 | 5 The ladder | R | Growth, static model, moving arm, growth coupling, policy, rest of the body | d2_ladder |
| 1:54 | 6 Growth | R | Preece–Baines growth equation fitted to the CDC curves, 0.28 cm typical error | fig01 |
| 2:17 | 7 Model 0 | A | Holding still: the socket pushes up near the elbow and down near the wrist; load spread over the engaged length | d3_free_body |
| 2:54 | 8 Scaling laws | S | Same object: pressure falls like (M·H)^(−1/2). Object scaled with the child: it rises like (M/H)^(+1/2) | fig02 |
| 3:23 | 9 Four actions | S | Hold, slow curl, fast curl, lift to a shelf; smooth minimum-jerk paths | fig03, anim_fast_curl.gif |
| 3:48 | 10 Speed beats weight | S | Same object: fast curl 77 kPa, holding 43 kPa. Slow curls match holding; brisker ones follow the Π line | fig05 |
| 4:14 | 11 Two ways to fail | R | Written as ODEs; failure is the first event. Cylindrical socket: the limb gets squeezed. Tapered socket: it rides up | d4_mechanisms, fig06 |
| 4:54 | 12 Socket life | R | No tolerance needed: peak pressure +25 % after 11–26 months. At 100 kPa a boy fitted at 8 gets 21.6 (cylindrical) / 16.7 (tapered) months; clinics replace every 16.4 months | fig16 |
| 5:27 | 13 **Substantial change** | A | The tug of war between a falling prosthesis load and a rising object load; closure at 13.9 (boys) and 14.6 (girls); earlier for larger children. Slow down here | fig09 |
| 6:06 | 14 How firm is that? | A | Not very. Object mass and tolerance move it by years; in 600 random scenarios closure before 18 happens in 58–88 %, mostly when the load is a large share of body mass | fig17 (fig14 optional) |
| 6:45 | 15 Replacement schedule | R | Standard fit: 6 sockets for a median boy. Growth-allowance fit: 5 | fig08 |
| 7:11 | 16 The rest of the body | S | An unreplaced age-8 socket costs 4 cm of reach at 12, with some trunk lean | fig12 |
| 7:36 | 17 Checking the maths | R | 31 automated tests, energy conservation, ODE event vs direct search; say the MATLAB/Octave line only after the cross-check has agreed | fig13, fig18 |
| 8:04 | 18 Uncertainty | R | Ranges and 400 random parameter sets; closure age spread widely | fig10, fig11 |
| 8:30 | 19 Answers | A | The four questions, answered in plain words, with the caveat on closure | text only |
| 9:04 | 20 Strengths and limits | R | Real growth data, scaling laws and heavy checking; less sure of tissue values and the closure age | text only |
| 9:33 | 21 Thanks | A | QR code to the public repository; all faces | QR code |

## Before recording

- Rehearse once with a stopwatch. Aim to finish by 9:45 to leave a safety margin.
- Put the real GitHub link and QR code on slide 21 (it is a placeholder in the slide file).
- Few words on screen, faces on camera, clean audio.
- If you use any AI feature in editing (auto-captions, noise removal, speech enhancement, a synthetic voice), write down the tool, version, purpose and where in the video it appears. It goes in the "Report on Use of AI Tools". If the video shows an AI-generated animation, label it on screen.

Tips from earlier outstanding videos, from our coach's planning document: explain the context before the equations, keep slides light, rehearse, and say plainly what the model can't do.
