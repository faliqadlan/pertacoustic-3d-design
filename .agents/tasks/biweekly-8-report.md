---
title: PertAcoustic Biweekly 8 Reporting Contract
document_id: AGENT-TASK-BIWEEKLY-8-REPORT
version: 1.1
status: Validated/Published
language: en-US
last_updated: 2026-09-10
scope:
  - PertAcoustic Biweekly 8 report generation
  - accepted compact-casing evidence synthesis
  - reporting traceability and evidence labeling
  - native Google Docs human-facing deliverable
  - reporting-only repository source artifact maintenance
authority_note: This task authorizes a reporting and traceability deliverable only. It does not redefine, broaden, amend, supersede, or retroactively reinterpret the compact-casing engineering contract or accepted engineering evidence.
---

# Executable Task

This file defines the bounded delivery contract for remediating the PertAcoustic Biweekly 8 report in a later Executor run.

The report is a communication and traceability artifact derived from accepted repository evidence. The repository Markdown remains the traceability/source artifact; the primary human-facing deliverable is a native Google Doc. Neither artifact is the engineering source of truth.

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

The current report implementation requiring remediation is:

```text
29a602029cf55a0b036887d776440447325bd864
```

That implementation created the repository source artifact:

```text
results/biweekly-8/biweekly-8.md
```

The future remediated report must explain, with traceable evidence:

1. what the engineering state was before the compact-casing redesign;
2. what engineering work was completed;
3. what evidence was produced;
4. what changed from the previous accepted baseline;
5. what the current preliminary engineering configuration is;
6. which results are VERIFIED, DERIVED SCREENING, ASSUMED SCREENING, HISTORICAL, PROVISIONAL, or UNRESOLVED;
7. what remains unresolved; and
8. what engineering work should happen next.

The report must be suitable for PertAcoustic project members, academic supervisors, engineering collaborators, and project decision-makers. Technical clarity and traceability are more important than presentation decoration.

The primary human-facing deliverable MUST be a native Google Doc titled:

```text
3d-design-biweekly-8
```

The Google Doc MUST be created directly in the specified PertAcoustic Google Drive folder:

```text
https://drive.google.com/drive/folders/14V4rGX0lwHmwCNOGn8BQYE-0R6DH-Fy9
```

The existing Biweekly 5 Google Doc is a formatting and editorial template only:

```text
https://docs.google.com/document/d/1hAxKtHvkiHflduqY9msiPGFDHWHsi38WFNxwXvtDBFk/edit
```

The Biweekly 5 Google Doc and repository Biweekly 5 artifacts are historical engineering evidence. They MUST NOT be cited or treated as current engineering authority. If the Google Doc is copied as a native formatting template, copied historical content MUST be replaced or clearly relabeled as historical. Biweekly 5 may constrain only the visual/editorial form of the Biweekly 8 Google Doc.

The repository/project evidence inspected for task publication does not establish a reliable Biweekly 6 / Biweekly 7 reporting-period chain. The future report MUST NOT invent reporting-period dates or a Biweekly 7 repository artifact. If authoritative dates remain unavailable, record the dates as unresolved and make the evidence cutoff explicit.

## Baseline and task revision

**Implementation baseline:**  
`29a602029cf55a0b036887d776440447325bd864`

**Task revision:**  
Resolved by the immutable Git commit that publishes this task file. The preferred identity is:

```text
.agents/tasks/biweekly-8-report.md @ <full Git commit SHA containing this task content>
```

The task body does not need to embed the commit SHA that contains itself. The Executor MUST use the exact immutable task revision supplied by the Planner/Reviewer handoff or Git history before starting report generation.

The implementation baseline and governing task revision are separate references. The implementation baseline is the current report implementation requiring remediation. The accepted engineering reporting cutoff remains `667ccd59cf6657a75dfe3cc2b4c67488737ef028`.

Do not change the implementation baseline silently during execution. If `origin/main` or the accepted reporting cutoff has moved, stop and return to Planner/Reviewer for reporting-cutoff review before remediating Biweekly 8.

## Objective

Remediate the existing coherent, evidence-based PertAcoustic Biweekly 8 report from accepted repository evidence by keeping `results/biweekly-8/biweekly-8.md` as the repository traceability/source artifact and creating a native Google Docs primary human-facing deliverable in the specified PertAcoustic Drive folder.

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
- Previous governing reporting task revision:
  - `.agents/tasks/biweekly-8-report.md @ c1d8d7c00d6fe3b3055bdabebb604f4e49bb86cb`
