<!-- code-agent-template:managed -->
# Project Context

**Status:** Verified
**Last verified:** 2026-07-16
**Repository checkpoint:** `a134d1486e05940160f3ecafce60cbd938692405`

This file distinguishes repository-observed behavior from proposed product direction. Every durable claim below identifies repository evidence or a command successfully observed on the verification date.

## Purpose

PertAcoustic is a research workspace for developing a downhole Spectral Noise Logging (SNL) tool and studying automated enclosure design for that tool. The software currently present is a Python CAD-CAE workflow for iterative transient-thermal optimization of a concentric downhole enclosure; the broader sensing hardware and SNL analysis application remain proposals. Evidence: `.agents/context/references/reference-readme-old-1.md`, `.agents/context/references/2604.05547v1.pdf`, `cosmo/`, and `presentation/slide_outline.md`.

## Intended users

- UGM and PT Pertamina Hulu Energi research collaborators defining and evaluating the PertAcoustic concept. Evidence: `.agents/context/references/reference-readme-old-1.md` and `.agents/context/references/SESSION_LOG.md`.
- Engineering users or coding agents exploring thermal layer configurations and reviewing CAD, solver, temperature, and report artifacts. Evidence: `.agents/tasks/cosmo-run.md`, `cosmo/cosmo_runner.py`, and `cosmo/results/`.

## Current capabilities and flows

The implemented workflow operates on a parametric stack of cylindrical layers ordered from outside to inside:

1. `cad_generator.py` creates separate concentric CadQuery solids and exports a STEP assembly.
2. `mesh_generator.py` imports and fragments the STEP volumes in Gmsh, assigns layer physical groups, creates a second-order tetrahedral mesh, and exports a CalculiX-compatible INP file.
3. `solver_interface.py` reads local material properties, appends transient heat-transfer definitions to the INP file, applies the configured bottomhole temperature to the outer radial boundary, and invokes the bundled CalculiX executable as a subprocess.
4. `result_extractor.py` parses FRD nodal coordinates and temperature steps, then reports the maximum temperature near the requested inner radius.
5. `cosmo_runner.py` composes those stages for one iteration; `automated_optimization.py` applies hard-coded configuration heuristics until its temperature threshold is met or ten iterations are exhausted.
6. Supporting scripts compile Markdown/JSON/CSV results and produce plots or a PyVista/VTK MP4 animation. Evidence: `cosmo/results_compiler.py`, `cosmo/plot_results.py`, `cosmo/thermal_animator.py`, and `cosmo/generate_deliverables.py`.

Historical tracked artifacts record six iterations and a final reported inner temperature of 68.36 C for a 70 mm OD Titanium/Aerogel/PEEK configuration. These artifacts show prior output, not present-environment reproducibility. Evidence: `cosmo/results/optimization_log.json`, `cosmo/results/iteration_06/summary.json`, and `cosmo/results/final_report.md`.

## Technology stack

