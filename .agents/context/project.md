<!-- code-agent-template:managed -->
# Project Context

**Status:** Verified against the current working tree
**Last verified:** 2026-07-29
**Repository base:** `d71811dc434a32f8631128fa20f4bb2dc890605a`

This file records only repository-observed behavior and explicit user direction. Period-specific reporting context belongs under `.agents/context/biweekly-N/`.

## Purpose

PertAcoustic is a research workspace for developing a 3D casing design for a downhole acoustic tool. The implemented software is currently a Python transient-thermal CAD-CAE prototype for concentric cylindrical casing layers. A dimensionally validated HTI-02-DHPC/D connection design does not yet exist in the cleaned repository.

## Intended Users

- Research collaborators preparing and reviewing PertAcoustic casing designs and biweekly progress reports.
- Engineering users running the local CAD, mesh, CalculiX, and result-extraction workflow.

Evidence: `cosmo/`, `.agents/context/biweekly-2/`, `.agents/context/biweekly-4/`, and `.agents/context/biweekly-5/`.

## Current Capabilities and Flow

The thermal workflow uses layer dictionaries ordered from outside to inside:

1. `cosmo/core/cad_generator.py` creates separate concentric CadQuery solids and exports a STEP assembly.
2. `cosmo/core/mesh_generator.py` fragments and meshes the STEP volumes with Gmsh and exports a CalculiX-compatible INP file.
3. `cosmo/core/solver_interface.py` appends material data, initial temperature, outer-temperature boundaries, and optional internal heat before invoking the bundled CalculiX solver. It removes stale outputs and rejects fatal CalculiX text even when the executable returns exit code 0.
4. `cosmo/core/result_extractor.py` parses FRD coordinates and temperature steps and fails if the requested time or inner boundary cannot be identified.
5. `cosmo/cosmo_runner.py` composes one CAD-mesh-solve-extract iteration.
6. `cosmo/optimization/optimizer.py` applies hard-coded geometry heuristics until the configured 50 C threshold is met or ten iterations are exhausted.
7. `cosmo/core/results_compiler.py` creates a comparison table using the same supplied threshold; it does not invent unavailable time-to-temperature metrics.

`results/hti-02-dhpc-d-20260716/` contains one historical 43 mm OD, 100 mm long SS316/Aerogel/PEEK run. Its raw FRD reproduces 25.0177 C, but the input was generated with conductivity divided by 1,000. The result is invalid and retained only as historical provenance.

`cosmo/biweekly5.py` generates the current HTI-connected preliminary CAD, one-hour radial trade study, closed 3D thermal model at 1 W, closed-vessel static and eigenvalue-buckling FEA at three mesh levels, analytical checks, figures, and Indonesian report under `results/biweekly-5/`. The current engineering status is FAIL.

## Technology Stack

- Python 3.11.5 in the local `.venv`.
- CadQuery for CAD, Gmsh for meshing, NumPy for FRD processing, and Matplotlib for plots. Evidence: `pyproject.toml` and imports under `cosmo/`.
- CalculiX 2.22 through `cosmo/ccx/calculix_2.22_4win/ccx_static.exe`; `README_Install` records binary provenance.
- Setuptools package metadata in `pyproject.toml` for `cosmo`, `cosmo.core`, and `cosmo.optimization`.

## Architecture and Entry Points

- Automated optimization: `cosmo/optimization/optimizer.py::run_automated_optimization`.
- Single iteration: `cosmo/cosmo_runner.py::run_cosmo_iteration`.
- Core stages: `generate_casing`, `generate_mesh`, `setup_and_run_calculix`, and `extract_max_internal_temperature` under `cosmo/core/`.
- Material properties: `cosmo/material_library.json`.

Run repository workflows from the repository root because output paths are relative to the current working directory.

## Commands

| Purpose | Command | Verification status |
|---|---|---|
| Check Python | `.\.venv\Scripts\python.exe --version` | Passed: Python 3.11.5 |
| Check dependencies | `.\.venv\Scripts\python.exe -c "import cadquery, gmsh, numpy, matplotlib"` | Passed on 2026-07-29 |
| Check solver | `.\cosmo\ccx\calculix_2.22_4win\ccx_static.exe -v` | Passed: CalculiX 2.22 |
| Run regression check | `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` | Passed: 8 tests on 2026-07-29 |
| Install project | `.\.venv\Scripts\python.exe -m pip install -e .` | Derived from `pyproject.toml`; not run during verification |
| Run optimizer | `.\.venv\Scripts\python.exe .\cosmo\optimization\optimizer.py` | Not run during cleanup; it mutates result artifacts |
| Reproduce Biweekly 5 | `.\.venv\Scripts\python.exe -m cosmo.biweekly5` | Passed on 2026-07-29; generates CAD, simulations, and report |

