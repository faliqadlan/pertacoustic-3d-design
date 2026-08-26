---
title: Compact Downhole Casing Redesign
document_id: AGENT-TASK-002
version: 1.1
status: Draft
language: en-US
last_updated: 2026-08-26
scope:
  - compact downhole casing design
  - electronics packaging and clear ID feasibility
  - geometric, structural, and thermal trade study
  - HTI-02-DHPC/D interface integration
  - preliminary engineering screening
authority_note: A published validated task authorizes only the bounded implementation scope explicitly defined by the task and applicable approved repository authority. Observed repository evidence governs claims about current implementation reality but does not silently redefine the task or its intended authority.
---

# Executable Task

This file defines a bounded software-delivery contract for the PertAcoustic 3D compact downhole casing redesign.

A validated task MUST provide enough authority, scope, acceptance, verification, and stop-condition information for an Executor to proceed without inventing material product, requirement, architecture, scope, or approval decisions.

This is an umbrella task covering internal packaging investigation, geometry sizing, structural screening, 2-hour transient thermal simulation, and HTI-02-DHPC/D interface integration.

## Task identity

**Task title:**  
Compact Downhole Casing Redesign: Geometry, Packaging, Thermal, and Structural Screening

**Task path:**  
`.agents/tasks/compact-downhole-casing-redesign.md`

**Task contract state:**  
Draft

The task file is the executable delivery contract.

Execution and review lifecycle states such as `In Execution`, `Review Required`, `Remediation Required`, and `Accepted` SHOULD normally be tracked by orchestration, review records, repository metadata, or another mechanism that preserves the exact governing task revision.

A lifecycle-status update MUST NOT silently replace the immutable task revision that governed an execution attempt.

When remediation materially changes this executable contract, edit this same stable task path, return it to Draft as needed, and republish it as a new immutable governing task revision before renewed execution.

**Delivery objective / Work Package / MVP:**  
PertAcoustic Downhole Casing Compact Redesign (20 August 2026 Direction)

**Owner / designated planning authority:**  
PertAcoustic Research Collaboration / Designated Technical Authority

## Delivery context

Historical Biweekly 5 work investigated a preliminary 200 mm (7.87 in) OD, 425 mm long casing concept designed for a 150 °C external environment, 1-hour exposure duration, and 10,000 psi screening pressure with a 41 mm clear ID for a legacy board layout.

Under the 20 August 2026 design direction, the operational envelope is refocused on a representative ~1000 m deployment context with an external ambient temperature of 70 °C and a conservative 2-hour (7200 s) thermal exposure duration. The geometric constraints require exploring a preferred casing OD of 1.75 in (44.45 mm), an absolute maximum casing OD of 2.25 in (57.15 mm), a maximum overall tool length of 2.0 m (2000 mm), and preserving mechanical interface compatibility with the HTI-02-DHPC/D hydrophone outline. User notes also reference contextual downhole information regarding nominal 2-7/8 in tubing and a 2.441 in dimension (pending confirmation as wellbore/tubing drift context rather than casing OD).

Crucially, the redesign must investigate whether an internal clear diameter of approximately 30 mm is physically feasible for the downhole electronics packaging (incorporating the currently selected PCM1808 ADC, STM32 MCU, power regulation, RTC, SD storage, and wiring harness) rather than assuming 30 mm a priori. MCU or ADC component substitutions are outside the scope of this task.

An objective multi-disciplinary trade study across geometry, packaging clearance, insulation thickness, thermal barrier performance (evaluating the inherited 1 W screening heat load and comparing against justified component operating limits), and structural pressure screening is required. Concluding that 1.75 in OD is infeasible while another diameter ≤ 2.25 in OD satisfies the requirements is an entirely valid, approved engineering outcome. Because authoritative downhole casing design pressure remains unresolved, structural evaluations and final geometry recommendations must explicitly state their underlying pressure assumptions and remain conditional where field pressure authority is absent.

All historical Biweekly 5 reports, code, and simulation results must remain preserved as baseline provenance without modification or overwriting.