- Current report implementation requiring remediation:
  - `29a602029cf55a0b036887d776440447325bd864`
- Biweekly 8 Google Doc target:
  - Title: `3d-design-biweekly-8`
  - Folder: `https://drive.google.com/drive/folders/14V4rGX0lwHmwCNOGn8BQYE-0R6DH-Fy9`
- Formatting/editorial template only:
  - Biweekly 5 Google Doc: `https://docs.google.com/document/d/1hAxKtHvkiHflduqY9msiPGFDHWHsi38WFNxwXvtDBFk/edit`

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
- `results/biweekly-8/biweekly-8.md`

Historical Biweekly 5 artifacts must remain unchanged.

The Biweekly 5 Google Doc and repository Biweekly 5 artifacts are HISTORICAL engineering evidence. They may be used for formatting/editorial style and previous-baseline comparison only. They MUST NOT be treated as current engineering authority.

### Requirement traceability

- `REQ-RPT8-001` (Evidence-bound report) -> This task, repository governance, and reporting cutoff: Biweekly 8 must synthesize accepted evidence without inventing unsupported progress.
- `REQ-RPT8-002` (Current configuration reconciliation) -> Accepted compact-casing evidence: the report must reconcile preliminary dimensions, materials, architecture, and status labels against repository evidence before publication.
- `REQ-RPT8-003` (Strict thermal semantics) -> Accepted compact-casing evidence and task constraints: shell-coupled lower-bound thermal results must not be relabeled as electronics temperature.
- `REQ-RPT8-004` (Strict structural semantics) -> Accepted compact-casing evidence and unresolved pressure authority: structural screening must remain conditional and must not be presented as pressure qualification.
- `REQ-RPT8-005` (Historical preservation) -> Repository context and historical reporting evidence: Biweekly 5 artifacts must remain unchanged and historical facts must be labeled historical.
- `REQ-RPT8-006` (Traceable reporting package) -> Repository reporting convention and human requirement change: `results/biweekly-8/biweekly-8.md` remains the repository traceability/source artifact, while the native Google Doc is the primary human-facing deliverable.
- `REQ-RPT8-007` (Native Google Docs deliverable) -> Human requirement change: Biweekly 8 must be created as a native Google Doc titled `3d-design-biweekly-8` directly in the specified PertAcoustic Google Drive folder.
- `REQ-RPT8-008` (Biweekly 5 style template boundary) -> Human requirement change: the Biweekly 8 Google Doc must closely match the visual/editorial structure of the Biweekly 5 Google Doc while treating Biweekly 5 only as historical evidence and formatting/editorial template material.

Do not use existing implementation as retroactive justification for missing authority.

## Scope

### In scope

- Synthesize accepted engineering evidence into a Biweekly 8 report.
- Preserve and, if needed, update the repository source artifact under:

```text
results/biweekly-8/
  biweekly-8.md
  figures/        if justified
  supporting generated evidence only when required
```

- Create a native Google Doc titled `3d-design-biweekly-8` directly in:

```text
https://drive.google.com/drive/folders/14V4rGX0lwHmwCNOGn8BQYE-0R6DH-Fy9
```

- Use the Biweekly 5 Google Doc only as a formatting/editorial template.
- Write the primary Google Doc in Indonesian.
- Match the Biweekly 5 Google Doc style closely enough to preserve report readability and audience expectations, including report-style title, period/date/status block, concise disclaimer, numbered engineering sections, explanatory prose, native Google Docs tables, inline engineering figures, figure captions, references section, typography, heading hierarchy, and page layout.
- Select relevant accepted engineering figures when useful.
- Create reporting-only explanatory tables or figures when justified by traceability and generated from accepted evidence.
- Create evidence and traceability tables where useful.
- Record the final Google Doc identity, URL, and folder placement in the Executor's evidence and, if appropriate, in `results/biweekly-8/biweekly-8.md` without turning the Google Doc into engineering authority.
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
- Modifying the Biweekly 5 Google Doc.
- Modifying `cosmo/compact_casing.py`, compact-casing result artifacts, tests, or other engineering source-of-truth data to make the report easier to write.
- Creating a PDF, slide deck, or alternative publication artifact unless separately authorized.
- Treating the Google Doc, Biweekly 5 Google Doc, or the Markdown report as engineering source-of-truth authority.

### Preserved behavior

