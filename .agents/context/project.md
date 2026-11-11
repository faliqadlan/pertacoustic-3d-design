<!-- code-agent-template:managed -->
# Project Context

**Status:** Verified against the current working tree
**Last verified:** 2026-11-11
**Repository base:** `c91c20c83a26d8d61e5e23b99a1fce28cad27c19`

This file records only repository-observed behavior and explicit user direction. Period-specific reporting context belongs under `.agents/context/biweekly-N/`.

## Purpose

PertAcoustic is a research workspace for an integrated downhole acoustic instrument concept and its earlier casing/thermal studies. The current Python/CadQuery model represents an 863 mm long, 44.45 mm OD self-contained memory-logging concept. It supports discussion of a TRL 5 development pathway; the TRL 4 laboratory apparatus is reference work rather than the target assembly. A supplier-validated HTI connection and field-qualified instrument do not yet exist.

## Intended Users

- Research collaborators preparing and reviewing PertAcoustic casing designs and biweekly progress reports.
- Engineering users running the local CAD, mesh, CalculiX, and result-extraction workflow.

Evidence: `cosmo/`, `.agents/context/biweekly-2/`, `.agents/context/biweekly-4/`, and `.agents/context/biweekly-5/`.

## Current Capabilities and Flow

The current integrated workflow is `python -m cosmo.integrated_downhole`:

1. `Parameters` and `build_design` define the housing, wet sensor head, pressure-boundary reservation, electronics cartridge, battery cartridge and deployment interface.
2. `verify_design` checks nominal solids, full envelope, prohibited part interference, ideal boundary coverage and acoustic guard openings.
3. Complete, sectional and exploded representations derive from the same parts. Eight STEP outputs are exported and reimported to check units, solid coverage, volume and bounds.
4. Optional VTK/Matplotlib rendering produces six views. `--no-figures` retains geometry/export checks without image generation.
5. `cosmo/integrated_report.py` generates an engineering summary from the evidence. Default outputs are under `results/integrated-downhole/`; use a fresh `--output` directory to preserve the committed baseline.

Recorded final-source evidence at `results/integrated-downhole/validation/review-remediation/` identifies the exact tested source revision, 81 passing tests, source hashes, STEP reconfirmation and the observable governance-approval turn pair. These are local checks, not CI or physical qualification.

The retained legacy thermal workflow uses layer dictionaries ordered from outside to inside:

1. `cosmo/core/cad_generator.py` creates separate concentric CadQuery solids and exports a STEP assembly.
2. `cosmo/core/mesh_generator.py` fragments and meshes the STEP volumes with Gmsh and exports a CalculiX-compatible INP file.
3. `cosmo/core/solver_interface.py` appends material data, initial temperature, outer-temperature boundaries, and optional internal heat before invoking the bundled CalculiX solver. It removes stale outputs and rejects fatal CalculiX text even when the executable returns exit code 0.
4. `cosmo/core/result_extractor.py` parses FRD coordinates and temperature steps and fails if the requested time or inner boundary cannot be identified.
5. `cosmo/cosmo_runner.py` composes one CAD-mesh-solve-extract iteration.
6. `cosmo/optimization/optimizer.py` applies hard-coded geometry heuristics until the configured 50 C threshold is met or ten iterations are exhausted.
7. `cosmo/core/results_compiler.py` creates a comparison table using the same supplied threshold; it does not invent unavailable time-to-temperature metrics.

`results/hti-02-dhpc-d-20260716/` contains one historical 43 mm OD, 100 mm long SS316/Aerogel/PEEK run. Its raw FRD reproduces 25.0177 C, but the input was generated with conductivity divided by 1,000. The result is invalid and retained only as historical provenance.

`cosmo/biweekly5.py` generated the historical HTI-connected preliminary CAD, one-hour radial trade study, closed 3D thermal model at 1 W, static pressure screening, figures and Indonesian report under `results/biweekly-5/`. Its recorded preliminary screening PASS is historical, not the current integrated geometry or a manufacturing pressure rating. `cosmo/compact_casing.py` supplies the later compact-casing packaging, material and analytical screening mechanisms reused by the integrated generator. Preserve both historical output directories.

## Technology Stack