## Baseline and task revision

**Implementation baseline:**  
`b33e1622b04ec5e723c634573dbfa93aaa065576`

**Task revision:**  
`resolved when published`

`resolved when published` is a Draft placeholder. It is not sufficient for T5.

Before this task is treated as `Validated/Published` or handed to an Executor, the exact immutable governing task revision MUST be resolvable.

For Git repositories, the preferred published task identity is:

```text
.agents/tasks/compact-downhole-casing-redesign.md @ <full Git commit SHA containing the governing task content>
```

The immutable revision MAY be supplied externally by version-control history, publication metadata, Planner handoff, runtime metadata, or another repository-approved immutable content-identity mechanism. The task body does not need to embed the commit SHA that contains itself.

If establishing the immutable published task revision requires an otherwise unauthorized commit, publication, or other side effect, stop for the applicable authorization. Do not claim the task is Validated/Published while its governing revision remains unresolved.

The implementation baseline and governing task revision are separate references.

Do not change the implementation baseline silently during execution.

If parallel or intervening repository changes require reconciliation, return the issue to planning or follow explicit repository policy.

## Objective

Execute an integrated geometry, electronics packaging, transient thermal, and structural trade study for the compact downhole casing (preferred OD 1.75 in / 44.45 mm, maximum OD 2.25 in / 57.15 mm, maximum overall length 2.0 m, external temperature 70 °C, 2-hour duration, ~1000 m deployment context) interfacing with the nominal HTI-02-DHPC/D hydrophone interface concept. Determine whether 1.75 in OD with ~30 mm clear ID is feasible or identify the optimal feasible envelope ≤ 2.25 in OD, evaluating thermal behavior against justified component operating limits and reporting structural screening under explicit pressure scenarios, while preserving historical Biweekly 5 artifacts intact.

## Authoritative inputs

List of approved sources, working notes, and provenance constraining this task:

### Governing authority

1. **Formal 20 August 2026 Minutes of Meeting (MoM):**
   - External design temperature: 70 °C.
   - Preferred casing OD: 1.75 in (44.45 mm).
   - Maximum casing OD: 2.25 in (57.15 mm).
   - Maximum overall tool length: 2.0 m (2000 mm).
2. **20 August 2026 Meeting Notes (Contextual & Planning Inputs):**
   - Representative deployment / mobilization context: approximately 1000 m depth.
   - Conservative thermal exposure / design duration: 2.0 hours (7200 s).
   - Contextual wellbore / tubing reference: nominal 2-7/8 in tubing and a 2.441 in dimension (contextual bore drift, pending confirmation; not an approved tool casing OD requirement).
3. **Current User Design Direction:**
   - Investigate whether an internal clear diameter of approximately 30 mm is physically feasible for electronics packaging; do NOT assume 30 mm ID is feasible without packaging evidence.
   - Require an objective geometry/packaging/thermal/structural trade study rather than forcing 1.75 in OD to PASS.
4. **Historical Biweekly 5 Evidence & Repository Baseline (`.agents/context/biweekly-5/project.md`, `cosmo/biweekly5.py`):**
   - Baseline screening internal heat load: approximately 1.0 W continuous dissipation (inherited screening scenario).
   - Historical 200 mm OD / 150 °C / 1-hour geometry and baseline CAE simulation pipeline.
   - Historical 10,000 psi (68.9 MPa) screening pressure condition (screening reference scenario only, not an approved design pressure).
   - Historical component-zone temperature extraction logic.
5. **HTI Supplier Mechanical Outline (`.agents/context/biweekly-5/HTI-02-DHPC_D MECH OUTLINE_.pdf`):**
   - Nominal interface concept: 7/16-20 UNF-2A male adapter, nominal seal area, and exposed acoustic sensing head.
   - Documented limitations: A dimensionally validated connection design does not yet exist; supplier-controlled datums, thread tolerances, seal groove geometry, pressure-tight sealing, and manufacturing dimensions remain provisional and uncertified.