- Historical reporting directories remain unchanged, especially `results/biweekly-5/`.
- The Biweekly 5 Google Doc remains unchanged.
- Compact-casing engineering source and accepted generated evidence remain unchanged.
- Repository governance and task contract semantics remain unchanged.
- `results/biweekly-8/biweekly-8.md` remains the repository traceability/source artifact.
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

The Google Doc MUST be written in Indonesian and use explanatory engineering prose rather than audit-oriented prose. It MUST include, at minimum:

1. Ringkasan Kemajuan.
2. Periode, status, dan batas bukti.
3. Pekerjaan yang selesai pada periode pelaporan.
4. Konfigurasi teknik saat ini.
5. Analisis teknik, covering these topics where supported:
   - mechanical packaging;
   - ID/OD envelope;
   - material/carrier selection;
   - structural screening;
   - thermal screening;
   - electronics packaging;
   - HTI/acoustic interface.
6. Perbandingan dengan baseline sebelumnya, explicitly explaining the transition from the earlier large casing / aerogel-oriented concept toward the compact architecture.
7. Verifikasi dan bukti, including the exact repository revision and generated evidence used.
8. Keputusan teknik saat ini.
9. Hal yang belum terselesaikan / risiko.
10. Pekerjaan teknik berikutnya.
11. Referensi.
12. Evidence / traceability table where useful.

The Google Doc MUST closely match the Biweekly 5 document's visual and editorial pattern:

- Indonesian language.
- Report-style title.
- Period/date/status block near the top.
- Concise disclaimer that the report is not a manufacturing drawing, pressure qualification, field qualification, or new engineering source of truth.
- Numbered engineering sections.
- Explanatory prose rather than audit-oriented prose.
- Native Google Docs tables, not pasted Markdown table text or screenshots of tables.
- Engineering figures embedded inline from accepted evidence when useful.
- Figure captions placed next to the corresponding figures.
- References section.
- Approximately the same typography, heading hierarchy, page layout, and overall readability as the Biweekly 5 Google Doc.

`results/biweekly-8/biweekly-8.md` MUST remain an English or repository-conventional traceability/source artifact unless the Executor has a clearly bounded reason to translate it. The Google Doc is the Indonesian human-facing deliverable.

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

- Local repository state at `29a602029cf55a0b036887d776440447325bd864`.
- Published reporting task revision for this task.
- Accepted compact-casing engineering evidence at the reporting cutoff.
- Historical Biweekly 5 artifacts for comparison and provenance.
- Read access to the Biweekly 5 Google Doc for formatting/editorial template inspection.
- Google Drive connector/API access sufficient to create or update one native Google Doc in the specified target folder.

### Approved assumptions

- `results/biweekly-8/biweekly-8.md` is the repository traceability/source artifact.
- The native Google Doc titled `3d-design-biweekly-8` is the primary human-facing deliverable.
- Figures are optional and must be justified by evidence and provenance.
- Reporting-period dates are unresolved unless authoritative repository/project evidence establishes them during execution.
- The Biweekly 5 Google Doc provides visual/editorial structure only; it is not current engineering authority.

### Remaining approval requirements

- Planner/Reviewer must inspect this exact task revision before report implementation is authorized.
- The future Executor must return the generated Biweekly 8 artifacts for review and must not self-accept the report.
- Authorization is granted only for creation or update of the Biweekly 8 Google Doc titled `3d-design-biweekly-8` in the specified PertAcoustic folder.
- Any request to modify Biweekly 5, publish outside the specified folder, push, open a PR, release, deploy, or perform other external publication requires separate authorization.

## Required capabilities

- Repository read and write.
- Git state inspection.
- Local shell command execution for non-destructive verification.
- Markdown authoring.
- Google Drive connector/API access for native Google Doc creation/update in the specified folder.
- Google Docs editing capability for native text, headings, page layout, tables, inline figures, captions, and references.
- Ability to inspect CSV, Markdown, Python, generated figures, and repository history.
- Existing project test execution when proportionate to verifying preservation.

No new PDF generator, slide toolchain, or local dependency is required. The Google Drive/Docs capability is required only for the authorized native Google Doc deliverable.

## Execution constraints

### Constraints

