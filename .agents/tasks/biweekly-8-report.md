---
title: PertAcoustic Biweekly 8 Reporting Contract
document_id: AGENT-TASK-BIWEEKLY-8-REPORT
version: 1.0
status: Validated/Published
language: en-US
last_updated: 2026-09-10
scope:
  - PertAcoustic Biweekly 8 report generation
  - accepted compact-casing evidence synthesis
  - reporting traceability and evidence labeling
  - reporting-only artifact production
authority_note: This task authorizes a reporting and traceability deliverable only. It does not redefine, broaden, amend, supersede, or retroactively reinterpret the compact-casing engineering contract or accepted engineering evidence.
---

# Executable Task

This file defines the bounded delivery contract for generating the PertAcoustic Biweekly 8 report in a later Executor run.

The report is a communication and traceability artifact derived from accepted repository evidence. It is not the engineering source of truth.

## Task identity

**Task title:**  
PertAcoustic Biweekly 8 Evidence-Based Progress Report

**Task path:**  
`.agents/tasks/biweekly-8-report.md`

**Task contract state:**  
Validated/Published

The task file is the executable delivery contract.

Execution and review lifecycle states such as `In Execution`, `Review Required`, `Remediation Required`, and `Accepted` SHOULD normally be tracked by orchestration, review records, repository metadata, or another mechanism that preserves the exact governing task revision.

A lifecycle-status update MUST NOT silently replace the immutable task revision that governed an execution attempt.

When remediation materially changes this executable contract, edit this same stable task path, return it to Draft as needed, and republish it as a new immutable governing task revision before renewed execution.

**Delivery objective / Work Package / MVP:**  
PertAcoustic reporting work package: Biweekly 8 accepted-evidence report

**Owner / designated planning authority:**  
PertAcoustic Research Collaboration / Planner-Reviewer reporting authority

## Delivery context

Biweekly 8 must summarize accepted PertAcoustic engineering progress at the current reporting cutoff:

```text
main@667ccd59cf6657a75dfe3cc2b4c67488737ef028
```

The principal engineering work being reported is governed by:

```text
.agents/tasks/compact-downhole-casing-redesign.md @ ad24d9146815f88368d8f6b1d635831d57aed13d
```

That engineering task recorded implementation baseline:

```text
b33e1622b04ec5e723c634573dbfa93aaa065576
```

The future report must explain, with traceable evidence:

1. what the engineering state was before the compact-casing redesign;
2. what engineering work was completed;
3. what evidence was produced;
4. what changed from the previous accepted baseline;
5. what the current preliminary engineering configuration is;
6. which results are VERIFIED, DERIVED SCREENING, ASSUMED SCREENING, HISTORICAL, PROVISIONAL, or UNRESOLVED;
7. what remains unresolved; and
8. what engineering work should happen next.

The report must be suitable for PertAcoustic project members, academic supervisors, engineering collaborators, and project decision-makers. Technical clarity and traceability are more important than presentation decoration.

The repository/project evidence inspected for task publication does not establish a reliable Biweekly 6 / Biweekly 7 reporting-period chain. The future report MUST NOT invent reporting-period dates or a Biweekly 7 repository artifact. If authoritative dates remain unavailable, record the dates as unresolved and make the evidence cutoff explicit.

## Baseline and task revision

**Implementation baseline:**  
`667ccd59cf6657a75dfe3cc2b4c67488737ef028`

**Task revision:**  
Resolved by the immutable Git commit that publishes this task file. The preferred identity is:

```text
.agents/tasks/biweekly-8-report.md @ <full Git commit SHA containing this task content>
```

The task body does not need to embed the commit SHA that contains itself. The Executor MUST use the exact immutable task revision supplied by the Planner/Reviewer handoff or Git history before starting report generation.

The implementation baseline and governing task revision are separate references.

Do not change the implementation baseline silently during execution. If `origin/main` or the accepted reporting cutoff has moved, stop and return to Planner/Reviewer for reporting-cutoff review before generating Biweekly 8.

## Objective

Create a coherent, evidence-based PertAcoustic Biweekly 8 report from accepted repository evidence, preserving engineering semantics and uncertainty labels while producing only reporting artifacts under `results/biweekly-8/`.

