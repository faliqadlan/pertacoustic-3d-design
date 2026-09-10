# PertAcoustic Biweekly 8 Engineering Progress Report

**Document type:** Evidence-based progress report  
**Status:** Review Required  
**Reporting-period dates:** UNRESOLVED - no authoritative Biweekly 6/7/8 date chain was established in repository evidence.  
**Repository evidence cutoff:** `main@667ccd59cf6657a75dfe3cc2b4c67488737ef028`  
**Governing reporting task:** `.agents/tasks/biweekly-8-report.md @ c1d8d7c00d6fe3b3055bdabebb604f4e49bb86cb`  
**Governing compact-casing task:** `.agents/tasks/compact-downhole-casing-redesign.md @ ad24d9146815f88368d8f6b1d635831d57aed13d`

This report summarizes accepted repository evidence only. It is not a manufacturing drawing, pressure qualification, field qualification, or new engineering source of truth.

## Executive Progress Summary

PertAcoustic progressed from the historical Biweekly 5 large casing / aerogel-oriented concept to a compact no-aerogel screening architecture. The accepted compact-casing evidence now supports a preferred preliminary envelope of **44.45 mm / 1.75 in OD**, **3.50 mm Inconel 718 pressure-shell wall**, and **37.45 mm shell bore**.

The current electronics packaging screen indicates that the nominal PCM1808 transverse envelope plus **1.0 mm per side** requires approximately **34.93 mm** circular diameter. Against the **37.45 mm** bore, the current preliminary diametral packaging margin is approximately **2.52 mm**. This is a screening calculation, not a physical fit validation.

The current architecture is:

| Item | Current Status |
|---|---|
| Pressure shell | Inconel 718 |
| Preferred OD | 44.45 mm / 1.75 in |
| Maximum screening OD | 57.15 mm / 2.25 in |
| Preliminary wall | 3.50 mm |
| Shell bore | 37.45 mm |
| Internal-diameter direction | ID > 30 mm; 30 mm is a lower bound, not the target design ID |
| Internal packaging strategy | Discrete/conformal polymer electronics carrier inside the Inconel shell |
| Aerogel | No longer part of the current baseline architecture |
| PA66-GF30 | PRIMARY NYLON PROTOTYPE / VALIDATION CANDIDATE |
| PEEK | ENGINEERING BENCHMARK / REFERENCE |
| PPA | HIGHER-PERFORMANCE POLYAMIDE ALTERNATIVE / SECONDARY VALIDATION CANDIDATE |

Structural and thermal outputs remain **PRELIMINARY ENGINEERING SCREENING**. Structural status remains **CONDITIONAL - DESIGN PRESSURE UNRESOLVED**. The current thermal result is an **IDEAL SHELL-COUPLED LOWER-BOUND TEMPERATURE (INNER SHELL SURFACE)**, not PCB, cavity, chip-junction, or electronics qualification evidence.

## Work Completed During The Reporting Period

Because authoritative reporting-period dates are unresolved, this section is bounded by the repository evidence cutoff rather than a calendar range.

- Completed compact ID/OD screening across **44.45 mm to 57.15 mm OD** and **3.50 mm / 4.00 mm** shell-wall candidates.
- Selected the smallest viable preliminary screening geometry: **44.45 mm OD / 37.45 mm bore / 3.50 mm wall**.
- Reframed the architecture from radial aerogel insulation toward an **Inconel shell plus discrete/conformal polymer electronics carrier**.
- Preserved the current electronics selection baseline while identifying that measured board, header, connector, wiring, and bend-radius geometry is still required.
- Classified the polymer carrier options: PA66-GF30 for first prototype validation, PEEK as the strongest current benchmark, and PPA as a secondary higher-performance polyamide candidate.
- Recorded structural pressure cases as screening and sensitivity scenarios rather than design-pressure authority.
- Recorded thermal results as inner-shell lower-bound screening and documented the missing internal electronics thermal path.

## Current Engineering Configuration

| Parameter | Value | Evidence Status |
|---|---:|---|
| Preferred casing OD | 44.45 mm / 1.750 in | VERIFIED from accepted compact-casing envelope |
| Maximum casing OD | 57.15 mm / 2.250 in | VERIFIED from governing compact-casing task and accepted envelope |
| Preliminary shell wall | 3.50 mm | DERIVED SCREENING / recommended preliminary configuration |
| Shell bore | 37.45 mm | DERIVED: 44.45 - 2 x 3.50 = 37.45 mm |
| ID direction | > 30.0 mm | VERIFIED as project floor; not a target ID |
| Electronics-required circular envelope | 34.93 mm | DERIVED SCREENING from PCM1808 30 mm x 12 mm transverse envelope plus 1.0 mm per side |
| Packaging diametral margin | 2.52 mm | DERIVED SCREENING: 37.45 - 34.93 = 2.52 mm |
| Total modeled tool length | 656.9 mm | VERIFIED generated compact-casing evidence |
| Thermal exposure screen | 70 C external, 7200 s / 2 h | VERIFIED from governing task and compact-casing evidence |
| Internal heat input | 1.0 W inherited screening case | ASSUMED SCREENING |

