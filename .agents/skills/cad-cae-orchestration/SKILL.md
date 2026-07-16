---
name: cad-cae-orchestration
description: Execute and supervise this repository's COSMO-inspired closed-loop transient-thermal CAD-CAE workflow for concentric downhole casings. Use when Codex must configure or run CadQuery, Gmsh, and CalculiX iterations; extract inner-surface temperature; evaluate a thermal threshold; revise layer geometry or materials; or diagnose run failures and artifacts under cosmo/. Do not use this skill to claim structural, pressure, acoustic, fatigue, corrosion, sour-service, or cost validation.
---

# CAD-CAE Orchestration

## Respect the implemented scope

- Operate only the transient heat-transfer workflow implemented under `cosmo/`.
- Treat the COSMO-Agent paper (`arXiv:2604.05547`) as methodological inspiration, not proof that this repository implements its reinforcement-learning system or full constraint set.
- Use `cosmo/cosmo_runner.py::run_cosmo_iteration` as the single-iteration boundary and `cosmo/automated_optimization.py::run_automated_optimization` as the current hard-coded multi-iteration driver.
- Treat `cosmo/material_library.json` as the runtime material-property source.
- Do not infer structural, pressure, acoustic, fatigue, corrosion, sour-service, manufacturability, or cost performance from thermal results.
- Describe a passing design as satisfying the modeled thermal constraint. Do not call it globally optimal, qualified, certified, or field-ready.

## Establish the run contract

Before executing a state-changing workflow, establish and report:

- outer diameter and length in millimeters;
- layers ordered from outside to inside, each with a unique `name`, a material key from `cosmo/material_library.json`, and a positive thickness in millimeters;
- bottomhole boundary temperature in degrees Celsius;
- simulation duration in seconds;
- maximum allowed internal temperature in degrees Celsius;
- minimum internal diameter and any other geometry limits;
- maximum iteration count or other compute budget;
- whether to create optional plots or animation; and
- whether existing generated artifacts may be overwritten.

If the user omits a non-critical value, use a repository default only after stating it. The current automated driver defaults to 43 mm OD, 100 mm length, 150 degrees Celsius BHT, 3,600 seconds, an 85 degrees Celsius threshold, and at most 10 iterations. Re-read the source before relying on these values because they are not exposed through a stable CLI.

Do not treat historical files under `cosmo/results/` as authoritative run inputs. Their thresholds, configurations, or pass labels may differ from the current source.

## Validate inputs

Perform these checks before generating geometry:

1. Confirm that OD, length, duration, temperatures, thicknesses, and iteration limit are finite and physically meaningful for the requested model.
2. Confirm every material key exists in `cosmo/material_library.json`. Do not silently substitute a material.
3. Compute the modeled internal diameter:

   `ID = OD - 2 * sum(layer thicknesses)`

4. Reject non-positive ID and any ID below the agreed minimum.
5. Compare the configuration with all user-supplied envelope constraints, including maximum OD. Do not enlarge OD merely to satisfy the thermal threshold when doing so violates another constraint.
6. Keep layer names stable and unique because Gmsh physical groups and CalculiX element sets use them.
7. Flag material properties or boundary conditions that are assumptions rather than verified design data.

## Run preflight checks

Run the workflow from `cosmo/` because several runtime paths are relative to the current directory.

1. Inspect `git status --short` and identify generated files that are already modified or tracked.
2. Inspect the intended output names before execution. The automated and quick-test scripts can remove, move, or overwrite iteration artifacts and logs.
3. Obtain user approval before overwriting artifacts unless the request already grants that authority.
4. Verify the Python interpreter and required imports for the requested stages: `cadquery`, `gmsh`, and `numpy`. Verify `matplotlib`, `pyvista`, and `vtk` only when their optional outputs are requested.
5. Verify that `ccx/calculix_2.22_4win/ccx_static.exe` exists and that its version command succeeds.
6. Do not install or upgrade dependencies unless the user explicitly authorizes dependency changes.
7. Stop before simulation when the environment cannot satisfy a required preflight check. Report the exact missing dependency or executable.

## Choose the execution mode

### Run one controlled iteration

Prefer `run_cosmo_iteration(...)` when inputs differ from the automated driver's hard-coded values or when evaluating a deliberate design revision. Invoke it from `cosmo/`, pass an unused iteration number, and keep animation disabled unless requested.

The function performs this sequence:

