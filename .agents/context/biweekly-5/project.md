# Biweekly 5 Working Context

**Status:** Preparation only - report execution has not been authorized
**Reporting deadline:** 30 July 2026
**Scope:** AI context for the Biweekly 5 milestone

## Relationship to Repository Context

- `.agents/context/project.md` describes the verified repository-wide state.
- This file narrows that context to Biweekly 5.
- Earlier PDFs in `biweekly-2/` and `biweekly-4/` are continuity and formatting references, not factual authority for the new design.

## Intended Milestone

Prepare an evidence-based 3D casing concept that can connect to the HTI-02-DHPC/D mechanical interface shown in `HTI-02-DHPC_D MECH OUTLINE_.pdf`, then document the actual progress in a separate Indonesian Markdown report for transfer to Google Docs.

## Current State After Repository Cleanup

- The supplier mechanical outline is present and is the controlling local reference for the interface.
- The previous generated hydrophone envelope, threaded adapter, and assembly code were removed because their dimensions contradicted the drawing and their solids overlapped.
- No dimensionally validated casing-to-hydrophone design currently exists.
- The surviving thermal CAD-CAE workflow models only concentric casing layers; it does not model or validate the hydrophone interface.

## Execution Guardrails

- Do not generate the collaborator-facing Biweekly 5 report until the user explicitly authorizes report execution.
- Do not describe removed Antigravity outputs as progress or evidence.
- Distinguish drawing dimensions, user requirements, derived calculations, modeling assumptions, and verified CAD results.
- Do not claim pressure integrity, sealing performance, structural strength, manufacturability, or certification without corresponding evidence.
- Preserve the prior reports and supplier drawing unchanged.
- Prefer a concise milestone report unless the user requests the full long-form structure used previously.

## Decisions Needed Before Design and Report Execution

1. Confirm which parts of the supplier drawing form the casing connection boundary.
2. Confirm maximum tool OD, available casing length, internal component envelope, target pressure, and target temperature.
3. Decide whether Biweekly 5 should cover only CAD interface progress or also include new thermal analysis.
4. Agree on the next two-week work plan and any progress percentage required by the formal report.

## Preparation Acceptance Criteria

- Future agents load this file only when working on Biweekly 5.
- No removed or unverified design is presented as completed work.
- No collaborator-facing report is created before explicit authorization.