## Data and Integrations

- Geometry and boundary inputs are Python dictionaries; thermal properties come from `cosmo/material_library.json`.
- Intermediate formats include STEP, INP, FRD, CVG, DAT, STA, and related solver files. These are ignored by `.gitignore`.
- Tracked result summaries use JSON and Markdown. Generated plots and numerical CSV files stay under their run directory and are ignored.
- The only implemented external process is the bundled local CalculiX executable. No database, authentication flow, runtime network API, or secret-bearing environment variable was found.

## Repository Conventions

- Layer lists are ordered outermost to innermost and use `name`, `material`, and `thickness`.
- Iteration files use `casing_iterN.*`; archived outputs use `results/<run-id>/iteration_NN/`.
- Period-specific evidence belongs under `.agents/context/biweekly-N/`. When a task names a period, load that folder's `project.md` in addition to this file.
- The GitHub repository is private, and the user approved versioning the biweekly reports and supplier drawing on 2026-07-29. Agents still require an explicit request before staging, committing, or pushing.
- `.agents/context/README.md` remains uninitialized unless the user explicitly requests `generate-readme`.

## Constraints and Hazards

- The optimizer deletes an existing run log and moves or overwrites generated artifacts. It is not a read-only verification command.
- The reusable legacy pipeline covers transient heat transfer. The bounded Biweekly 5 runner adds preliminary pressure-shell FEA and analytical checks but does not validate sealing, collapse qualification, acoustic response, corrosion, fatigue, sour service, or manufacturability.
- Temperature extraction fails closed when the requested boundary or time is absent; callers must handle `ValueError` rather than substituting another metric.
- CalculiX can return exit code 0 after fatal input errors, so solver success requires clean logs and freshly generated result files.
- The Biweekly 5 hydrophone envelope, mating thread, adapter, and seal area are preliminary geometry only; supplier-controlled datums and seal qualification remain required before manufacture.
- Vacuum insulation and added thermal-mass blocks are out of scope because the design must be manufacturable with conventional CNC and assembly capability at the UGM Geophysics Laboratory.

## Evidence Provenance

- Source, manifests, current raw solver output, and remaining reference locations were inspected locally on 2026-07-29.
- Dependency imports, CalculiX 2.22, the result extractor against the raw FRD, and the comparison-table regression test passed.
- The complete Biweekly 5 CAD-mesh-solve-report runner passed on 2026-07-29 and reproducibly reported engineering status FAIL.
- Antigravity-generated legacy reports, presentations, hydrophone geometry, duplicate outputs, bootstrapping code, bytecode, and redundant solver binaries were deliberately removed as untrusted or unnecessary.

## Proposed Behavior

- Produce a 3D PertAcoustic casing design that can connect to the HTI-02-DHPC/D interface shown in `.agents/context/biweekly-5/HTI-02-DHPC_D MECH OUTLINE_.pdf`.
- Keep the hydrophone exposed to the acoustic environment while protecting internal electronics, subject to dimensions and requirements confirmed by the user or authoritative drawings.
- Use CAD-CAE evidence to iterate thermal casing geometry without presenting preliminary results as certification or manufacturing approval.

## Superseded Facts

- The deleted 70 mm, six-iteration legacy result and presentation are not authoritative project evidence.
- The deleted hydrophone adapter and envelope modules are not valid design progress.
- The repository no longer includes PyVista animation code, `get-pip.py`, the one-off restructure script, tracked Python bytecode, duplicate CalculiX bundles, or duplicate root/cosmo plots and CSV files.

## Known Gaps

- Dependencies are unpinned; no lockfile exists.
- No CLI entry point, lint/format configuration, or CI workflow exists.
- Regression coverage contains focused standard-library tests for result-table accuracy, Biweekly 5 geometry/thermal screens, HTI thread datums, and thermal-conductivity units.
- The packaging configuration does not explicitly include `material_library.json` or the bundled solver as package data.
- The historical thermal run used an incorrect conductivity conversion and is not valid evidence.
- The 146 mm radial candidate fails the closed 3D thermal, static-stress, displacement-convergence, and buckling criteria; no validated passing casing is currently claimed.

## Open Questions

- Which HTI drawing dimensions and datums control the new casing interface?
- What pressure, temperature, maximum OD, internal volume, and material constraints are authoritative for the next design?
- Should the bundled CalculiX executable remain in normal Git history or move to release storage/Git LFS later?
- Which result artifacts should be retained after a clean reproducible rerun?