6. **Repository AI Delivery Contract & Materials:**
   - `.agents/AGENTS.md`, `.agents/software-workflow.md`, `.agents/context/project.md`.
   - `cosmo/material_library.json` (Inconel 718, Pyrogel/Aerogel, PEEK, SS316).

### Requirement traceability

- `REQ-GEO-001` (Casing Outer Diameter) → Formal 20 August 2026 MoM: Preferred OD is 1.75 in (44.45 mm); maximum allowable OD is 2.25 in (57.15 mm).
- `REQ-GEO-002` (Overall Length) → Formal 20 August 2026 MoM: Maximum overall tool length is 2.0 m (2000 mm), including housing, endcaps, and HTI interface adapter.
- `REQ-PKG-001` (Internal Electronics Packaging & Clear ID Investigation) → Current User Direction & Hardware Baseline: Investigate whether an internal clear diameter of approximately 30 mm is feasible for the selected electronics stack (currently selected PCM1808 ADC, STM32 MCU, power regulation, RTC, SD storage, interconnects, and wire harness); do not assume 30 mm ID is feasible without physical component layout and radial clearance evidence.
- `REQ-IF-001` (Acoustic Interface Concept) → HTI Supplier Drawing & Historical Provenance: Preserve nominal 7/16-20 UNF-2A interface concept, acoustic head exposure, and wiring pass-through while explicitly treating thread tolerances, seal grooves, and pressure retention as provisional engineering screening.
- `REQ-THM-001` (Thermal Screening & Component Limits) → Formal MoM, Meeting Notes, & Biweekly 5 Baseline: External ambient temperature 70 °C; conservative duration 2 hours (7200 s); inherited screening heat load 1.0 W (with option to report refined hardware estimates alongside 1 W baseline); evaluate results against justified component operating temperature limits where authoritative evidence exists (classifying unestablished limits as conditional).
- `REQ-STR-001` (Structural Pressure Screening) → Meeting Notes & Historical Provenance: Perform structural screening across explicit pressure scenarios (including ~1000 m hydrostatic context ~10 MPa and the historical 10,000 psi / 68.9 MPa screening benchmark); explicitly document that authoritative casing design pressure remains unresolved and structural recommendations are conditional on field pressure confirmation.
- `REQ-PROV-001` (Historical Provenance & Non-Destructive Separation) → `.agents/context/project.md` & Biweekly 5 Context: Historical Biweekly 5 report, CAD/CAE scripts, and results in `results/biweekly-5/` and `cosmo/biweekly5.py` must remain preserved and unmodified.

Do not use existing implementation as retroactive justification for missing authority.

## Scope

### In scope

- **Electronics Packaging & Clear ID Feasibility Evaluation:**
  - Physical dimension and layout review for the selected hardware components (currently selected PCM1808 ADC, STM32 MCU, power module, RTC, SD, cabling). Packaging rearrangement and axial reorientation are permitted; MCU/ADC component substitution is excluded.
  - Determination of whether ~30 mm clear ID is feasible and establishment of the minimum required clear ID $D_{\text{clear}}$.
- **Structural Pressure Screening & Wall Sizing:**
  - Analytical Lamé stress, von Mises yield FoS, and long-cylinder buckling calculations for Inconel 718 across candidate outer diameters (44.45 mm to 57.15 mm).
  - Parametric evaluation under explicit external pressure scenarios (e.g., ~1000 m hydrostatic context and 10,000 psi legacy screening reference) with explicit notation of unresolved design pressure authority.
- **Parametric Thermal Modeling & Trade Study:**
  - 2-hour (7200 s) transient thermal simulation under 70 °C external ambient boundary.
  - Evaluation of the inherited 1.0 W baseline screening heat load (and comparison with refined hardware dissipation estimates if available).
  - Multi-layer evaluation (Inconel 718 outer barrel, Aerogel insulation layer, PEEK liner) and assessment of component-zone temperatures against justified manufacturer operating limits.
