# CCL interoperability and depth-correlation assessment

**Date:** 11 November 2026

**Scope:** Documentation and interface assessment; no CAD, CCL sensor, connector or firmware implementation

**Preserved baseline:** `c91c20c83a26d8d61e5e23b99a1fce28cad27c19`, with an 863 mm × 44.45 mm PertAcoustic module

This assessment supports a PHE configuration decision. It does not select a final toolstring, claim compatibility with a particular PHE CCL, or change the current conceptual instrument. The [root README](../README.md) is the main project entrypoint.

## 1. Meeting observations and verified references

| Input | Evidence class | Treatment |
|---|---|---|
| CCL used for casing/tubing joint detection and depth correlation | Human meeting notes, consistent with manufacturer descriptions | Establish the required reference-data role with PHE |
| CCL approximately 0.7 m long | Preliminary meeting observation | Not a selected model or approved dimension |
| ALFA segments approximately 1.0 m and 1.5 m in diagrams | Preliminary meeting observation | Several configurations were shown; no universal length or mandatory ALFA component is inferred |
| PertAcoustic length 863 mm, OD 44.45 mm | Existing CAD/verification evidence | Preserve the acoustic instrument geometry |
| Maximum 2 m requirement | Human-adopted instrument constraint | PHE must clarify whether it also governs a connected toolstring |

No meeting photographs, supplier-controlled drawings, restricted documents or well data are included. The manufacturer examples below illustrate variation; none is identified as PHE's equipment.

### Operating principle and model-specific dimensions