- Python 3.11; `python --version` returned `Python 3.11.5` on 2026-07-16.
- CadQuery for STEP geometry and Gmsh for volume meshing, as imported by `cosmo/cad_generator.py` and `cosmo/mesh_generator.py`.
- NumPy for FRD/result processing; Matplotlib for plots; PyVista and VTK for 3D visualization and animation. Evidence: imports in `cosmo/result_extractor.py`, `cosmo/plot_results.py`, and `cosmo/thermal_animator.py`.
- CalculiX 2.22 for transient heat-transfer solving; running `cosmo/ccx/calculix_2.22_4win/ccx_static.exe -v` from `cosmo/` returned `This is Version 2.22` on 2026-07-16. The upstream project is [CalculiX](http://www.calculix.de/).
- The design-loop concept is explicitly based on the bundled paper, [COSMO-Agent: Tool-Augmented Agent for Closed-loop Optimization, Simulation, and Modeling Orchestration](https://arxiv.org/abs/2604.05547). Evidence: `.agents/context/references/2604.05547v1.pdf` and `.agents/tasks/cosmo-run.md`.

No `pyproject.toml`, requirements file, Conda environment file, package metadata, or CI configuration was found by `rg --files` searches on 2026-07-16.

## Architecture and entry points

- Primary automated entry point: `cosmo/automated_optimization.py::run_automated_optimization`.
- Single-iteration orchestration boundary: `cosmo/cosmo_runner.py::run_cosmo_iteration`.
- Stage interfaces: `generate_casing`, `generate_mesh`, `setup_and_run_calculix`, and `extract_max_internal_temperature` in their correspondingly named modules under `cosmo/`.
- Configuration source: `cosmo/material_library.json`, containing density, conductivity, specific heat, notes, standards, and source URLs for nine modeled materials or effective layers.
- Historical outputs: `cosmo/results/` plus tracked root-level solver status/data artifacts and presentation assets under `presentation/`.

Most runtime paths are relative to the current directory, including `material_library.json`, `results/`, generated iteration files, and the solver path. Run the workflow with `cosmo/` as the working directory. Evidence: path construction in `cosmo/solver_interface.py`, `cosmo/cosmo_runner.py`, and `cosmo/automated_optimization.py`.

## Commands

| Purpose | Command | Evidence | Verification status |
|---|---|---|---|
| Install | Unknown | No dependency or environment manifest exists | Not run; required packages are not reproducibly specified |
| Check Python | `python --version` | Local interpreter | Passed: Python 3.11.5 |
| Check solver | From `cosmo/`: `.\ccx\calculix_2.22_4win\ccx_static.exe -v` | Bundled executable | Passed: CalculiX 2.22 |
| Static syntax check | Parse every `cosmo/*.py` file except `get-pip.py` with Python `ast.parse` | Repository Python sources | Passed for 24 files |
| Run automated workflow | From `cosmo/`: `python automated_optimization.py` | `cosmo/automated_optimization.py` | Not run; missing/incompatible dependencies and it overwrites generated outputs |
| Run quick verification | From `cosmo/`: `python quick_test.py` | `cosmo/quick_test.py` | Not run; it overwrites iteration artifacts and requires unavailable dependencies |
| Formal test suite | Unknown | No pytest/unittest configuration or test directory found; `quick_test.py` is a side-effectful workflow script | Not available |
| Lint or format | Unknown | No lint/format configuration found | Not run |
| Build or package | Unknown | No packaging manifest, build script, or CI workflow found | Not run |

## Data and integrations

- Inputs are Python dictionaries for geometry and boundary conditions plus the local `cosmo/material_library.json`; there is no implemented user-facing configuration file or CLI argument parser. Evidence: `cosmo/automated_optimization.py` and `cosmo/cosmo_runner.py`.
- Intermediate engineering files are STEP geometry, Gmsh/CalculiX INP meshes, CalculiX FRD results, and solver status/output files. `.inp` and `.frd` are ignored by the root `.gitignore`.
- Durable result formats include JSON summaries/logs, Markdown reports/tables, CSV numerical data, PNG plots, STEP models, and MP4 animation. Evidence: tracked contents of `cosmo/results/`, `cosmo/numerical_data.csv`, and `cosmo/temperature_plot.png`.
- The only implemented external-process integration is the bundled local CalculiX executable. `solver_interface.py` sets `OMP_NUM_THREADS=4`; no runtime network API, database, authentication mechanism, or secret-bearing environment variable was found in the core workflow.
- Reference documents are canonical under `.agents/context/references/`; no reference file needs to be copied to or duplicated at the repository root.

## Repository conventions

- Layer lists are ordered outermost to innermost and use `name`, `material`, and `thickness` fields. Evidence: `cosmo/cad_generator.py` and `.agents/tasks/cosmo-run.md`.
- Iteration files use `casing_iterN.*`; archived outputs use numbered subdirectories under `cosmo/results/`. Evidence: `cosmo/cosmo_runner.py` and the tracked result tree.
- New durable project facts belong in this file. `.agents/context/README.md` is human-facing context and must only be regenerated through the separate `generate-readme` procedure. Evidence: `.agents/AGENTS.md` and `.agents/skills/onboard-repository/SKILL.md`.
- Repository reference material remains under `.agents/context/references/`; stale root-level locations mentioned by older documents are not authoritative.

## Constraints and hazards

- The active Python environment cannot currently run the full workflow: CadQuery, Gmsh, PyVista, and VTK imports failed as unavailable; Matplotlib failed because its compiled extension is incompatible with installed NumPy 2.4.1. These import checks were observed on 2026-07-16.
- The automated and quick workflows create, delete, move, or overwrite iteration logs and generated artifacts. They are not read-only verification commands. Evidence: `cosmo/automated_optimization.py`, `cosmo/quick_test.py`, and `cosmo/generate_deliverables.py`.
- The solver models transient heat transfer with temperature boundary conditions. The repository contains no observed structural-pressure, acoustic-response, corrosion, seal, fatigue, or sour-service simulation that validates the broader tool requirements. Evidence: `cosmo/solver_interface.py` and `cosmo/material_library.json`.
- The current result extractor falls back to all nodes when it cannot find inner-boundary nodes, which can change the physical meaning of the reported maximum. Evidence: `cosmo/result_extractor.py`.
- Several scripts catch broad exceptions and return `None` or continue after optional visualization failures; callers must inspect actual output rather than assuming completion. Evidence: `cosmo/cosmo_runner.py` and `cosmo/automated_optimization.py`.
- Generated results and source defaults are not internally synchronized; see Known gaps.

## Evidence provenance

- Repository structure, current `HEAD`, source, reference files, and generated artifacts were inspected locally on 2026-07-16.
- `git rev-parse HEAD` returned `a134d1486e05940160f3ecafce60cbd938692405`; `git status --short --branch` was clean and reported `main...origin/main [ahead 1]` before this context edit.
- Python version, CalculiX version, individual dependency imports, and AST parsing were executed directly. No full CAD-CAE run was performed.
- Product targets and commercial specifications are retained as proposals unless implemented and validated by source/tests. Evidence includes `.agents/context/references/pertacoustic_tool_targets.md`, `.agents/context/references/FIND-specification-flyer.pdf`, `.agents/context/references/Oil-_-Gas-5.3-Noise-Logging-Tool-1.pdf`, and the remaining research Markdown files in that directory.

## Proposed behavior

- Develop a downhole SNL instrument for passive acoustic diagnosis of tubing/casing leaks, behind-casing migration, reservoir inflow, and cross-flow. Evidence: `.agents/context/references/reference-readme-old-1.md` and `.agents/context/references/commercial_snl_tools.md`.
- Target a 43 mm maximum tool OD, 150 C bottomhole temperature, 10,000 PSI pressure, 3,500 m depth, heavy-crude compatibility, and sour-service resistance. These are design targets, not verified capabilities. Evidence: `.agents/context/references/pertacoustic_tool_targets.md`.
- Evaluate hydrophones, high-temperature electronics, pressure housings, insulation, telemetry, storage, and supplier options. No final architecture or procured implementation is established by the repository. Evidence: `.agents/context/references/hydrophone_recommendations.md`, `.agents/context/references/downhole_tool_components.md`, and `.agents/context/references/sensor_market_survey.md`.
- Use closed-loop CAD-CAE iteration to revise geometry from solver feedback until engineering constraints are satisfied. The current repository demonstrates a hard-coded thermal prototype rather than the paper's trained reinforcement-learning system. Evidence: `.agents/context/references/2604.05547v1.pdf`, `.agents/tasks/cosmo-run.md`, and `cosmo/automated_optimization.py`.

## Superseded facts

- `.agents/context/references/reference-readme-old-1.md` describes a root `README.md` and root-level reference files. At checkpoint `a134d1486e05940160f3ecafce60cbd938692405`, no root README exists and surviving references are stored under `.agents/context/references/`.
- The planned onboarding checkpoint `1cea243971c5d3cf31792394d4f1e5930479d823` was superseded before implementation by commit `a134d1486e05940160f3ecafce60cbd938692405`, which records the approved reference cleanup.

## Known gaps

- No reproducible environment or dependency installation command exists.
- No formal automated tests, lint configuration, packaging configuration, or CI workflow exists.
- `cosmo/automated_optimization.py` currently defaults to an 85 C threshold, a Microporous initial design, and a ten-iteration cap, while `cosmo/results/optimization_log.json` records a 70 C threshold and a different Titanium/Aerogel progression. The tracked result history therefore cannot be attributed reproducibly to the current automated driver without additional provenance.
- `cosmo/results/comparison_table.md` labels iterations 3-5 as PASS even though their recorded maximum temperatures exceed the 70 C threshold shown in `cosmo/results/optimization_log.json`.
- `cosmo/results/final_report.md` names `iteration_06/casing_iter6.frd` as a deliverable, but that file is absent from `cosmo/results/iteration_06/` at verification time.
- The reported converged design uses a 70 mm OD, exceeding the proposed 43 mm maximum tool OD in `.agents/context/references/pertacoustic_tool_targets.md`.
- Historical solver status files show a completed 3,600-second step, but the current environment lacks the dependencies needed to reproduce the complete CAD-mesh-solve-extract pipeline.
- Root-level generated solver artifacts and Python bytecode are tracked even though some related intermediates are ignored, leaving artifact ownership and retention policy unclear.

## Open questions

- Which dependency versions and installation method should become the supported environment?
- Which optimization threshold, initial design, and geometry constraints are authoritative for future runs?
- Can the historical six-iteration result set be reproduced from a clean environment and the current source?
- Should the thermal optimizer enforce the proposed 43 mm OD limit, or is the 70 mm result an accepted research trade-off?
- Which generated solver and visualization artifacts should remain version-controlled?
