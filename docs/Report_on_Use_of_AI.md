# Team 26126 · Report on Use of AI Tools

Nov 10, 2026 · @Sujal

*(Export this as a PDF titled exactly "Report on Use of AI Tools". COMAP asks for it as a separate file with the video submission form, and there is no page limit.)*

## The short, honest version

We used AI a lot. Claude (Anthropic) did most of the technical work in this submission: it proposed the model, wrote and ran the code, produced the figures, and drafted the report, the video script and the slides. We chose Problem A, told it what to do at every step, and read and checked what came back. We record the video ourselves.

There were three working sessions with Claude, and we also asked Google Gemini for one opinion:

| | Session 1 | Session 2 | Session 3 | Gemini |
| --- | --- | --- | --- | --- |
| **Tool and model** | Claude Opus 5.5 (Anthropic), in the claude.ai chat with its code-execution tools | Claude Sonnet 5.5 (`claude-sonnet-5-5`), working in claude.ai with a file and code environment | Claude (Anthropic) in claude.ai with a file and code environment; the model changed during the session (Claude Sonnet 5.5, Claude Fable 5.2 and Claude Opus 5.5). *Check the names your chat shows and correct this cell if needed.* | Google Gemini *(fill in the version shown in the app)* |
| **Dates** | 9–10 November 2026 | 10 November 2026 | 10 November 2026 | 10 November 2026 |
| **What it was used for** | Building everything: model, Python and MATLAB code, simulations and figures, the LaTeX report, explanation notes, video script, slides | Reviewing the whole project as a critic, re-running it, fixing weak spots, and rewriting wording that read as machine-written | A second critical review and rating, then new analyses (tolerance-free lifetime, ODE/event formulation, closure probability, comparison with published data), 12 new tests, and updates to the report, script, slides and documents | A general opinion and rating of the project. Nothing from its answer was used in the submission |

Version dates: the dates above are the days we used each model. If the app shows a more exact version or build date, add it here.

**Data.** The CDC 2000 growth reference tables (LMS parameters) came from a public open-source mirror of the official CDC files. No data was made up by AI.

## What the AI did and what we did

| Stage | What the AI did | What we did |
| --- | --- | --- |
| Problem choice | Summarised the challenge rules and past winning approaches from our coach's planning notes | Chose Problem A |
| Modelling | Proposed the ladder of models: growth ODE, static socket, two-link arm, growth coupling, musculoskeletal extension | Asked for more depth and a simpler first model; reviewed the structure |
| Data | Found and extracted the CDC 2000 tables from a public mirror | Confirm the source against the CDC website |
| Code | Wrote the Python package, tests, analysis scripts and an independent MATLAB version, and ran them | Run the code and tests on our own machines |
| Results | Produced the figures, numbers and uncertainty analysis | Review each result to see if it makes physical sense |
| Report | Drafted the LaTeX report and the reference list | Check every reference against the original source |
| Video | Drafted the notes, script and slides | Rehearse, edit, record and present |
| Review and cleanup (session 2) | Reviewed and rated the project, tested how firm our headline result is, added one new analysis, corrected overstated claims, and rewrote wording, comments and documents | Read the changes and decide what stays |
| Robustness and validation (session 3) | Reviewed and rated the project again; added scripts 12–16 and `src/pedsocket/slow_ode.py`; searched for published data and compared the model with it; rewrote parts of the paper, script and slides | Check the new references, run the code, decide what stays, re-record the affected video slides |

## Exact prompts and outputs

COMAP's policy asks for the exact query and the complete output for chat assistants. The full transcripts of both sessions are attached as appendices. A short summary is in the next section.

- **Appendix A: full transcript of Session 1** (Claude Opus 5.5, 9–10 Nov). *[Attach the chat export here before submitting.]*
- **Appendix B: full transcript of Session 2** (Claude Sonnet 5.5, 10 Nov). *[Attach the chat export here before submitting.]*
- **Appendix C: full transcript of Session 3** (10 Nov). *[Attach the chat export here before submitting.]*
- **Appendix D: the Gemini query and its complete answer** (10 Nov). *[Paste the exact question you asked Gemini and its full reply here.]*

For Session 2 these were the two requests we sent, word for word:

> **Request 1:** "role: you are the best project reviewer in the world / context: my team and i are participating in this competition called scudem. i am attaching the document regarding the competition and are entire project on it / task: give feedback and rating / constraints: be thorough"

> **Request 2:** "role: you are the best mathematician in the world / context: attached above is the codebase, unlocked, instead of giving it to you in zip format. attached before it are all the md files. / my friend said for me to do this which im giving you: [[ we have to do some changes and specially on the ai generated formats and wordings make it humanize not fully just go through and whereever u feel like ai edit it video materials- slides, script, code, report and the AI Use Report. ]] / task: execute the necessary changes / constraints: be amazing, use human and and natural language, be thorough"

