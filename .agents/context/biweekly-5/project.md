# Biweekly 5 Working Context

**Status:** Preliminary package executed and verified locally
**Reporting deadline:** 30 July 2026
**Scope:** AI context for the Biweekly 5 milestone

## Relationship to Repository Context

- `.agents/context/project.md` describes the verified repository-wide state.
- This file narrows that context to Biweekly 5.
- Earlier PDFs in `biweekly-2/` and `biweekly-4/` are continuity and formatting references, not factual authority for the new design.

## Intended Milestone

Prepare an evidence-based 3D casing concept that can connect to the HTI-02-DHPC/D mechanical interface shown in `HTI-02-DHPC_D MECH OUTLINE_.pdf`, then document the actual progress in a separate Indonesian Markdown report for transfer to Google Docs.

## Current State

- The supplier mechanical outline is present and is the controlling local reference for the interface.
- The previous generated hydrophone envelope, threaded adapter, and assembly code were removed because their dimensions contradicted the drawing and their solids overlapped.
- `results/biweekly-5/` contains the Indonesian Markdown report, final presentation/analysis STEP files, figures, tabular results, run inputs, and solver summaries.
- The reference design uses a nominal 7/16-20 UNF-2A male adapter, a separate pressure-seal area, three provisional conductors, and axial electronics envelopes.
- A 41 mm clear internal diameter is required by the provisional PCM1808 envelope and 1.5 mm clearance. The 43 mm and 50 mm OD candidates fail the resulting fit screen.
- The 60 mm OD reference uses 5.25 mm Inconel 718, 2.25 mm sealed aerogel, and 2 mm PEEK. It passes the preliminary analytical yield and elastic-buckling factors.
- Three CalculiX structural meshes converged to 433.37 MPa maximum nodal von Mises stress and 0.0714 mm displacement; medium-to-fine stress change is 2.76%.
- The corrected one-hour thermal study fails: 153.41 C at 1 W in the radial model and 149.62 C at zero internal power in the 3D CalculiX comparison.
- The thermal workflow previously divided conductivity by 1,000. That unit error was fixed; the old near-25 C result is invalid and must not be cited.

## Execution Guardrails

- Treat the generated report as preliminary engineering, not manufacturing approval or certification.
- Do not describe removed Antigravity outputs as progress or evidence.
- Distinguish drawing dimensions, user requirements, derived calculations, modeling assumptions, and verified CAD results.
- Do not claim pressure integrity, sealing performance, structural strength, manufacturability, or certification without corresponding evidence.
- Preserve the prior reports and supplier drawing unchanged.
- Prefer a concise milestone report unless the user requests the full long-form structure used previously.

## Decisions Needed Before Manufacturing-Grade Design

1. Obtain the supplier-controlled HTI drawing, pinout, preamplifier mode, cable, and endcap configuration.
2. Measure the purchased boards and confirm maximum tool OD/length.
3. Select exact Inconel heat treatment, aerogel/PEEK grades, seal system, and well-fluid/sour-service requirements.
4. Replace the failed solid-aerogel thermal concept with a vacuum-flask or verified thermal-mass architecture.

## Package Acceptance Criteria

- Future agents load this file only when working on Biweekly 5.
- Reproduce results with `.\.venv\Scripts\python.exe -m cosmo.biweekly5` before changing reported values.
- Preserve the explicit distinction between reference dimensions, assumptions, calculations, and solver results.