1. Generate a multi-solid STEP assembly with CadQuery.
2. Fragment and mesh the volumes with Gmsh, then write a CalculiX-compatible INP file.
3. Append material definitions, thermal initial conditions, the outer-temperature boundary condition, and the heat-transfer step.
4. Run CalculiX and produce FRD and diagnostic files.
5. Parse the FRD file and extract the maximum temperature near the modeled inner radius.
6. Optionally create an animation; never make visualization success a convergence requirement.

### Run the automated driver

Run `python automated_optimization.py` only when all hard-coded inputs match the approved run contract and overwriting its outputs is acceptable. Re-read the driver immediately before execution.

Do not silently patch production source merely to pass different run parameters. For custom inputs, orchestrate controlled single iterations. If the user requests a reusable parameterized interface, treat that as a separate code change with tests.

### Perform a read-only assessment

When asked to inspect prior results, analyze the existing source, JSON, solver status, and result files without running side-effectful scripts. Do not use `quick_test.py` as a read-only verification command.

## Gate every iteration on evidence

Do not advance the loop merely because a function returned or a file exists. Verify each stage:

1. **CAD:** Confirm that the STEP file exists, is non-empty, and represents the requested OD, length, layer count, and ordering.
2. **Mesh:** Confirm that the INP file exists and is non-empty. Treat a mismatch between volume count and layer count as invalid material mapping, not a harmless warning.
3. **Solver:** Require a successful CalculiX exit and inspect relevant status, data, and captured error output. Confirm that the FRD file exists and contains temperature results for the intended job.
4. **Extraction:** Confirm that a temperature step exists near the requested time and record the actual selected time. If no inner-boundary nodes are found, reject the fallback maximum over all nodes as an invalid inner-surface metric.
5. **Constraint:** Compute `passed = max_internal_temperature <= threshold` independently. Do not trust a stored `converged` flag or historical PASS label without recomputing it.
6. **Artifacts:** Associate every metric with its exact configuration, iteration number, and file paths.

Treat `None`, missing files, malformed output, empty node sets, non-finite temperatures, or incomplete solver steps as failed iterations.

## Revise the design deliberately

When the modeled thermal constraint fails:

1. Quantify the absolute and percentage temperature overshoot.
2. Preserve the best valid candidate observed so far.
3. Propose a bounded change supported by thermal reasoning, such as changing an insulation material or thickness, while continuing to enforce all geometry constraints.
4. Prefer one attributable design change per iteration when practical. If multiple coupled changes are necessary, state why their effects cannot reasonably be isolated.
5. Validate the proposed configuration before running it.
6. Record the previous configuration, proposed configuration, rationale, and expected directional effect.
7. Never invent material properties. Add or alter material data only through a separately authorized source change.

Stop the loop when any of these conditions occurs:

- the thermal threshold is satisfied;
- the approved iteration, time, or compute budget is exhausted;
- a required stage fails or produces invalid evidence;
- every admissible revision would violate a geometry or user constraint;
- successive valid iterations show no meaningful improvement; or
- continuing requires a new engineering choice or authority from the user.

Never run an unbounded optimization loop.

## Handle failures

For a failed iteration:

1. Stop before revising the design from an invalid metric.
2. Identify the failing stage, command or function, iteration configuration, and affected artifacts.
3. Inspect available logs and output using read-only commands.
4. Attempt only safe, in-scope diagnostics that do not alter dependencies, source, or prior artifacts.
5. Distinguish environmental failure, geometry failure, mesh/material mapping failure, solver failure, extraction failure, and constraint failure.
6. Request user direction only when recovery requires new authority, overwriting artifacts, changing dependencies, or making a material engineering choice.

## Report the outcome

For every valid iteration, report:

- iteration number and complete layer configuration;
- OD, length, computed ID, BHT, duration, and threshold;
- generated STEP, INP, FRD, and summary paths that actually exist;
- extracted maximum internal temperature and actual result time;
- independently computed pass or fail status;
- warnings, assumptions, and verification gaps;
- revision rationale and parameter delta, when applicable; and
- the best valid candidate so far.

In the final result:

1. State why the loop stopped.
2. Identify the best valid candidate and whether it satisfies the modeled thermal constraint.
3. Separate generated evidence from historical or unverified artifacts.
4. List failed or skipped optional deliverables without presenting them as completed.
5. State explicitly that the thermal workflow does not validate structural integrity, pressure containment, acoustic performance, fatigue, corrosion, sour-service suitability, manufacturability, or cost.