Request 1 produced a long written review with ratings. Request 2 produced the changed files described below. *(Typos are ours and left as sent.)*

For Session 3 these were the two requests, word for word (each came with the project zip or a text attachment):

> **Request 1:** "role: you are the best mathematician in the world / context: for scudem competition which my team and me are participating. this is our project / i have installed gnu octave ,as i dont have matlab / task: give feedback and rating / constraints: be amazing, be thorough"

> **Request 2:** "role: you are the best mathematical project creator in the world / context: improve robustness of the headline answer , validate against rela data / fit to a differential equation contest, and make it submission ready. / im guessing you already know how to improve it in a lot of ways, do that. / also ,this is what gemini said ,maybe it might help you: [Gemini's answer, attached as a text file; see Appendix D] / task: make the necessary improvements and changes / constraints: be amazing, be thorough / output: make it submission ready in all way"

Request 1 produced a written review (7.5/10), a figure on two hidden assumptions behind the closure age (script 12, figure 15) and an Octave run of the MATLAB cross-check. Request 2 produced the changes listed under "What Session 3 changed". Claude's reading of the Gemini answer was that it gave praise and a rating but no specific findings, so nothing from it was used.

## Log of requests, Session 1 (paraphrased)

These are summaries. The exact wording is in Appendix A.

| # | Request | What came back |
| --- | --- | --- |
| 1 | Read our coach's emails and the rules; help us start Problem A with little time left | Deadline check, rule summary, lessons from past winners |
| 2 | Given the Problem A statement, build the model, analysis and Python and MATLAB code | A first model (growth ODE, two-link arm, socket pressure, lifetime), code and figures |
| 3 | Go deeper, re-verify, organise the project, show the research behind it | Official CDC data; Model 0 with scaling laws; tapered-socket mechanism; centile children; Monte Carlo; 19 unit tests; MATLAB cross-check; LaTeX report |
| 4 | Package it with a README and a video storyboard | Project zip, README, data notes, storyboard |
| 5 | Rate the work; make explanation notes, a script and slides | Ratings (8/10 model, 8/10 report); explanation notes; script; 20-slide deck; four diagrams |
| 6 | Continue | The first version of this report |

During request 3 the AI corrected two of its own mistakes: a free-body diagram with the pressure directions reversed, and a misreading of why Monte Carlo samples failed.

## What Session 2 changed

Session 2 was a review and a clean-up. It was not a rebuild. No model equation and no baseline parameter value was changed. The AI re-ran the whole pipeline from scratch and every earlier result came out identical, and all 19 tests pass.

**What it found in the earlier AI-written work, and fixed:**

