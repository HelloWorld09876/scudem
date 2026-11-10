# Team 26126 · Report on Use of AI Tools

Nov 10, 2026 · @Sujal


## Overview & Team Collaboration

Our team designed, evaluated, and directed the entire mathematical modeling framework for Problem A. To execute our strategy effectively within the competition timeframe, we partnered with AI tools as technical assistants for heavy computational implementation, drafting script materials, LaTeX typesetting, and generating initial script skeletons. 

We used AI extensively as an interactive workbench: our team set the physical boundaries, chose the governing assumptions, verified every mathematical step, and ran all numerical validation on our own machines. Claude (Anthropic) served as our primary code execution and drafting tool, while Google Gemini was consulted once for an independent perspective.

We conducted three core working sessions with Claude alongside a targeted review query with Gemini:

| | Session 1 | Session 2 | Session 3 | Gemini |
| --- | --- | --- | --- | --- |
| **Tool and model** | Claude Opus 5.5 (Anthropic), inside the claude.ai environment with code execution capabilities | Claude Sonnet 5.5 (`claude-sonnet-5-5`), in claude.ai workspace with dedicated file environment | Claude (Anthropic) in claude.ai workspace; models switched dynamically during deep analysis (Sonnet 5.5, Fable 5.2, Opus 5.5) | Google Gemini 1.5 Pro |
| **Dates** | 9–10 November 2026 | 10 November 2026 | 10 November 2026 | 10 November 2026 |
| **Collaborative Focus** | **Team:** Defined modeling scope, equations, parameter constraints, and project layout.<br>**AI:** Generated initial Python/MATLAB scripts, draft LaTeX text, baseline plots, script outlines, and initial slide layouts. | **Team:** Critiqued model assumptions, identified ungrounded claims, and requested sanity checks.<br>**AI:** Executed code cleanup, refined tone, updated parameter notes, and verified test suites. | **Team:** Directed advanced robustness checks (tolerance-free analysis, ODE formulation, clinical comparisons).<br>**AI:** Implemented ODE scripts, performed numerical checks, expanded test coverage to 31 tests, and drafted updated paper sections. | **Team:** Prompted for a high-level secondary critique.<br>**AI:** Provided general feedback (not incorporated into final submission). |

**Data.** CDC 2000 growth reference tables (LMS parameters) were retrieved from an open-source mirror of official CDC records. All dataset sources were manually verified by the team; no data was synthetic or AI-fabricated.

## Division of Responsibility

| Project Stage | Team Contribution (Human Oversight & Intuition) | AI Contribution (Computational & Drafting Execution) |
| --- | --- | --- |
| **Problem Choice & Scope** | Evaluated challenge prompts, analyzed past winning frameworks, and chose Problem A based on mechanical interest. | Summarized rule constraints and synthesized strategy points from team notes. |
| **Model Conceptualization** | Designed the multi-stage model hierarchy (growth ODE, static socket mechanics, two-link arm, growth coupling). Prompted AI for structural revisions when initial ideas lacked physical backing. | Proposed mathematical representations, expanded differential notation, and structured initial variable systems. |
| **Data Acquisition & Audit** | Cross-referenced CDC growth parameters against official CDC published tables to ensure dimensional consistency. | Parsed LMS parameters from the public mirror into structured lookup tables. |
| **Software & Simulation** | Directed code architecture, debugged numerical errors, validated units, and executed all scripts/tests on local hardware. | Automated writing of modular Python modules, pytest suites, and independent MATLAB/Octave cross-check scripts. |
| **Data Analysis & Critique** | Analyzed physical validity of output curves, identified flawed assumptions (e.g., replacement window bracket claims), and set parameter ranges. | Ran sweeps, generated Monte Carlo simulations, performed sensitivity scripts, and rendered Matplotlib figures. |
| **Documentation & Paper** | Wrote core physical explanations, checked every reference against primary literature, and edited draft language for scientific clarity. | Transcribed model derivations into LaTeX, generated bibliography files, and drafted initial section templates. |
| **Video & Presentation** | Refined presentation structure, edited video scripts to reflect human speech patterns, designed final slides, and recorded voiceover/presentation. | Provided narrative storyboard concepts, initial slide text drafts, and timing estimates. |

## Query Log & Iterative Guidance

COMAP guidelines require documentation of AI queries and transcript references. Full chat exports are attached as appendices.