- **Trade Study Matrix & Engineering Recommendation:**
  - Structured trade-off matrix evaluating combinations of OD (44.45 mm / 1.75 in to 57.15 mm / 2.25 in), clear ID, insulation thickness, structural FoS, and 2-hour transient thermal response.
  - Formal engineering conclusion regarding 1.75 in OD feasibility and recommended casing geometry ≤ 2.25 in OD, noting conditional structural/thermal limits where authoritative requirements are unresolved.
- **3D Parametric CAD Assembly:**
  - Parametric CAD models generating the compact casing assembly (housing barrel, endcaps, internal sleeve/carrier, axial buffers, and nominal HTI adapter) with total modeled length ≤ 2.0 m.
  - STEP/assembly export for mechanical visualization.
- **Verification & Automated Testing:**
  - Automated tests verifying compact casing geometry sizing, packaging clearance logic, analytical structural formulas, thermal extraction routines, and nominal HTI thread datums without regressing historical Biweekly 5 tests.

### Out of scope

- Modifying, renaming, or overwriting historical Biweekly 5 code (`cosmo/biweekly5.py`), context (`.agents/context/biweekly-5/`), or results (`results/biweekly-5/`).
- Substituting the PCM1808 ADC or STM32 MCU with different integrated circuits.
- Manufacturing shop drawings, machining G-code, tooling specifications, or certified physical fabrication drawings.
- Physical pressure-vessel certification, API/ASME stamp qualification, or high-temperature well-logging field qualification.
- Physical O-ring seal compound qualification, sour-gas ($H_2S$) qualification, or downhole corrosive wear testing.
- Exotic thermal technologies excluded by UGM lab CNC constraints (vacuum dewar flasks, active Stirling coolers, or active phase-change material blocks).
- Altering the material library unit system or corrupting CalculiX conductivity units.

### Preserved behavior

- Existing Biweekly 5 tests (`tests/test_biweekly5.py`) and compiler tests (`tests/test_results_compiler.py`) continue to pass without regression.
- Core simulation engines (`cosmo/core/cad_generator.py`, `cosmo/core/mesh_generator.py`, `cosmo/core/solver_interface.py`, `cosmo/core/result_extractor.py`) maintain unit consistency and fail-closed error handling.
- Nominal HTI-02-DHPC/D interface concept (7/16-20 UNF-2A thread pitch, 10.16 mm engagement, nominal seal area, and acoustic head exposure).
- Conventional CNC manufacturability constraint for components fabricated at the UGM Geophysics Laboratory.

## Dependencies and assumptions

### Dependencies

- Python 3.11 environment with CadQuery, Gmsh, NumPy, Matplotlib.
- CalculiX 2.22 solver (`cosmo/ccx/calculix_2.22_4win/ccx_static.exe` or environment-compatible CCX binary).
- Mechanical outline specification: `.agents/context/biweekly-5/HTI-02-DHPC_D MECH OUTLINE_.pdf`.
- Material database: `cosmo/material_library.json`.

### Approved assumptions

- **External Ambient Temperature:** 70 °C constant Dirichlet boundary condition on outer exposed surfaces (Formal MoM).
- **Exposure Duration:** 2.0 hours (7200 seconds) conservative transient thermal exposure (Meeting Notes).
- **Baseline Heat Load:** 1.0 W continuous internal heat dissipation evaluated as an inherited Biweekly 5 screening baseline.
- **Hardware Configuration:** Currently selected PCM1808 ADC and STM32 MCU baseline hardware; packaging orientation and placement may be optimized axially.
- **Objective Trade-Off Rule:** If physics, structural safety, or packaging clearance reveals that 1.75 in (44.45 mm) OD cannot satisfy operational component temperature limits over 2 hours with required structural margin, concluding infeasibility of 1.75 in and recommending a feasible OD ≤ 2.25 in (57.15 mm) is an approved valid outcome.

### Unresolved authority items & conditional assumptions