The report MUST synthesize accepted engineering evidence without making new engineering design decisions, changing source-of-truth engineering artifacts, or overstating preliminary screening as qualification.

## Authoritative inputs

### Governing authority

- Repository delivery governance:
  - `AGENTS.md`
  - `.agents/AGENTS.md`
  - `.agents/software-workflow.md`
  - `.agents/context/project.md`
- This reporting task:
  - `.agents/tasks/biweekly-8-report.md @ <published immutable task revision>`
- Governing compact-casing engineering task:
  - `.agents/tasks/compact-downhole-casing-redesign.md @ ad24d9146815f88368d8f6b1d635831d57aed13d`
- Accepted reporting cutoff:
  - `main@667ccd59cf6657a75dfe3cc2b4c67488737ef028`

### Primary repository evidence

Prioritize evidence in this order:

1. Current accepted repository implementation and generated results at the reporting cutoff.
2. The exact governing engineering task revision.
3. Actual executed test, simulation, CAD, and generated evidence.
4. Formal project decisions represented in repository authority/context.
5. Manufacturer, supplier, standard, or paper evidence already properly traced by the accepted engineering work.
6. Engineering measurements.
7. Historical Biweekly reports.
8. Informal discussion or context only when appropriately labeled.

Important evidence surfaces include:

- `results/compact-casing/compact_casing_redesign_report.md`
- `results/compact-casing/compact_casing_id_od_envelope.csv`
- `results/compact-casing/compact_casing_trade_study.csv`
- `results/compact-casing/figures/`
- `cosmo/compact_casing.py`
- `tests/test_compact_casing.py`
- `results/biweekly-5/biweekly-5.md`
- `results/biweekly-5/figures/`
- `results/biweekly-5/cad/`
- `results/biweekly-5/summary.json`
- `results/biweekly-5/thermal_results.csv`
- `results/biweekly-5/structural_fea_results.csv`
- `results/biweekly-5/mesh_convergence.csv`
- `results/biweekly-5/input_spec.json`
- `.agents/context/biweekly-5/`

Historical Biweekly 5 artifacts must remain unchanged.

### Requirement traceability

- `REQ-RPT8-001` (Evidence-bound report) -> This task, repository governance, and reporting cutoff: Biweekly 8 must synthesize accepted evidence without inventing unsupported progress.
- `REQ-RPT8-002` (Current configuration reconciliation) -> Accepted compact-casing evidence: the report must reconcile preliminary dimensions, materials, architecture, and status labels against repository evidence before publication.
- `REQ-RPT8-003` (Strict thermal semantics) -> Accepted compact-casing evidence and task constraints: shell-coupled lower-bound thermal results must not be relabeled as electronics temperature.
- `REQ-RPT8-004` (Strict structural semantics) -> Accepted compact-casing evidence and unresolved pressure authority: structural screening must remain conditional and must not be presented as pressure qualification.
- `REQ-RPT8-005` (Historical preservation) -> Repository context and historical reporting evidence: Biweekly 5 artifacts must remain unchanged and historical facts must be labeled historical.
- `REQ-RPT8-006` (Traceable reporting package) -> Repository reporting convention: the report belongs under `results/biweekly-8/` with minimal supporting artifacts.

Do not use existing implementation as retroactive justification for missing authority.

## Scope

### In scope

- Synthesize accepted engineering evidence into a Biweekly 8 report.
- Produce reporting artifacts under:

```text
results/biweekly-8/
  biweekly-8.md
  figures/        if justified
  supporting generated evidence only when required
```

- Select relevant accepted engineering figures when useful.
- Create reporting-only explanatory tables or figures when justified by traceability and generated from accepted evidence.
- Create evidence and traceability tables where useful.
- Document unresolved engineering gaps.
- Document next engineering work.
- Verify report consistency, dimensions, units, claims, evidence links, and figure captions.

### Out of scope

