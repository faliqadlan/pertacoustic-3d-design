# Biweekly 5 Working Context

**Status:** Preliminary package executed; closed 3D validation status is FAIL
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
- The smallest radial-screen candidate is 146 mm OD: 12.5 mm Inconel 718, 38 mm sealed aerogel, 2 mm PEEK, 41 mm clear ID, and 255 mm housing length.
- The closed 3D one-hour/1 W thermal model includes both endcaps and available axial aerogel buffers. The 140.434 C maximum occurs on the cavity boundary in the analog front-end zone beside the 6 mm front buffer; the PCM1808 and STM32F411 zone boundaries reach 92.02 C and 71.77 C. Boards are not modeled as solids, so these are screening boundary temperatures rather than chip junction temperatures. Radial aerogel cools the middle of the housing, but the short axial paths still fail the electronics limits.
- The closed-vessel structural FEA applies 10,000 psi to the barrel and both endcaps. The fine result is 778.05 MPa, 3.297 mm displacement, and buckling factor 0.881; all fail acceptance and medium-to-fine changes remain above 5%.
- The detailed CAD now includes a rear pressure endcap and front/rear axial aerogel buffers. Seal grooves, contacts, thread tolerances, and pressure retention remain conceptual.
- Gmsh fragment-to-material mapping and solver success detection now fail closed; stale FRD files and CalculiX fatal text cannot be reported as successful reruns.
- The thermal workflow previously divided conductivity by 1,000. That unit error was fixed; the old near-25 C result is invalid and must not be cited.
- The user excluded vacuum insulation and added thermal-mass blocks because the tool must be made with conventional CNC and assembly capability at the UGM Geophysics Laboratory.

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
4. Redesign the end closures and axial thermal path before seeking a passing OD; increasing radial aerogel alone is not sufficient.

## Package Acceptance Criteria

- Future agents load this file only when working on Biweekly 5.
- Reproduce results with `.\.venv\Scripts\python.exe -m cosmo.biweekly5` before changing reported values.
- Preserve the explicit distinction between reference dimensions, assumptions, calculations, and solver results.