- **Authoritative Casing Design Pressure:** Unresolved. ~1000 m is deployment context, not an approved design pressure rating. Structural screening will evaluate explicit scenarios (including ~1000 m hydrostatic and 10,000 psi legacy screening), but final structural acceptance remains conditional on client pressure specification.
- **Component Temperature Limits:** The legacy 50 °C optimizer threshold is not an approved design authority. Thermal results must be evaluated against justified datasheet operating limits (e.g., industrial -40 °C to +85 °C or commercial 0 °C to +70 °C ratings). Where specific component limits are unverified, thermal acceptance remains conditional.
- **Supplier-Controlled HTI Interface Geometry:** Unresolved. Supplier-controlled datums, exact thread tolerances, seal gland dimensions, and pressure-tight sealing details remain unverified and provisional.
- **Wellbore / Tubing Drift Reference:** The 2-7/8 in tubing and 2.441 in dimension are contextual bore notes pending confirmation, not approved casing OD constraints.

### Remaining approval requirements

- **Task Publication Approval:** Designated technical authority review and approval to publish this task contract from Draft to Validated/Published.
- **Design Pressure & Final Geometry Approval:** Human engineering and client review of the trade study matrix and recommended OD/ID configuration before initiating physical procurement or machining.

## Required capabilities

- Repository read and write
- Local Python command execution in `.venv`
- CadQuery 3D solid modeling and STEP export
- Gmsh finite element mesh generation
- CalculiX FEA execution and FRD parsing
- Automated test execution (`unittest`)

Runtime, model, vendor, reasoning level, or agent implementation SHOULD NOT be encoded here.

## Execution constraints

### Constraints

- **Honest Screening Reporting:** Do not manipulate material properties, heat transfer coefficients, or safety margins to force a "PASS" on the 1.75 in OD candidate. Report true physical screening outputs.
- **Packaging Evidence:** Packaging feasibility for ~30 mm ID must be demonstrated with explicit physical component dimensions, axial stacking, and radial clearances for the selected PCM1808 ADC and STM32 MCU.
- **Preliminary Screening Status:** All structural, thermal, and packaging results must be explicitly designated as preliminary engineering screening, not manufacturing certification or commercial rating.
- **Unit and Solver Integrity:** Maintain strict SI/CalculiX unit conventions (Conductivity in $\text{W}/(\text{m}\cdot\text{K})$, dimensions in mm, pressures/stresses in MPa).
- **Reuse and Historical Separation:** Reuse existing repository CAD/CAE mechanisms where appropriate; ensure all new outputs and code maintain clean separation from historical Biweekly 5 artifacts.

## Acceptance criteria

- [ ] **Packaging Feasibility Assessment:** Packaging analysis objectively investigates and documents whether the selected electronics (PCM1808 ADC, STM32 MCU, power, sensors, wiring) can package within ~30 mm clear ID (or establishes the exact minimum required clear ID $D_{\text{clear}}$ based on physical board dimensions and clearance).
- [ ] **Parametric Trade Study Execution:** Trade study evaluates casing ODs across the range from preferred 1.75 in (44.45 mm) to maximum 2.25 in (57.15 mm), varying Inconel wall thickness and Aerogel insulation thickness under 70 °C ambient and 2-hour duration.
- [ ] **Thermal Screening & Component Limits:** 2-hour (7200 s) transient thermal simulation reports internal cavity and zone temperatures under the inherited 1.0 W screening heat load, comparing results against justified component-specific operating limits where authoritative evidence exists (marking unestablished limits as conditional).
- [ ] **Structural Screening & Pressure Scenarios:** Structural calculations determine Lamé stresses, von Mises yield safety factors, and buckling factors under explicit pressure scenarios (including ~1000 m hydrostatic context and 10,000 psi legacy screening), explicitly documenting that authoritative field design pressure remains unresolved.
- [ ] **Trade Study Matrix & Recommendation:** A structured trade-off matrix clearly presents OD vs. clear ID vs. insulation thickness vs. structural FoS vs. 2-hour transient thermal response, providing a definitive recommendation on the feasibility of 1.75 in OD and the optimal envelope ≤ 2.25 in OD without exceeding 57.15 mm OD.
- [ ] **3D CAD Assembly:** Parametric CAD model generates the complete compact downhole casing assembly (housing, endcaps, internal sleeve, axial buffers, and nominal HTI adapter) with total modeled length ≤ 2.0 m.
- [ ] **Interface & Historical Preservation:** Nominal HTI-02-DHPC/D interface concept is modeled with explicit provisional assumptions; historical Biweekly 5 files (`cosmo/biweekly5.py`, `results/biweekly-5/`) remain unmodified; all existing tests in `tests/test_biweekly5.py` and `tests/test_results_compiler.py` pass.
- [ ] **Automated Test Coverage:** Automated unit tests in `tests/` verify compact casing geometry sizing, packaging clearance logic, analytical structural formulas, and thermal extraction routines.