- Creating `results/biweekly-8/` or `biweekly-8.md` before this task is executed in a future reporting slice.
- Changing the current engineering design.
- Choosing a different OD merely for reporting.
- Changing casing wall thickness.
- Changing material selection.
- Introducing a new carrier material.
- Modifying thermal physics.
- Changing structural models.
- Changing pressure assumptions.
- Changing HTI geometry.
- Inventing actual electronics dimensions.
- Inventing measured power dissipation.
- Fabricating prototype results.
- Claiming field qualification, pressure qualification, manufacturing readiness, or downhole qualification.
- Modifying, renaming, overwriting, or regenerating historical Biweekly 5 evidence.
- Modifying `cosmo/compact_casing.py`, compact-casing result artifacts, tests, or other engineering source-of-truth data to make the report easier to write.
- Inventing a new PDF-generation toolchain. Markdown is the minimum canonical report artifact unless later human direction requires another format.

### Preserved behavior

- Historical reporting directories remain unchanged, especially `results/biweekly-5/`.
- Compact-casing engineering source and accepted generated evidence remain unchanged.
- Repository governance and task contract semantics remain unchanged.
- Preliminary engineering results remain clearly preliminary.
- Assumptions, historical values, and unresolved items remain visible.

If report preparation exposes a genuine engineering inconsistency, record it as a reporting blocker or finding rather than silently fixing engineering source-of-truth data inside this reporting task.

## Current engineering baseline to preserve

Before publication, the future report MUST reconcile these current accepted preliminary values against repository evidence:

- Pressure shell: Inconel 718.
- Preferred casing OD: 44.45 mm / 1.75 in.
- Maximum screening OD: 57.15 mm / 2.25 in.
- Preliminary wall: 3.50 mm.
- Resulting shell bore: 37.45 mm.
- Project internal-diameter direction: ID > 30 mm.
- Critical interpretation: 30 mm is a lower bound, not the target internal diameter.
- Current electronics screening requirement: approximately 34.93 mm circular packaging envelope.
- Current preliminary diametral packaging margin: approximately 2.52 mm.
- Current architecture:
  - Inconel 718 metallic pressure shell.
  - Discrete/conformal polymer electronics carrier.
  - Electronics inside the carrier.
  - No aerogel baseline.
- Carrier hierarchy:
  - PA66-GF30: PRIMARY NYLON PROTOTYPE / VALIDATION CANDIDATE.
  - PEEK: ENGINEERING BENCHMARK / REFERENCE.
  - PPA: HIGHER-PERFORMANCE POLYAMIDE ALTERNATIVE / SECONDARY VALIDATION CANDIDATE.

The report MUST NOT call:

- PA66 downhole-qualified;
- the polymer carrier a pressure boundary;
- the current casing pressure-qualified;
- the current design manufacturing-ready;
- the design field-qualified.

## Reporting content requirements

The report MUST include, at minimum:

1. Executive Progress Summary.
2. Work Completed During the Reporting Period.
3. Current Engineering Configuration.
4. Engineering Analysis, covering where supported:
   - mechanical packaging;
   - ID/OD envelope;
   - material/carrier selection;
   - structural screening;
   - thermal screening;
   - electronics packaging;
   - HTI/acoustic interface.
5. Comparison With Previous Baseline, explicitly explaining the transition from the earlier large casing / aerogel-oriented concept toward the compact architecture.
6. Verification and Evidence, including exact repository revision and generated evidence used.
7. Current Engineering Decision.
8. Unresolved Items / Risks.
9. Next Engineering Work.
10. Evidence / Traceability Table where useful.

Assess and include these items only when supported by reporting-cutoff evidence:

- compact-casing redesign;
- 1.75 in / 44.45 mm OD recommendation;
- 3.50 mm preliminary Inconel wall;
- 37.45 mm bore;
- 30 mm ID as lower bound rather than target;
- current approximately 34.93 mm electronics screening requirement;
- approximately 2.52 mm packaging margin;
- removal of aerogel from the current baseline;
- PA66-GF30 first-prototype direction;
- PEEK benchmark/reference role;
- PPA secondary-candidate role;
- structural-screening results;
- unresolved authoritative pressure;
- current shell thermal-screening results;
- limitations of the present thermal model;
- actual electronics dimensional measurement requirement;
- actual electronics power requirement;
- planned PA66 physical validation;
- next thermal-development step;
- unresolved HTI supplier-controlled thread/seal/interface geometry.

Do not add unsupported engineering progress merely to make Biweekly 8 appear more substantial.

## Thermal semantics