- Python 3.11.16 in the local `.venv`, verified in this workspace.
- Observed imports: CadQuery 2.8.0, NumPy 2.4.6, Matplotlib 3.11.1, VTK 9.6.2 and Gmsh 4.15.2. CadQuery/OCP creates geometry; VTK renders the current views; Gmsh belongs to retained meshing workflows.
- CalculiX 2.22 through `cosmo/ccx/calculix_2.22_4win/ccx_static.exe`; `README_Install` records binary provenance.
- Setuptools package metadata in `pyproject.toml` for `cosmo`, `cosmo.core`, and `cosmo.optimization`.
- Dependencies are unpinned, no lockfile exists, and `pyproject.toml` does not declare a Python compatibility range. Observed versions are not minimum-version guarantees. No dependency installation was performed for this documentation update.

## Architecture and Entry Points

- Current integrated concept: `cosmo/integrated_downhole.py::{build_design,verify_design,export_all,generate,main}`.
- Generated engineering report: `cosmo/integrated_report.py::design_report`.
- Current project entrypoint: root `README.md`; CCL assessment: `docs/ccl-integration-assessment.md`.
- Automated optimization: `cosmo/optimization/optimizer.py::run_automated_optimization`.
- Single iteration: `cosmo/cosmo_runner.py::run_cosmo_iteration`.
- Core stages: `generate_casing`, `generate_mesh`, `setup_and_run_calculix`, and `extract_max_internal_temperature` under `cosmo/core/`.
- Material properties: `cosmo/material_library.json`.

Run documented commands from the repository root. The integrated generator resolves its default output from the source tree and accepts an explicit output directory; legacy workflow paths may be relative to the current directory.

## Commands

| Purpose | Command | Verification status |
|---|---|---|
| Check Python | `.venv/bin/python --version` | Python 3.11.16 verified |
| Check dependencies | `.venv/bin/python -c "import cadquery, gmsh, numpy, matplotlib, vtk"` | Imports verified on 2026-11-11 |
| Inspect current CLI | `.venv/bin/python -m cosmo.integrated_downhole --help` | Options verified: `--output`, `--parameters`, `--no-figures` |
| Reproduce integrated concept | `python -m cosmo.integrated_downhole --output /tmp/pertacoustic-reproduction` | Implemented CAD/STEP/view generation; prior execution evidence is committed |
| Generate geometry/STEP only | `python -m cosmo.integrated_downhole --output /tmp/pertacoustic-geometry-check --no-figures` | Implemented geometry and eight STEP round trips |
| Run regression check | `python -m unittest discover -s tests -v` | Committed exact-final-source evidence records 81 passing tests; not rerun merely for documentation changes |
| Install project | `python -m pip install -e .` | Derived editable setup; no fresh installation performed in this update |

Commands using `python` assume the compatible environment is active. The legacy Windows CalculiX executable was not revalidated in this update and is not required for integrated CAD generation.

## Data and Integrations

- Integrated geometry uses a `Parameters` dataclass; legacy boundary/geometry inputs use dictionaries. Material data comes from `cosmo/material_library.json`.
- Solver/intermediate formats are generally ignored. The current eight integrated STEP deliverables and the two final Biweekly 5 STEP files are tracked; do not assume every ignored extension is absent from Git.
- Tracked evidence includes JSON, Markdown, PNG, CSV and selected STEP files. Other generated intermediates remain subject to `.gitignore`; inspect actual Git state before asserting that an output is untracked.
- The integrated workflow uses local Python/OCP/VTK and reads Git revision metadata. CalculiX is a retained legacy external solver. No database, authentication flow or runtime service API is part of the integrated instrument generator.

## Repository Conventions

- Layer lists are ordered outermost to innermost and use `name`, `material`, and `thickness`.
- Iteration files use `casing_iterN.*`; archived outputs use `results/<run-id>/iteration_NN/`.
- Period-specific evidence belongs under `.agents/context/biweekly-N/`. When a task names a period, load that folder's `project.md` in addition to this file.
- GitHub reports the repository as **public**, verified on 2026-11-11. Earlier private-repository context must not justify adding restricted supplier/PHE material. The current human request authorizes bounded documentation commits/pushes to the existing feature branch; broader side effects remain subject to governing authorization.
- Root `README.md` is the primary human-facing document. `.agents/context/README.md` is a pointer, not a duplicate README source. The inherited `generate-readme` name has no repository implementation or available command in this environment.

## Constraints and Hazards