The current packaging result means the nominal screening envelope fits inside the shell bore with limited margin. It does not prove that actual purchased PCBs, solder joints, headers, connectors, wire exits, or cable bend radii fit after measurement and assembly.

## Engineering Analysis

### Mechanical Packaging And ID/OD Envelope

The accepted ID/OD envelope supports the **44.45 mm OD / 3.50 mm wall** configuration as the recommended preliminary geometry because it is the smallest screened OD that satisfies the ID floor, current nominal electronics envelope, and 10 MPa screening structural checks.

| OD (mm) | OD (in) | Wall (mm) | ID (mm) | Electronics Required Diameter (mm) | Packaging Margin (mm) | 10 MPa Buckling FoS | Historical 10k psi Buckling FoS | Recommendation |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 44.45 | 1.750 | 3.50 | 37.45 | 34.93 | 2.52 | 11.33 | 1.64 | RECOMMENDED PRELIMINARY CONFIGURATION |
| 44.45 | 1.750 | 4.00 | 36.45 | 34.93 | 1.52 | 16.92 | 2.45 | VIABLE SCREENING ALTERNATIVE |
| 57.15 | 2.250 | 3.50 | 50.15 | 34.93 | 15.22 | 5.33 | 0.77 | VIABLE SCREENING ALTERNATIVE |

The table above is a reporting excerpt. The full accepted matrix is in `results/compact-casing/compact_casing_id_od_envelope.csv`.

### Material And Carrier Selection

The pressure boundary remains the **Inconel 718 shell**. The polymer carrier is an internal support and packaging feature only; it is not a pressure boundary.

| Carrier Material | Current Role | Key Limitation |
|---|---|---|
| PA66-GF30, BASF Ultramid A3WG6 HRX BK23591 | PRIMARY NYLON PROTOTYPE / VALIDATION CANDIDATE | Exact 70 C wet dimensional and mechanical behavior, water swelling, and downhole fluid compatibility remain unresolved |
| Victrex 450G PEEK | ENGINEERING BENCHMARK / REFERENCE | Higher cost class; actual PertAcoustic carrier still requires physical validation |
| Solvay Amodel A-1133 HS PPA | HIGHER-PERFORMANCE POLYAMIDE ALTERNATIVE / SECONDARY VALIDATION CANDIDATE | Procurement and exact carrier validation pending; downhole qualification is not established for the current grade |

PA66-GF30 must not be treated as downhole-qualified. Its manufacturer data supports a screening material definition, but the repository evidence keeps hot/wet dimensional response, water absorption/swelling, long-duration performance, and well-fluid compatibility unresolved.

### Structural Screening

Structural status remains:

```text
CONDITIONAL - DESIGN PRESSURE UNRESOLVED
```

For the recommended **44.45 mm OD / 3.50 mm wall Inconel 718 shell**, accepted screening values are:

| Pressure Case | Correct Classification | Max von Mises Stress | Strength Ratio | Buckling FoS | Reporting Boundary |
|---|---|---:|---:|---:|---|
| ~10 MPa / ~1,450 psi | Screening context | 59.7 MPa | 16.75 | 11.33 | Preliminary screen only |
| 20 MPa / ~2,900 psi | Sensitivity scenario | 119.4 MPa | 8.38 | 5.67 | Preliminary sensitivity only |
| 68.95 MPa / 10,000 psi | Historical comparison | 411.6 MPa | 2.43 | 1.64 | Historical benchmark comparison only |

These factors of safety do not establish pressure qualification. Authoritative field design pressure, collapse criteria, seal pressure retention, fatigue, corrosion, sour-service exposure, and physical pressure testing remain unresolved.

### Thermal Screening

The current accepted thermal result may support statements about shell response and inner-shell lower-bound temperature only:

```text
IDEAL SHELL-COUPLED LOWER-BOUND TEMPERATURE (INNER SHELL SURFACE)
```

For the current no-aerogel compact architecture, the 2-hour / 1 W screening result is **70.00 C** at the inner shell surface. It must not be relabeled as PCB temperature, electronics cavity temperature, STM32 junction temperature, PCM1808 junction temperature, complete electronics temperature, or electronics qualification.