- The report said our two socket lifetimes "bracket the 12–18-month replacement intervals commonly reported for children". We had no source for that range, and our own numbers did not actually bracket it (at age 8 the boy's two sockets last 21.6 and 16.7 months). The claim was removed, and the report now says the lifetimes are not calibrated against clinic data.
- The window-closure age (13.9 y for boys, 14.6 y for girls) was presented as a firm answer. It is not. It changes by several years if the object load, the pressure tolerance, or the residual-limb growth rule is changed slightly. The report now says so, with a new analysis and figure (script 11, figure 14).
- Our baseline gives every new socket a residual limb that is 45 % of the forearm at any age. That does not match the limb-growth rule we use after fitting. This is now disclosed, and its effect on the closure age is measured.
- The report explained the 0.64 intercept of the dynamic-pressure line with a physical reason that turned out to be wrong. Slow curls actually give a ratio of exactly 1. The line is only a fit and misses that flat start. The explanation, the figure and the video script were corrected.
- "Closure comes 2–2.5 years earlier for large children" was wrong for girls (it is about 3). "Just after the growth spurt" is only true for boys. "Every claim in the table is an automated test" was wrong: one row (pistoning) is a script, not a test.
- The Monte Carlo summary did not say that 14.5 % of samples were already "closed" at the youngest age tested and 33 % never closed by 18. The full breakdown is now in the report.

**What it rewrote:** comments in the code, the config file, the README, the video storyboard, the report text, the slide text, the video script, the explanation notes and this report. The aim was plain, human wording, and nothing that hides the fact that AI did the work.

**Video script.** The script was rewritten to sound more like speech, and it gained one slide on how firm the closure age is. It is now 21 slides and about 1,215 spoken words, which is roughly 9:25 at a relaxed 135 words a minute with a short breath between slides. That is only an estimate. We time it ourselves with a stopwatch before recording, and the hard limit is 10:00.

**Things the AI could not do.** It could not run MATLAB, so the MATLAB cross-check against the Python results has to be run by us. It could not edit the PowerPoint file, so the slide text came back as markdown and the pictures have to be swapped in by hand.

## What Session 3 changed

No baseline parameter and no earlier result was changed; every number from sessions 1 and 2 is still produced by the same scripts. What was added:

- **A tolerance-free result** (script 13, figure 16). The peak-pressure path of a frozen socket does not depend on the assumed 100 kPa, so the paper now reports how long it takes pressure to rise by 10, 25 or 50 % (for +25 %: 11–26 months across ages 6–12, both sexes and both sockets), and reads the lifetime for any tolerance off that path. Checked against the original lifetime search to 0.002 months.
- **Model 2 as differential equations** (new module `src/pedsocket/slow_ode.py`, script 15, figure 18). Limb length, girth, tissue strain and fit pressure as ODEs forced by the peak arm load, with socket failure found as a solver event. It reproduces the earlier algebraic model (relative 6×10⁻⁸) and lifetimes (0.001 months, 28 cases). It also gave a conserved quantity and a closed-form "girth budget".
- **Closure as a probability** (script 14, figure 17). 600 random scenarios, adding object share and movement-time scaling, under two readings of residual-limb growth: closure before 18 in 58–88 %, median 14.3 or 9.9 years.
- **Comparison with published data** (script 16, figure 19, new paper Section 11): clinic replacement intervals (Ghidini et al. 2025, lower-limb), children's pressure-pain thresholds (Nikolajsen et al. 2011), adult socket pressures (Razak et al. 2014), arm and wrist circumference growth (Öztürk et al. 2009, 2017), growth-plate shares (Pritchett 1991). The paper says plainly which comparisons tune a parameter, which data are lower-limb, and where the model is off (girth growth a little high, φ above the literature range, growth ODE not predictive out of sample).
- **Corrections:** the growth-plate share was "75–80 %" and is now "about 80 % (radius) and 85 % (ulna)" as in Pritchett; the statement "not calibrated against clinic records" was replaced by the comparison above.
- **Tests:** 12 new tests (31 in all).
- **Documents:** paper (abstract, two new sections, new figures, discussion), README, video script (slides 3, 11, 12, 14, 17, 19, 20; now about 9:43), slides text, storyboard, explanation notes, this report.

**What we must check ourselves before submitting:** each new reference against the original (some were read only as abstracts or search snippets: the arm-circumference values, the "up to 60 % a year" volume figure from a conference poster, and the adult socket pressure); the new numbers in the video against the paper.

## Other AI features (fill in and confirm)

The policy also covers AI features in other tools. Please tick or fill in each line.

| Kind of use | Status |
| --- | --- |
| Voice synthesis (AI-generated voice) | ☐ Not used  ☐ Used: tool, version, purpose, timestamps: ______ |
| Text-to-video or image generation | ☐ Not used  ☐ Used: exact prompt, timestamps; label "AI-generated animation" on screen: ______ |
| AI features in editing software (auto-captions, speech enhancement, noise removal, etc.) | ☐ Not used  ☐ Used: tool, version, purpose, where in the video: ______ |

For reference: the result figures are drawn by Python scripts (matplotlib), the two animated GIFs by `scripts/10_animation.py`, and the four explanation diagrams by LaTeX/TikZ code (`diagrams/d1` to `d4`). The AI wrote all of that code. None of it came from a text-to-video or image-generation tool, so the second row is "not used" unless we add something else.

## Verification before signing

COMAP expects us to check AI output and check citations. Tick each item only once it is actually done.

- ☐ Ran `python -m pytest` on our own machine: all 31 tests pass
- ☐ Ran `python scripts/run_all.py`: the figures and numbers match the slides, and slides 10, 12, 13 and 14 use the new pictures (fig05, fig16, fig09, fig17)
- ☐ Ran `matlab/crosscheck.m` (in Octave) and the MATLAB and Python numbers agree
- ☐ Read the final paper PDF from start to finish and checked its numbers against the figures and slides
- ☐ Each of us can explain Model 0's free-body diagram and the window-closure result, including why the age is not firm, without notes
- ☐ Checked every reference in `paper/references.bib` against the original paper, book or report, and fixed or removed any that are wrong
- ☐ Confirmed the CDC data source on the official CDC growth-charts page
- ☐ Checked that no text was copied from a source without citation
- ☐ The slides and video say which numbers rest on assumed tissue parameters
- ☐ Exported the full chat transcripts and attached them as Appendices A, B and C, and pasted the Gemini query and answer as Appendix D
- ☐ Filled in the "Other AI features" table above
- ☐ Saved this report as a PDF titled "Report on Use of AI Tools" and attached it to the submission form

## Team statement

We used Claude (Opus 5.5, Sonnet 5.5 and, in session 3, Fable 5.2) and Google Gemini as described above. We have reviewed the model, code and results, checked the references, and take full responsibility for the content of our submission.

| Team member | Institution | Signature | Date |
| --- | --- | --- | --- |
| Betgeri Aditya Nikhil | BITS Pilani, Dubai Campus, Dubai, UAE | | |
| Sujal Patial | BITS Pilani, Dubai Campus, Dubai, UAE | | |
| Rakshit Maheshwari | BITS Pilani, Dubai Campus, Dubai, UAE | | |