## Verification requirements

### Required checks

- `python -m unittest discover -s tests -v` passes with 100% success (including both existing Biweekly 5 regression tests and new compact casing tests).
- Automated execution of the compact casing trade study runner generates complete tabular outputs and comparison plots without manual intervention.
- CadQuery solid verification confirms valid, watertight solids without invalid intersections or disconnected volumes.
- Result extraction routines confirm fail-closed behavior on missing solver steps or malformed outputs.

### Required evidence

The Executor MUST report:
- Implementation revision or exact working-tree state.
- Full output of all executed test suites.
- Complete numerical trade study matrix (OD, ID, wall thickness, insulation thickness, yield FoS, buckling FoS, 2-hour peak internal temperature).
- Final recommendation regarding 1.75 in OD feasibility and selected geometry ≤ 2.25 in OD.
- Justified component temperature limits used and identification of any conditional thermal/structural results.
- Generated CAD STEP files and thermal/structural trade-off comparison plots.
- Confirmation of zero regressions or modifications to Biweekly 5 historical artifacts.

## Stop conditions

The Executor MUST stop implementation and return the issue to planning when:
- Selected electronics (PCM1808 ADC, STM32 MCU, power, sensors) cannot physically fit within the maximum 2.25 in (57.15 mm) OD casing envelope under any valid structural/insulation configuration.
- Exact supplier-controlled HTI interface geometry or certified seal details are required for execution but unavailable from the supplier outline drawing.
- The CalculiX solver consistently fails to converge or exhibits numerical instability across valid mesh configurations.
- Execution requires unauthorized MCU/ADC component substitutions, unapproved external dependencies, or destructive changes to historical files.
- Material ambiguity arises regarding client operational constraints or approval boundaries.

## Side-effect authorization

Implementation authorization is strictly bounded to the task's defined execution scope.

Unless explicitly authorized by this task, applicable repository policy, or designated authority, the task does NOT authorize:
- Git commit, push, or pull-request creation.
- Deployment, external publication, or release tagging.
- Deletion or modification of historical `results/biweekly-5/` or `cosmo/biweekly5.py` files.
- Modification of package dependencies in `pyproject.toml` without prior review.

### Explicitly authorized side effects

- Creation of new compact casing Python modules under `cosmo/`.
- Creation of new compact casing unit tests under `tests/`.
- Creation of new compact casing results, plots, STEP files, and trade study markdown reports under a dedicated results directory (e.g., `results/compact-casing/`).

## Expected terminal outcome

The Executor's implementation phase SHOULD end in **Review Required**:
- Exact implementation revision or working-tree state identified.
- Complete verification results and trade study matrix available.
- Final engineering recommendation regarding 1.75 in vs ≤ 2.25 in OD documented with simulation evidence and explicit pressure/component-limit assumptions for Reviewer evaluation.

## Review and remediation handling

The Reviewer evaluates implementation against the exact governing task revision, applicable authority, implementation baseline, implementation revision, and observed evidence.

If review identifies bounded corrections within the same delivery objective, update and republish this same task file rather than creating filename-version copies.