The report MUST use strict thermal wording.

The current 70 C model may support discussion of:

- shell response;
- inner-shell temperature;
- shell-coupled lower-bound behavior;
- present thermal-screening limitations.

It MUST NOT be presented as directly establishing:

- PCB temperature;
- electronics cavity temperature;
- STM32 junction temperature;
- PCM1808 junction temperature;
- complete electronics temperature;
- electronics qualification.

The current result is:

```text
IDEAL SHELL-COUPLED LOWER-BOUND TEMPERATURE (INNER SHELL SURFACE)
```

Do not relabel it as "electronics temperature".

The report MUST explicitly state that stronger thermal work requires:

```text
environment
-> Inconel shell
-> shell/carrier contact
-> polymer carrier
-> PCB/contact
-> electronics heat sources
```

with measured or justified thermal resistances and actual electronics power.

## Structural semantics

Structural conclusions MUST remain:

```text
CONDITIONAL - DESIGN PRESSURE UNRESOLVED
```

Current pressure scenarios may be reported only according to their evidence status:

- `~10 MPa`: screening context.
- `20 MPa`: sensitivity case.
- `68.95 MPa / 10,000 psi`: historical comparison where applicable.

None of these establishes authoritative field design pressure.

A calculated screening factor of safety MUST NOT be presented as pressure qualification.

## Dependencies and assumptions

### Dependencies

- Local repository state at `667ccd59cf6657a75dfe3cc2b4c67488737ef028`.
- Published reporting task revision for this task.
- Accepted compact-casing engineering evidence at the reporting cutoff.
- Historical Biweekly 5 artifacts for comparison and provenance.

### Approved assumptions

- Markdown is the minimum canonical Biweekly 8 report artifact.
- `results/biweekly-8/biweekly-8.md` is the default report path.
- Figures are optional and must be justified by evidence and provenance.
- Reporting-period dates are unresolved unless authoritative repository/project evidence establishes them during execution.

### Remaining approval requirements

- Planner/Reviewer must inspect this exact task revision before report implementation is authorized.
- The future Executor must return the generated Biweekly 8 artifacts for review and must not self-accept the report.
- Any request to publish externally, push, open a PR, release, or deploy requires separate authorization.

## Required capabilities

- Repository read and write.
- Git state inspection.
- Local shell command execution for non-destructive verification.
- Markdown authoring.
- Ability to inspect CSV, Markdown, Python, generated figures, and repository history.
- Existing project test execution when proportionate to verifying preservation.

No new external service, plugin, PDF generator, or dependency is required for the minimum report.

## Execution constraints

### Constraints

- Use the reporting cutoff exactly; do not silently move to a newer revision.
- Do not generate engineering evidence or rerun simulations unless a specific report consistency check requires non-destructive verification and the generated output remains within this reporting task's scope.
- Do not duplicate compact-casing numerical artifacts merely to make `results/biweekly-8/` self-contained when traceable references are sufficient.
- If figures are reused from accepted current engineering evidence, preserve provenance.
- If a figure must be regenerated, regenerate from the canonical generator/source rather than manually modifying an image.
- Use established repository reporting conventions; do not create a new reporting framework.
- Keep claims tied to evidence status labels.
- Use concise technical language suitable for the stated audiences.

## Acceptance criteria

- [ ] `results/biweekly-8/biweekly-8.md` exists and presents one coherent engineering story from previous baseline to current preliminary compact architecture.
- [ ] The report records the exact repository revision/evidence cutoff: `667ccd59cf6657a75dfe3cc2b4c67488737ef028`.
- [ ] The report identifies the governing compact-casing task revision: `ad24d9146815f88368d8f6b1d635831d57aed13d`.
- [ ] Reporting-period dates are either supported by authoritative evidence or explicitly recorded as unresolved.
- [ ] Numbers match accepted engineering evidence; OD, ID, wall, bore, and packaging-margin dimensions are internally consistent and units are correct.
- [ ] Figures correspond to the described quantity, preserve provenance, and captions do not overclaim.
- [ ] Historical values are clearly historical.
- [ ] Preliminary results are clearly preliminary.
- [ ] Assumptions remain labeled.
- [ ] Unresolved issues remain visible.
- [ ] References support their associated statements.
- [ ] Structural screening is not presented as qualification.
- [ ] Shell temperature is not presented as electronics temperature.
- [ ] The report preserves historical Biweekly artifacts, especially `results/biweekly-5/`.
- [ ] The report does not modify compact-casing engineering source/results or create new engineering decisions.