The [Sondex CCL201 specification](https://dam.bakerhughes.com/m/1a4960ecd80f51df/original/Sondex-casing-collar-locator-CCL-spec.pdf) describes a magnetic-flux disturbance at changes in metal volume, with a coil signal recorded through its Ultrawire system. A collar indication is a feature for depth correlation, not by itself a complete continuous depth trajectory or an absolute survey datum.

| Public manufacturer example | Published envelope | Measurement-point information | Assessment implication |
|---|---|---|---|
| Baker Hughes Sondex CCL201 | 43 mm OD; 485 mm length | Sensor measure point: 174.45 mm | The one-page table does not define that coordinate's datum/direction. Obtain the exact outline before using it as an offset. Its Ultrawire interface is not established as compatible with PertAcoustic. |
| [Welltec CCL product range](https://www.welltec.com/products-services/intervention/casing-collar-locator-ccl) | 2⅛–3⅛ in. OD; 0.9–1.5 ft length, dependent on configuration | No single measurement-point datum is established by the overview | Converted ranges: 53.975–79.375 mm OD and 274.32–457.2 mm length. These ranges are not paired specifications for one selected model. |

The Welltec overview illustrates why a generic CCL designation cannot establish fit: even the smaller listed OD exceeds PertAcoustic's preferred 44.45 mm, and the larger exceeds 57.15 mm if that maximum governs the combined string. The Sondex example's 43 mm body does not prove that its crossovers, cablehead or complete string remain within either limit. No manufacturer pressure/temperature rating is transferred to PertAcoustic.

[Weatherford's Memory Logging Tool](https://www.weatherford.com/drilling-and-evaluation/wireline-products/cased-hole-formation-evaluation/memory-logging-tool/) describes combinability within its HD tool family. This and the Sondex toolbus example support a modular architecture comparison, not universal mechanical, electrical or protocol interoperability.

## 2. Alternative A — separate CCL on a combined toolstring

The current acoustic instrument would remain a module alongside a separate CCL. No connecting hardware has been modeled or selected.

### Envelope and connection reservations

Use the assembled make-up length, including the actual load path and any crossovers:

```text
L_string = 863 mm + L_CCL + L_interfaces,net + L_other
D_string = max(44.45 mm, D_CCL, D_interfaces, D_other external features)
```

`L_interfaces,net` must account for connector engagement/overlap already included in supplier dimensions; do not double-count threaded make-up. `L_other` includes only equipment actually required by the selected configuration. ALFA is not assumed in either term.

| Explicit planning scenario | Simple length subtotal | Meaning |
|---|---:|---|
| Unconfirmed meeting CCL length: 700 mm | 863 + 700 = 1,563 mm | 437 mm arithmetic difference from 2,000 mm, before net interfaces and any other required equipment |
| Published Sondex example: 485 mm | 863 + 485 = 1,348 mm | An illustrative manufacturer example, not a PHE configuration |

Neither subtotal verifies compatibility or compliance. If PHE's 2 m limit applies to the acoustic instrument alone, a separate total-string limit is still required. If it applies to the full string, all modules, external connections, deployment and retrieval hardware must be accounted for.

Practical dependencies are the exact connector gender/thread and mating datums, maximum external diameters, axial retention and rated tensile/bending loads, alignment/anti-rotation, pressure boundaries, electrical isolation or feedthroughs, power requirements, communications and deployment method. A generic retrieval eye is not evidence of a compatible toolbus crossover. No direct connection to the candidate 7.2 V battery or MCU interface is authorized by a CCL manufacturer's combinability claim.

### Measurement-point offset

Define a common assembled-string datum, with coordinate `s` increasing toward the downhole end. Obtain the actual CCL sensing coordinate `s_C` and hydrophone measurement coordinate `s_H` in the same units and assembled configuration. For a rigid, aligned string where the axial separation represents the along-hole offset:

```text
delta_s = s_H - s_C
D_H(t) = D_C(t) + delta_s
```

`D_C` must already be the depth of the CCL sensing point, not an unspecified cablehead/tool-zero depth. Positive `delta_s` means the hydrophone is farther downhole. PHE must confirm direction, make-up dimensions, reference location, and any deviation/curvature corrections. This along-hole relation must not be silently applied to true vertical depth.

The CAD hydrophone envelope occupies Z = 32–120.9 mm, measured upward from the lower nose. Its geometric midpoint is Z = 76.45 mm, or 786.55 mm below the 863 mm uppermost model extent. **This is not a verified acoustic measurement/phase center or a connector datum.** Neither a bare module length nor the unreferenced 174.45 mm CCL table entry is enough to establish `delta_s`.

### Deployment and measurement interaction

As engineering considerations requiring later validation, assess magnetic/electrical pickup into the low-level AFE, shared-power or telemetry interference, cable strain/noise, guard/body acoustic scattering and motion-induced noise. A common mechanical string does not automatically synchronize independent clocks. Logging speed, stationary acoustic acquisition, CCL signal processing, event timestamp latency and the tension/encoder correction strategy must be coordinated with PHE. No such interaction test or field qualification was performed here.

## 3. Alternative B — separately operated measurement systems

PHE would provide appropriate CCL/depth reference records while PertAcoustic records timestamped acoustic data. [Weatherford's depth-logger documentation](https://www.weatherford.com/drilling-and-evaluation/wireline-products/telemetry-systems/geothermal-depth-logger-and-encoder/) describes recording depth and line speed against clock time and merging those records with tool data. That establishes an industrial workflow example, not an existing PertAcoustic time–depth processing implementation.

Two cases need different handling:

- **Independent electronics with common, known conveyance:** if both sensing points share a verified trajectory and fixed separation, calibrated time alignment plus the measured offset may support correlation.
- **Different physical runs or independently moving tools:** one run's time–depth trajectory cannot be assigned to another tool by synchronizing wall clocks or adding a constant offset. The acoustic deployment needs its own depth-versus-time trajectory, tied through PHE's approved collar/reference-log correlation and common depth datum. A collar log from an earlier run can support that reference relationship, but does not reconstruct the later tool's motion.

If PHE cannot provide an appropriate acoustic-run time–depth trajectory or another justified localization method, timestamps alone cannot yield a defensible acoustic depth log.

### Required data exchange

| Data / definition | Why it is needed |
|---|---|
| Timestamped depth trajectory, units, resolution and gaps for the relevant deployment | Associate acoustic windows with position; distinguish movement, dwell, reversal and missing data |
| CCL signal/events with timestamps or depth, model identity and processing latency | Tie features to the reference log without treating every magnetic response as a unique collar |
| Depth datum and convention: e.g. specified well reference, measured depth versus TVD, tool-zero definition | Prevent datum shifts and double application of tool offsets |
| Clock timebase, epoch/timezone, precision, synchronization observations and reset history | Align independent records and identify clock jumps |
| Acoustic timestamp definition and sample-clock relationship | Distinguish the start, center or end of an acquisition/FFT window from file-write time |
| Actual sensor measurement-point coordinates and applied offset history | Apply the correct sign once; distinguish cablehead depth from CCL sensing depth |
| Logging direction, line speed, tension/stretch/encoder corrections, station and run identifiers | Avoid merging different passes or assuming surface cable movement equals downhole movement |
| Appropriate collar tally/reference log and PHE-approved tie points | Resolve repeated/missing features and establish the reference-depth relationship |

No data schema or PHE export format has been approved. CSV or another exchange format would require agreement on these semantics; selecting a file extension alone is insufficient.

### Time synchronization and drift

As a proposed processing method, compare the acoustic clock with a common reference before and after the run and retain the observations. Let `A0, A1` be acoustic-clock readings corresponding to reference times `T0, T1`. A two-anchor linear mapping would be:

```text
b = (T1 - T0) / (A1 - A0)
t_ref = T0 + b * (t_acoustic - A0)
```

Use consistent time units and identify the reference time standard explicitly. Temperature-dependent drift, resets or non-linear residuals may require additional anchors or segmented correction; two anchors do not prove a constant drift rate. The RTC and acquisition sample clock may also require separate characterization. After valid time alignment, interpolate the appropriate depth trajectory only within supported intervals, then apply the verified measurement-point correction. Do not interpolate blindly across missing records or mix separate runs.

For scale only, an **assumed** 20 ppm clock error over 7,200 s gives 0.144 s of timing error. At an **assumed** 0.1 m/s logging speed, the clock-only contribution is approximately 0.0144 m. These are illustrative calculations, not selected RTC specifications, logging requirements or total depth accuracy. Offset uncertainty, encoder/stretch errors, acoustic-window duration and synchronization latency remain additional terms. PHE must specify acceptable timing/depth uncertainty.

## 4. Integration strategy and open PHE decisions

Keep the existing acoustic/memory module unchanged and develop the external interface/data requirements for both alternatives. Alternative B avoids a new mechanical join only when PHE can supply an adequate acoustic-run trajectory and reference relationship. Alternative A can establish a fixed spatial relationship only after actual make-up and deployment interfaces are verified. Neither is selected as the final configuration.

| Open decision | Required PHE input |
|---|---|
| Physically connected CCL or separate logging system? | Intended operational arrangement, ownership and acquisition workflow |
| Does the 2 m maximum apply to PertAcoustic alone or the entire toolstring? | Governing length/OD envelope and included deployment hardware |
| Which exact CCL model, OD, make-up length and sensing point? | Current public/authorized specifications and datum definitions |
| What connectors and deployment interfaces are actually available? | Mechanical/load, pressure, electrical/power, communications and conveyance requirements |
| What time–depth/reference records can PHE provide? | Relevant deployment trajectories, CCL events, reference logs, datums, corrections and synchronization evidence |
| How should hydrophone position be referenced to the CCL? | Verified sensing coordinates, offset sign, already-applied corrections and allowed uncertainty |

These questions are requests for decisions, not assumptions already accepted by PHE. An incompatibility requiring geometry changes must return to Planner/Reviewer handling before design work. No valve, magnetic CCL sensor, unverified connector or manufacturing detail was added by this assessment.

## 5. Sources and evidence limits

Public manufacturer sources consulted on 11 November 2026:

1. [Baker Hughes — Sondex CCL201 specification](https://dam.bakerhughes.com/m/1a4960ecd80f51df/original/Sondex-casing-collar-locator-CCL-spec.pdf): operating principle, body dimensions, toolbus and sensor-measure-point table; coordinate datum remains unestablished by the sheet.
2. [Welltec — Casing Collar Locator](https://www.welltec.com/products-services/intervention/casing-collar-locator-ccl): configuration-dependent product range, not a selected PHE model.
3. [Weatherford — Geothermal Depth Logger and Encoder](https://www.weatherford.com/drilling-and-evaluation/wireline-products/telemetry-systems/geothermal-depth-logger-and-encoder/): recording time, depth and line speed for later merging with tool records.
4. [Weatherford — Memory Logging Tool](https://www.weatherford.com/drilling-and-evaluation/wireline-products/cased-hole-formation-evaluation/memory-logging-tool/): vendor-specific modular memory logging.
5. Existing [parameters](../results/integrated-downhole/parameters.json), [verification](../results/integrated-downhole/verification.json) and [engineering report](../results/integrated-downhole/design_report.md): PertAcoustic geometry and its limitations.

The 700 mm / ALFA observations come only from the supplied meeting-note summary; no underlying photographs or approved equipment specification were independently inspected. Length arithmetic, coordinate definitions, timing equations and interface risks above are engineering assessment, explicitly conditional on the missing PHE inputs. No field data, acquisition code or physical interoperability validation was produced.