- The current concept uses a 70 °C / 7,200 s envelope, preferred 44.45 mm OD, maximum 57.15 mm OD and 2,000 mm length. Authoritative pressure, supplier interfaces, seals, corrosion conditions and complete-instrument thermal/acoustic qualification remain unresolved. Nominal CAD closure is not leak-tightness evidence.
- The current human follow-up permits CCL interoperability assessment and README/context completion while preserving the 863 mm geometry. The meeting's approximately 700 mm CCL and 1.0/1.5 m ALFA observations are unconfirmed. No CCL module, connector or final configuration has been selected; whole-toolstring envelope and time–depth requirements remain PHE decisions.
- The optimizer deletes an existing run log and moves or overwrites generated artifacts. It is not a read-only verification command.
- The reusable legacy pipeline covers transient heat transfer. The bounded Biweekly 5 runner adds preliminary pressure-shell FEA and analytical checks but does not validate sealing, collapse qualification, acoustic response, corrosion, fatigue, sour service, or manufacturability.
- Temperature extraction fails closed when the requested boundary or time is absent; callers must handle `ValueError` rather than substituting another metric.
- CalculiX can return exit code 0 after fatal input errors, so solver success requires clean logs and freshly generated result files.
- The Biweekly 5 hydrophone envelope, mating thread, adapter, and seal area are preliminary geometry only; supplier-controlled datums, physical pressure testing, and seal qualification remain required before manufacture.
- Vacuum insulation and added thermal-mass blocks are out of scope because the design must be manufacturable with conventional CNC and assembly capability at the UGM Geophysics Laboratory.

## Evidence Provenance

- Current source, parameters, geometry/export evidence, complete final-source test log, CLI options and environment imports were inspected on 2026-11-11 at the repository base above. The GitHub connector reports public visibility. This documentation update does not relabel earlier tests as newly executed.

### Historical verification (2026-07-29)

- Source, manifests, current raw solver output, and remaining reference locations were inspected locally on 2026-07-29.
- Dependency imports, CalculiX 2.22, the result extractor against the raw FRD, and the comparison-table regression test passed.
- The complete Biweekly 5 CAD-mesh-solve-report runner passed on 2026-07-29 and reproducibly reported preliminary screening PASS for the 200 mm OD thermal-priority concept.
- Antigravity-generated legacy reports, presentations, hydrophone geometry, duplicate outputs, bootstrapping code, bytecode, and redundant solver binaries were deliberately removed as untrusted or unnecessary.

## Proposed Behavior

- Preserve the current integrated acoustic/memory concept and its clearly provisional HTI interface.
- Keep the hydrophone exposed to the acoustic environment while protecting internal electronics, subject to dimensions and requirements confirmed by the user or authoritative drawings.
- Use CAD-CAE evidence to iterate thermal casing geometry without presenting preliminary results as certification or manufacturing approval.

## Superseded Facts

- The deleted 70 mm, six-iteration legacy result and presentation are not authoritative project evidence.
- The deleted hydrophone adapter and envelope modules are not valid design progress.
- The repository no longer includes PyVista animation code, `get-pip.py`, the one-off restructure script, tracked Python bytecode, duplicate CalculiX bundles, or duplicate root/cosmo plots and CSV files.

## Known Gaps

- Dependencies are unpinned; no lockfile exists.
- The integrated module CLI exists; no installed console-script entry point, lint/format configuration or CI workflow was found.
- Regression coverage includes integrated geometry/representation/STEP checks, compact-casing screens, historical Biweekly 5 geometry/thermal and HTI datums, solver/extractor failure handling, conductivity units and result-table accuracy.
- The packaging configuration does not explicitly include `material_library.json` or the bundled solver as package data.
- The historical thermal run used an incorrect conductivity conversion and is not valid evidence.
- The historical 200 mm OD, 425 mm concept's earlier screening results must not be presented as current integrated-instrument thermal evidence. The current 863 mm concept has no qualified complete-instrument two-hour thermal result.

## Open Questions

- Which HTI drawing dimensions and datums control the new casing interface?
- What authoritative design pressure, fluid/corrosion conditions, actual hardware dimensions and battery/thermal limits govern the next physical design stage?
- Which CCL arrangement, exact model, assembled envelope, sensor datums and time–depth records will PHE supply? Does the 2 m limit apply to the whole toolstring? See `docs/ccl-integration-assessment.md`.
- Should the bundled CalculiX executable remain in normal Git history or move to release storage/Git LFS later?
- Which result artifacts should be retained after a clean reproducible rerun?