## Verification requirements

### Required checks

- Verify Git state and confirm the implementation baseline/reporting cutoff used for report generation.
- Inspect `git diff --name-only` or equivalent and confirm changes are limited to authorized Biweekly 8 reporting artifacts.
- Check that `results/biweekly-5/` is unmodified.
- Check that compact-casing engineering source/results are unmodified unless Planner/Reviewer explicitly authorized a reporting-only exception.
- Review `biweekly-8.md` against accepted evidence for dimension, unit, classification, and semantic consistency.
- Run the smallest relevant existing test or repository check needed to demonstrate preservation if any executable source or generated engineering artifact is touched. If only Markdown/reporting artifacts are changed, record that no code tests were required and explain why.

### Required evidence

The Executor MUST report:

- exact implementation revision or precise working-tree state;
- task revision used;
- reporting cutoff used;
- files changed;
- commands/checks actually executed and observed results;
- evidence sources used;
- tests not run and rationale;
- known verification gaps;
- unresolved reporting or engineering items;
- confirmation that engineering implementation was not changed;
- confirmation that historical Biweekly artifacts were not modified.

Do not represent unobserved, skipped, or local-only checks as broader evidence than they actually provide.

## Stop conditions

The Executor MUST stop report implementation and return the issue to planning when any of the following materially affects the task:

- `origin/main` or the accepted reporting cutoff no longer matches `667ccd59cf6657a75dfe3cc2b4c67488737ef028` and no reviewed new cutoff has been supplied.
- The governing compact-casing task revision cannot be resolved.
- Accepted compact-casing evidence does not support the current preliminary values listed in this task.
- Report generation requires changing engineering authority, design source, simulation source, or accepted engineering results.
- The report would need to invent a product or engineering decision.
- Historical Biweekly evidence would need destructive modification.
- Reporting-period dates cannot be established and a stakeholder requires exact dates rather than unresolved chronology.
- An externally visible action becomes necessary.

Do not stop merely because reporting-period dates are unresolved, some report data are intentionally unresolved, or the final report requires review after generation. Represent those uncertainties accurately.

## Side-effect authorization

Implementation authorization is strictly bounded to the task's defined reporting scope.

Unless explicitly authorized by this task, applicable repository policy, or designated authority, the task does NOT authorize:

- engineering source changes;
- compact-casing result modification;
- historical Biweekly 5 modification;
- dependency installation or replacement;
- Git push;
- remote branch creation;
- pull request creation;
- deployment;
- external publication;
- release;
- destructive cleanup;
- force-push or history rewrite;
- external-system mutation.

### Explicitly authorized side effects

- Create `results/biweekly-8/`.
- Create `results/biweekly-8/biweekly-8.md`.
- Create `results/biweekly-8/figures/` only if justified by the report and provenance is preserved.
- Create minimal supporting generated reporting evidence under `results/biweekly-8/` only when required for traceability.
- Run non-destructive local verification.

Git commit authorization is not implied for the future reporting Executor unless separately supplied by the handoff for that execution slice.

## Expected terminal outcome

The Executor's implementation phase SHOULD end in **Review Required**:

- `results/biweekly-8/biweekly-8.md` exists.
- Any justified supporting reporting artifacts exist under `results/biweekly-8/`.
- Verification evidence is truthfully reported.
- Engineering implementation changed: NO.
- Historical Biweekly artifacts modified: NO.
- Biweekly 8 report generated: YES.

The Executor does not self-declare final acceptance.

## Review and remediation handling

The Reviewer evaluates report artifacts against the exact governing task revision, reporting cutoff, accepted engineering evidence, and observed verification evidence.

If review identifies bounded corrections within the same reporting objective, update and republish this same task file only if the executable contract itself must change. Ordinary report corrections should remain implementation remediation under this task.

Materially new engineering objectives, new design decisions, new simulations, new authority needs, or scope expansion MUST return to Delivery Planning and become separate task work.