The current result leaves the internal electronics thermal path unresolved. Stronger thermal analysis requires:

```text
environment
-> Inconel shell
-> shell/carrier contact
-> polymer carrier
-> PCB/contact
-> electronics heat sources
```

with measured or justified thermal resistances and representative electronics power dissipation.

### Electronics Packaging

The current **34.93 mm** electronics envelope is provisional. It is derived from the nominal PCM1808 transverse envelope and clearance rule in the accepted compact-casing evidence. Actual hardware measurement is still required for:

- PCM1808 PCB length, width, thickness, component height, headers, connector protrusion, and solder protrusion.
- STM32 board dimensions, headers, component height, and solder protrusion.
- Power, RTC, SD/storage, analog front-end, connector, and wiring transverse envelopes.
- Wiring exits, cable bend radius, strain relief, and assembly sequence.
- Carrier slot dimensions and manufacturing tolerance stack after dry and wet conditioning.

Physical fit validation has not been completed.

### HTI And Acoustic Interface

The HTI-02-DHPC/D interface concept remains provisional. The accepted evidence preserves the nominal **7/16-20 UNF-2A** interface concept, separate pressure-seal area, conductor routing concept, and exposed acoustic sensing head where supported by the local supplier drawing context.

Supplier-controlled datums, engagement length, thread tolerances, seal gland geometry, pressure retention, preamplifier mode, pinout, cable details, and manufacturing dimensions remain unresolved.

## Comparison With Previous Baseline

| Topic | Historical Biweekly 5 Baseline | Current Compact-Casing Evidence |
|---|---|---|
| OD | 200 mm OD thermal-priority concept | 44.45 mm / 1.75 in preferred compact OD |
| Length | 425 mm housing length; historical package report | 656.9 mm modeled compact subassembly span, within 2000 mm maximum |
| Pressure shell | Inconel 718 | Inconel 718 |
| Wall | 35 mm historical screening wall | 3.50 mm preliminary screening wall |
| Internal clear diameter | 41 mm provisional electronics clear ID | 37.45 mm shell bore; 34.93 mm current electronics-required screening envelope |
| Insulation strategy | Aerogel radial layer and axial buffers | No aerogel baseline; internal polymer carrier strategy |
| Thermal environment | 150 C external, 1 hour | 70 C external, 2 hours |
| Thermal result semantics | Cavity-boundary / electronics-zone boundary screening, not chip junction | Inner-shell lower-bound screening, not PCB/cavity/junction/electronics qualification |
| Structural pressure | 10,000 psi historical screening case | ~10 MPa screen, 20 MPa sensitivity, 68.95 MPa historical comparison; design pressure unresolved |

The current work should be read as a change in architecture and evidence basis, not as completion of a finished tool. The large aerogel concept remains historical provenance. The compact architecture is the current preliminary screening direction.

## Verification And Evidence

Evidence inspected for this report:

| Evidence | Use In This Report |
|---|---|
| `results/compact-casing/compact_casing_redesign_report.md` | Current compact architecture, recommended geometry, material hierarchy, structural/thermal language, unresolved items |
| `results/compact-casing/compact_casing_id_od_envelope.csv` | OD/ID, wall, packaging margin, and structural screening table values |
| `results/compact-casing/compact_casing_trade_study.csv` | Architecture comparison, no-aerogel baseline, inner-shell thermal results, total length |
| `cosmo/compact_casing.py` | Constants and generated-evidence semantics for geometry, pressures, electronics envelope, and thermal metric label |
| `tests/test_compact_casing.py` | Verification intent for compact-casing logic and evidence-bound report semantics |
| `results/biweekly-5/biweekly-5.md` | Historical baseline report and figures |
| `results/biweekly-5/summary.json` | Historical geometry, thermal, structural, and limitation values |
| `.agents/context/project.md` | Repository-wide context, evidence hazards, and reporting conventions |
| `.agents/context/biweekly-5/project.md` | Historical Biweekly 5 context and preservation constraints |
| `.agents/tasks/compact-downhole-casing-redesign.md @ ad24d9146815f88368d8f6b1d635831d57aed13d` | Engineering task authority and constraints |
| `.agents/tasks/biweekly-8-report.md @ c1d8d7c00d6fe3b3055bdabebb604f4e49bb86cb` | Reporting task authority and acceptance criteria |

Accepted compact-casing figures available for review, without duplication in this reporting package:

- `results/compact-casing/figures/compact_cad_assembly.png` - accepted compact CAD assembly render.
- `results/compact-casing/figures/compact_transverse_pcm1808_section.png` - accepted transverse PCM1808 screening section.
- `results/compact-casing/figures/compact_longitudinal_section.png` - accepted compact longitudinal section.
- `results/compact-casing/figures/compact_thermal_trade_study.png` - accepted thermal architecture comparison.

No figures were copied into `results/biweekly-8/`; preserving traceable references avoids duplicating generated evidence.

## Current Engineering Decision

For the current evidence cutoff, the reviewable engineering direction is:

1. Continue with the **44.45 mm / 1.75 in OD**, **3.50 mm wall**, **37.45 mm bore** Inconel 718 shell as the recommended preliminary compact screening configuration.
2. Treat **ID > 30 mm** as a lower-bound direction only; do not treat 30 mm as the target ID.
3. Use the **discrete/conformal polymer carrier** as the internal packaging strategy and keep **aerogel outside the current baseline architecture**.
4. Use **PA66-GF30** as the first physical nylon prototype / validation candidate, while retaining **PEEK** as the engineering benchmark and **PPA** as the secondary higher-performance polyamide candidate.
5. Keep structural and thermal conclusions in screening status until design pressure, physical packaging measurements, thermal path data, material conditioning, and interface details are verified.

This section records the accepted evidence direction; it does not create a new engineering decision.

## Unresolved Items / Risks

- Reporting-period chronology/date range is unresolved; this report uses the exact repository evidence cutoff instead.
- Authoritative casing design pressure is unresolved.
- The ~10 MPa case is only a screening context; 20 MPa is a sensitivity case; 68.95 MPa / 10,000 psi is a historical comparison.
- No pressure qualification, field qualification, manufacturing readiness, or seal qualification is established.
- Actual PCM1808, STM32, power, RTC, SD/storage, analog-front-end, connector, header, solder, wiring, and cable-bend dimensions are unmeasured.
- Electronics power dissipation and representative operating modes remain unresolved.
- The current thermal result does not establish PCB, cavity, junction, or complete electronics temperatures.
- PA66-GF30 hot/wet dimensional response at 70 C, water swelling, well-fluid compatibility, sour-service compatibility, long-duration behavior, and prototype sliding fit remain unresolved.
- PPA procurement and exact carrier validation remain unresolved.
- HTI supplier-controlled datums, thread engagement, seal gland geometry, pressure-retention details, preamplifier mode, pinout, and cable/interface details remain unresolved.

## Next Engineering Work

1. Measure the actual purchased electronics stack: board outlines, thicknesses, headers, connectors, solder protrusions, wiring exits, and cable bend radii.
2. Build and inspect a physical carrier/bore coupon to validate assembly sliding clearance, card-guide fit, and tolerance stack.
3. Run PA66-GF30 dry and wet conditioning checks at representative temperatures, including dimensional change and insertion/extraction force.
4. Confirm authoritative design pressure and pressure-test requirements before using structural screening as a design basis.
5. Extend thermal analysis from the inner shell into the shell/carrier/PCB/electronics path using measured or justified thermal resistances and actual power dissipation.
6. Obtain or confirm supplier-controlled HTI interface data before manufacturing-grade interface drawings.
7. Revisit PPA or PEEK if PA66-GF30 fails dimensional, wet, thermal, compatibility, or assembly validation.

## Evidence / Traceability Table

| Requirement | Report Coverage | Evidence |
|---|---|---|
| REQ-RPT8-001 Evidence-bound report | Report uses accepted repository evidence and labels unresolved chronology | This report; `.agents/tasks/biweekly-8-report.md` |
| REQ-RPT8-002 Current configuration reconciliation | Current dimensions, material hierarchy, and architecture summarized with evidence status | `compact_casing_id_od_envelope.csv`; `compact_casing_trade_study.csv`; `compact_casing_redesign_report.md` |
| REQ-RPT8-003 Strict thermal semantics | Thermal result labeled as inner-shell lower-bound only | `compact_casing_redesign_report.md`; `cosmo/compact_casing.py` thermal metric label |
| REQ-RPT8-004 Strict structural semantics | Structural status remains conditional; pressure cases classified separately | `compact_casing_id_od_envelope.csv`; `compact_casing_redesign_report.md` |
| REQ-RPT8-005 Historical preservation | Historical Biweekly 5 is used only as historical comparison | `results/biweekly-5/`; `.agents/context/biweekly-5/project.md` |
| REQ-RPT8-006 Traceable reporting package | Canonical report generated under `results/biweekly-8/` only | `results/biweekly-8/biweekly-8.md` |