- **Appendix A: Full transcript of Session 1** (Claude Opus 5.5, 9–10 Nov)
- **Appendix B: Full transcript of Session 2** (Claude Sonnet 5.5, 10 Nov)
- **Appendix C: Full transcript of Session 3** (Claude dynamic models, 10 Nov)
- **Appendix D: Gemini query transcript** (10 Nov)

### Primary Prompts & Team Direction Summary

1. **Session 1 (Model Construction & Base Code):**
   * *Team Direction:* We tasked the AI with translating our physical framework (growth ODEs, socket pressure dynamics, dynamic arm loading) into a structured Python package with unit tests and Matplotlib plots.
   * *Self-Correction during Session:* During review, we caught an inverted pressure vector in an AI-generated free-body diagram. We directed the AI to flip the normal vectors to match physical reality.

2. **Session 2 (Critical Audit & Refinement):**
   * *Team Prompt:* Guided the AI to act as a rigorous peer reviewer, requesting an audit of our project files to find ungrounded claims or weak assumptions.
   * *Key Human-Led Corrections:*
     * *Unbacked Literature Claims:* The AI originally stated socket lifetimes "bracket the 12–18 month clinical replacement intervals." We caught that our mathematical model predicted 16.7–21.6 months for an 8-year-old boy. We removed the ungrounded claim and explicitly noted in the paper that our model is not clinically calibrated.
     * *Closure Age Sensitivity:* We noted the window-closure age (13.9y boys, 14.6y girls) was overly sensitive to assumptions. We directed the AI to build a dedicated sensitivity script (`script 11`, `fig 14`) showing how closure varies under load and growth changes.
     * *Physical Origin of Low-Speed Intercept:* We disproved an incorrect AI explanation regarding a 0.64 dynamic-pressure intercept, directing the model to correct the script and paper text to show it as a curve-fit artifact rather than a physical boundary.

3. **Session 3 (Advanced Robustness & Empirical Validation):**
   * *Team Prompt:* Directed the AI to refactor Model 2 into explicit differential equations with solver events, add a tolerance-free lifetime analysis, build a probabilistic closure model, and pull published clinical metrics for empirical comparison.
   * *Outcomes:*
     * Formulated `src/pedsocket/slow_ode.py` to mirror algebraic outputs within $6 \times 10^{-8}$ relative error.
     * Ran 600-sample probabilistic growth closure simulations.
     * Benchmarked model parameters against published literature (Ghidini et al. 2025, Nikolajsen et al. 2011, Razak et al. 2014, Öztürk et al. 2009/2017, Pritchett 1991).

## Technical Verification & Manual Checks

To ensure total accuracy, our team independently performed the following manual verification steps before submission:

| Verification Action | Method / Status |
| --- | --- |
| **Unit Test Execution** | Executed `python -m pytest` locally; all 31 tests passed. |
| **Script & Figure Verification** | Executed `python scripts/run_all.py`; verified all output numbers align with paper figures and slides. |
| **Octave / MATLAB Verification** | Ran `matlab/crosscheck.m` inside GNU Octave; confirmed numerical outputs match Python results. |
| **Literature Audit** | Manually reviewed papers in `paper/references.bib` against primary sources (Pritchett 1991, Nikolajsen 2011, etc.) to confirm correct citation of values. |
| **CDC Data Audit** | Cross-checked CDC LMS parameter tables against official CDC growth charts. |
| **Concept Mastery** | Confirmed all team members can independently present and explain Model 0 mechanics, free-body diagrams, and closure age sensitivities without notes. |

## Additional AI Tool Usage

| Category | Usage Status | Details |
| --- | --- | --- |
| **Voice Synthesis** | **Not Used** | All video audio recorded by team members. |
| **Text-to-Video / Image Generators** | **Not Used** | Figures rendered via Python Matplotlib (`scripts/10_animation.py`) and LaTeX TikZ (`diagrams/d1`–`d4`). |
| **Editing / Cleanup Tools** | **Not Used** | Standard noise suppression/editing within standard video recording software only. |

## Team Declaration & Signatures

We affirm that we actively directed, tested, verified, and edited all work presented in this submission. While AI tools provided significant drafting and implementation assistance, our team takes full responsibility for the mathematical formulations, physical interpretations, and final conclusions.

| Team Member | Institution | Signature | Date |
| --- | --- | --- | --- |
| Betgeri Aditya Nikhil | BITS Pilani, Dubai Campus, Dubai, UAE | | |
| Sujal Patial | BITS Pilani, Dubai Campus, Dubai, UAE | | |
| Rakshit Maheshwari | BITS Pilani, Dubai Campus, Dubai, UAE | | |