- Use the reporting cutoff exactly; do not silently move to a newer revision.
- Start remediation from the current report implementation baseline `29a602029cf55a0b036887d776440447325bd864` unless Planner/Reviewer supplies a newer remediation baseline.
- Do not generate engineering evidence or rerun simulations unless a specific report consistency check requires non-destructive verification and the generated output remains within this reporting task's scope.
- Do not duplicate compact-casing numerical artifacts merely to make `results/biweekly-8/` self-contained when traceable references are sufficient.
- If figures are reused from accepted current engineering evidence, preserve provenance.
- If a figure must be regenerated, regenerate from the canonical generator/source rather than manually modifying an image.
- Use established repository reporting conventions; do not create a new reporting framework.
- Use the Biweekly 5 Google Doc only to copy or reproduce visual/editorial structure for the Biweekly 8 Google Doc.
- If the Executor copies the Biweekly 5 Google Doc as a template, the copied document MUST be created as the new Biweekly 8 document titled `3d-design-biweekly-8` in the specified target folder, and all copied historical content MUST be replaced or relabeled so it cannot be mistaken for current Biweekly 8 engineering evidence.
- Do not mutate the Biweekly 5 Google Doc.
- Keep claims tied to evidence status labels.
- Use concise technical language suitable for the stated audiences.

## Acceptance criteria

- [ ] `results/biweekly-8/biweekly-8.md` exists and remains the repository traceability/source artifact for Biweekly 8.
- [ ] A native Google Doc titled `3d-design-biweekly-8` exists directly in the specified PertAcoustic Google Drive folder.
- [ ] The Google Doc is the primary human-facing deliverable and is written in Indonesian.
- [ ] The Google Doc closely follows the Biweekly 5 Google Doc's visual/editorial style: report-style title, period/date/status block, concise disclaimer, numbered engineering sections, explanatory prose, native Google Docs tables, inline engineering figures, figure captions, references section, typography, heading hierarchy, page layout, and readability.
- [ ] The Biweekly 5 Google Doc is not modified.
- [ ] The report records the exact repository revision/evidence cutoff: `667ccd59cf6657a75dfe3cc2b4c67488737ef028`.
- [ ] The report identifies the governing compact-casing task revision: `ad24d9146815f88368d8f6b1d635831d57aed13d`.
- [ ] The report identifies the governing reporting task revision used for remediation.
- [ ] Reporting-period dates are either supported by authoritative evidence or explicitly recorded as unresolved.
- [ ] Numbers match accepted engineering evidence; OD, ID, wall, bore, and packaging-margin dimensions are internally consistent and units are correct.
- [ ] Figures correspond to the described quantity, preserve provenance, and captions do not overclaim.
- [ ] Google Doc tables are native Google Docs tables, not pasted Markdown table text or screenshots.
- [ ] Engineering figures are embedded inline in the Google Doc when used, with captions and provenance.
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

- Verify Git state and confirm the implementation baseline/reporting cutoff used for report remediation.
- Inspect `git diff --name-only` or equivalent and confirm changes are limited to authorized Biweekly 8 reporting artifacts.
- Check that `results/biweekly-5/` is unmodified.
- Check that the Biweekly 5 Google Doc was not modified.
- Check that compact-casing engineering source/results are unmodified unless Planner/Reviewer explicitly authorized a reporting-only exception.
- Review `biweekly-8.md` against accepted evidence for dimension, unit, classification, and semantic consistency.
- Verify the native Google Doc title, folder placement, language, document structure, native tables, inline figures, captions, references, and link/identity.
- Verify the Google Doc does not treat the Biweekly 5 template as current engineering authority.
- Run the smallest relevant existing test or repository check needed to demonstrate preservation if any executable source or generated engineering artifact is touched. If only Markdown/reporting artifacts and the authorized Google Doc are changed, record that no code tests were required and explain why.

### Required evidence

The Executor MUST report:

- exact implementation revision or precise working-tree state;
- task revision used;
- reporting cutoff used;
- current report implementation baseline used;
- files changed;
- Google Doc title, URL/document ID, and target folder confirmation;
- Google Drive mutations performed;
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
- The current report implementation baseline `29a602029cf55a0b036887d776440447325bd864` cannot be resolved and no reviewed replacement remediation baseline has been supplied.
- The governing compact-casing task revision cannot be resolved.
- Accepted compact-casing evidence does not support the current preliminary values listed in this task.
- Report generation requires changing engineering authority, design source, simulation source, or accepted engineering results.
- The report would need to invent a product or engineering decision.
- Historical Biweekly evidence would need destructive modification.
- The Biweekly 5 Google Doc would need to be modified.
- Google Drive connector/API access is unavailable or cannot create/update the Biweekly 8 Google Doc directly in the specified target folder.
- The target PertAcoustic Google Drive folder cannot be resolved or is not writable.
- The Biweekly 5 Google Doc cannot be inspected sufficiently to reproduce its visual/editorial structure.
- Reporting-period dates cannot be established and a stakeholder requires exact dates rather than unresolved chronology.
- An externally visible action outside the single authorized Biweekly 8 Google Doc creation/update becomes necessary.

Do not stop merely because reporting-period dates are unresolved, some report data are intentionally unresolved, or the final report requires review after generation. Represent those uncertainties accurately.

## Side-effect authorization

Implementation authorization is strictly bounded to the task's defined reporting scope.

Unless explicitly authorized by this task, applicable repository policy, or designated authority, the task does NOT authorize:

- engineering source changes;
- compact-casing result modification;
- historical Biweekly 5 modification;
- Biweekly 5 Google Doc modification;
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
- Update `results/biweekly-8/biweekly-8.md` only as needed to preserve source/traceability consistency with the remediated Google Doc.
- Create `results/biweekly-8/figures/` only if justified by the report and provenance is preserved.
- Create minimal supporting generated reporting evidence under `results/biweekly-8/` only when required for traceability.
- Use the Google Drive connector/API to create or update only the Biweekly 8 native Google Doc titled `3d-design-biweekly-8` directly in the specified PertAcoustic folder.
- Use the Google Drive connector/API to copy/create the Biweekly 8 Google Doc from the Biweekly 5 Google Doc as a formatting/editorial template only, if that is the most reliable way to preserve native style.
- Use the Google Drive connector/API to write Biweekly 8 document content, create native Google Docs tables, insert accepted engineering figures inline, add figure captions, and record references in the Biweekly 8 Google Doc.
- Run non-destructive local verification.

Git commit authorization is not implied for the future reporting Executor unless separately supplied by the handoff for that execution slice.

The explicit Google Drive authorization above applies only to creating or updating the Biweekly 8 Google Doc in the specified folder. It does not authorize modification of the Biweekly 5 Google Doc, creation of additional Drive deliverables, link-sharing changes, publication outside the target folder, or any unrelated external-system mutation.

## Expected terminal outcome

The Executor's implementation phase SHOULD end in **Review Required**:

- `results/biweekly-8/biweekly-8.md` exists.
- Native Google Doc `3d-design-biweekly-8` exists in the specified PertAcoustic Google Drive folder.
- Any justified supporting reporting artifacts exist under `results/biweekly-8/`.
- Verification evidence is truthfully reported.
- Engineering implementation changed: NO.
- Historical Biweekly artifacts modified: NO.
- Biweekly 5 Google Doc modified: NO.
- Biweekly 8 report source artifact generated/maintained: YES.
- Biweekly 8 Google Doc created/updated: YES.

The Executor does not self-declare final acceptance.

## Review and remediation handling

The Reviewer evaluates report artifacts against the exact governing task revision, reporting cutoff, accepted engineering evidence, and observed verification evidence.

If review identifies bounded corrections within the same reporting objective, update and republish this same task file only if the executable contract itself must change. Ordinary report corrections should remain implementation remediation under this task.

Materially new engineering objectives, new design decisions, new simulations, new authority needs, or scope expansion MUST return to Delivery Planning and become separate task work.

## Remediation

**Review basis:**
`.agents/tasks/biweekly-8-report.md @ c1d8d7c00d6fe3b3055bdabebb604f4e49bb86cb`

**Current report implementation:**
`29a602029cf55a0b036887d776440447325bd864`

### Required corrections

- Preserve `results/biweekly-8/biweekly-8.md` as the repository traceability/source artifact.
- Create the primary human-facing Biweekly 8 deliverable as a native Google Doc titled `3d-design-biweekly-8` directly in the specified PertAcoustic Google Drive folder.
- Use the Biweekly 5 Google Doc only as formatting/editorial template material.
- Write the Google Doc in Indonesian with a report-style title, period/date/status block, concise disclaimer, numbered engineering sections, explanatory prose, native Google Docs tables, inline accepted engineering figures, figure captions, references, and matching visual hierarchy/readability.
- Preserve all strict engineering semantics in this task, including dimensions, no-aerogel architecture, material hierarchy, unresolved pressure status, and thermal lower-bound labeling.
- Do not modify Biweekly 5 repository artifacts or the Biweekly 5 Google Doc.

### Additional verification

- Verify the Google Doc title, native format, target folder placement, Indonesian language, section structure, native tables, figure placement, captions, and references.
- Verify Biweekly 5 repository artifacts and the Biweekly 5 Google Doc remain unmodified.
- Verify the Executor's reported Google Drive mutations are limited to the authorized Biweekly 8 document in the specified folder.
