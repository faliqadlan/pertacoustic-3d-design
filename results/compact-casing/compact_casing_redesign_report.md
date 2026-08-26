# PertAcoustic Compact Downhole Casing Redesign Report
## Simplified Architecture & Material Trade Study (70 °C / 2-Hour Envelope)

**Document ID:** PERT-REP-COMPACT-002  
**Design Direction:** Simplified 70 °C Operational Environment (No Aerogel)  
**Status:** Engineering Screening Complete — Review Required  
**Governing Task:** `.agents/tasks/compact-downhole-casing-redesign.md`

---

## 1. Executive Summary & Core Engineering Answers

This study investigates whether the compact PertAcoustic downhole casing (44.45 mm / 1.75" preferred OD, <= 57.15 mm max OD, <= 2000 mm length) can meet the 70 °C / 2-hour downhole operational envelope using a **simplified architecture consisting of an Inconel 718 pressure shell with conformal discrete polymer carrier rails and no aerogel**.

### Primary Technical Conclusions:

1. **Can the selected electronics fit directly inside the preferred 44.45 mm OD casing?**
   - **YES.** Using the nominal PCM1808 ADC cross-sectional envelope (30.0 mm width x 12.0 mm height; effective 32.0 x 14.0 mm bounding envelope with 1.0 mm assembly clearance per side), the minimum circumscribed circular diameter is:
     $$\sqrt{32.0^2 + 14.0^2} = \sqrt{1024 + 196} = \sqrt{1220} \approx 34.93\text{ mm}$$
   - Inside the preferred 44.45 mm OD Inconel 718 casing (3.50 mm screening wall), the **bare shell bore is 37.45 mm**.
   - With **conformal discrete PEEK or PPA carrier chassis**, the carrier outer diameter is sized to **37.05 mm** ($R = 18.525\text{ mm}$), providing **0.200 mm nominal radial slip clearance (0.400 mm diametral)** supported by an explicit differential thermal expansion and tolerance budget.
   - The carrier incorporates integrated card guide channels (grooves) providing $0.8\text{ mm}$ edge capture on each board side without encroaching on the non-retention general component clearance envelope.
   - Conformal carrier geometry leaves **0.00 mm³ prohibited CAD interference** with the Inconel shell, electronics, and buffer plugs.

2. **Does removing aerogel improve the 2-hour thermal behavior under the 70 °C environment?**
   - **YES.** Under the current fixed 70 °C outer-boundary model and 1 W internal-load screening case, the no-aerogel architecture produces a lower 2-hour cavity temperature (**70.00 °C**) than the aerogel reference architecture (**71.72 °C**).
   - In a 70 °C external environment, aerogel acts as an insulating blanket that traps internally generated heat. Without aerogel, heat conducts rapidly through the Inconel shell ($k = 14.7\text{ W/(m·K)}$) into the wellbore fluid.
   - Furthermore, eliminating aerogel reclaims 4.45 mm of radial wall space, enabling direct physical packaging.

3. **Is a discrete PEEK or PPA carrier preferable to a complete cylindrical polymer liner?**
   - **Conformal discrete polymer carrier rails are strongly PREFERRED.**
   - Discrete rails support the electronics along side-guide tracks without taking up radial wall thickness around the entire 360° perimeter, expanding the usable internal diameter from 34.45 mm to 37.45 mm.
   - Between carrier materials:
     - **Victrex 450G PEEK** is the baseline recommendation due to exceptional hydrolytic stability (0.10% 24h moisture absorption) and long-term chemical inertness.
     - **Solvay Amodel A-1133 HS PPA** (33% GF) provides higher stiffness ($E = 11.81\text{ GPa}$ at 70 °C vs 3.7 GPa for PEEK) and lower raw material cost, but exhibits higher equilibrium moisture absorption (1.80%).

4. **Can the preferred 1.75 in (44.45 mm) OD be retained?**
   - **YES.** At 44.45 mm OD with a 3.50 mm Inconel wall, the bare bore is 37.45 mm, providing ample physical space for all modeled electronics. Total modeled tool length is **656.9 mm** (well below the 2000 mm gate limit).

---

## 2. Carrier Tolerance & Differential Thermal Expansion Budget

- **Bore Nominal Diameter:** 37.450 mm (Inconel 718, CLTE = $13.0 \times 10^{-6}\text{ /K}$)
- **Carrier Nominal Diameter:** 37.050 mm (Victrex 450G PEEK, CLTE = $55.0 \times 10^{-6}\text{ /K}$ cross-flow)
- **Assembly Temperature:** 20 °C | **Max Screening Temperature:** 70 °C ($\Delta T = 50\text{ K}$)
- **Cold Assembly Clearance:** **0.400 mm diametral (0.200 mm radial)**
- **Thermal Growth of Inconel Bore:** $+0.0243\text{ mm}$
- **Thermal Growth of PEEK Carrier:** $+0.1019\text{ mm}$
- **Differential Expansion Growth:** $+0.0775\text{ mm}$ diametral ($+0.0388\text{ mm}$ radial)
- **Polymer Conditioning / Uncertainty Allowance (ASSUMED SCREENING ALLOWANCE):** $+0.0200\text{ mm}$ diametral
- **Hot Operating Clearance (70 °C + allowance):** **0.3025 mm diametral (0.1512 mm radial)**
- **Worst-Case Hot Clearance:** **0.3025 mm diametral (0.1512 mm radial)**
- *Conclusion:* **Positive screening clearance remains under the stated thermal, tolerance, and dimensional-allowance assumptions.**

---

## 3. Side-by-Side Architecture Comparison Matrix

Evaluated under 70 °C external boundary and 7200 s (2h) exposure:

| Architecture | Casing Material | Carrier / Liner | Wall mm | Shell Bore ID | Packaging Feasibility | 2h Temp @ 1W | FoS Buckle (10k psi) | Classification |
|---|---|---|---|---|---|---|---|---|
| **Architecture A: Inconel 718 + Discrete PEEK Carrier (3.5 mm Wall)** | Inconel718 | Conformal Rails (PEEK) | 3.50 | 37.45 mm | FEASIBLE | 70.00 °C | 1.64 | RECOMMENDED BASELINE |
| **Architecture A (4.0 mm Wall): Inconel 718 + Discrete PEEK Carrier** | Inconel718 | Conformal Rails (PEEK) | 4.00 | 36.45 mm | FEASIBLE | 70.00 °C | 2.45 | FEASIBLE |
| **Architecture B: Inconel 718 + Discrete PPA Carrier (3.5 mm Wall)** | Inconel718 | Conformal Rails (PPA_Amodel_A1133HS) | 3.50 | 37.45 mm | FEASIBLE | 70.00 °C | 1.64 | FEASIBLE |
| **Architecture C: Inconel 718 + Full PEEK Liner (3.5 mm Wall)** | Inconel718 | Full Liner (PEEK) | 3.50 | 37.45 mm | INFEASIBLE | 70.09 °C | 1.64 | INFEASIBLE |
| **Architecture D: Inconel 718 + Full PPA Liner (3.5 mm Wall)** | Inconel718 | Full Liner (PPA_Amodel_A1133HS) | 3.50 | 37.45 mm | INFEASIBLE | 70.10 °C | 1.64 | INFEASIBLE |
| **Reference Baseline (Arch E): Inconel 718 + Aerogel + PEEK** | Inconel718 | Full Liner (PEEK) | 3.50 | 37.45 mm | INFEASIBLE | 71.72 °C | 1.64 | INFEASIBLE |
| **Architecture F: PEEK-Only Pressure Casing (Exploratory)** | PEEK | None (PEEK) | 7.22 | 30.00 mm | INFEASIBLE | 70.41 °C | 0.29 | EXPLORATORY |
| **Architecture G: PPA-Only Pressure Casing (Exploratory)** | PPA_Amodel_A1133HS | None (PPA_Amodel_A1133HS) | 7.22 | 30.00 mm | INFEASIBLE | 70.46 °C | 0.93 | EXPLORATORY |
| **Architecture A: Inconel 718 + Discrete PEEK (OD 47.62 mm)** | Inconel718 | Conformal Rails (PEEK) | 3.50 | 40.62 mm | FEASIBLE | 70.00 °C | 1.34 | FEASIBLE |
| **Architecture A: Inconel 718 + Discrete PEEK (OD 50.80 mm)** | Inconel718 | Conformal Rails (PEEK) | 3.50 | 43.80 mm | FEASIBLE | 70.00 °C | 1.10 | FEASIBLE |
| **Architecture A: Inconel 718 + Discrete PEEK (OD 53.98 mm)** | Inconel718 | Conformal Rails (PEEK) | 3.50 | 46.98 mm | FEASIBLE | 70.00 °C | 0.92 | FEASIBLE |
| **Architecture A: Inconel 718 + Discrete PEEK (OD 57.15 mm)** | Inconel718 | Conformal Rails (PEEK) | 3.50 | 50.15 mm | FEASIBLE | 70.00 °C | 0.77 | FEASIBLE |

---

## 4. Material Properties & Component Limits Breakdown

### Active Material Database Properties:
| Material | Density | Thermal Conductivity | Specific Heat | Elastic Modulus | Strength Basis & Value | Thermal Expansion | Provenance Notes |
|---|---|---|---|---|---|---|---|
| **Inconel718** | Density: 8190 kg/m³ | k: 14.7 W/(m·K) | Cp: 460 J/(kg·K) | E (70/150C): 193000 MPa | Strength: 1000 MPa | CLTE: 13.0 ppm/K | Screening values near 150 C. Actual strength depends on product form, heat treatment condition, and supplier specification. |
| **PEEK** | Density: 1300 kg/m³ | k: 0.29 W/(m·K) | Cp: 1500 J/(kg·K) | E (70/150C): 3700 MPa | Strength: 70 MPa | CLTE: 55.0 ppm/K | Victrex 450G unfilled PEEK. Room-temperature and thermal expansion properties from manufacturer technical datasheets. Properties at 70 C derived from published ISO 527/DMA curves. |
| **Aerogel** | Density: 200 kg/m³ | k: 0.024 W/(m·K) | Cp: 1000 J/(kg·K) | E (70/150C): N/A MPa | Strength: N/A MPa | CLTE: N/A | Pyrogel HPS nominal density and conductivity at 100 C mean temperature. Specific heat remains an explicit screening assumption. |
| **PPA_Amodel_A1133HS** | Density: 1480 kg/m³ | k: 0.26 W/(m·K) | Cp: 1200 J/(kg·K) | E (70/150C): 11813 MPa | Strength: 181 MPa | CLTE: 55.0 ppm/K | Solvay (Syensqo) Amodel A-1133 HS (33% Glass Fiber Reinforced PPA, Heat Stabilized). Modulus and strength at 70 C derived by exact linear interpolation between 23 C DAM and 100 C DAM Solvay Technical Design Guide datapoints. Note: A-1133 HS is the standard heat-stabilized grade; AS-1133 HS designates structural lubricated grades. |

### Thermal Model Boundaries:
- External Boundary: 70.0 °C constant Dirichlet
- Initial Temperature: 25.0 °C uniform
- Duration: 7200 s (2.0 hours)
- Internal Dissipation Cases: 0.0 W (pure ingress: **70.00 °C**) & 1.0 W (inherited load: **70.00 °C**)

*Important Thermal Distinction:*
Cavity/environmental screening remains below the documented operating-temperature upper bound; actual device junction temperature is not established by this model.

### Component Operating Limit Verification (Architecture A: Inconel 718 + Discrete PEEK Carrier (3.5 mm Wall)):
| Component | Verified Operating Limit | 2h Cavity Temp | Verified Status | Margin | Notes |
|---|---|---|---|---|---|
| **STM32F411CEU6** | 85.0 °C | 70.00 °C | `VERIFIED` | +15.0 °C | Standard Industrial Range |
| **PCM1808** | 85.0 °C | 70.00 °C | `VERIFIED` | +15.0 °C | Standard Industrial Range |
| **RTC Module (Unspecified PN)** | UNSPECIFIED | 70.00 °C | `CONDITIONAL / UNVERIFIED` | N/A (Unspecified Part Rating) | Industrial-rated IC required in BOM |
| **MicroSD Storage (Unspecified PN)** | UNSPECIFIED | 70.00 °C | `CONDITIONAL / UNVERIFIED` | N/A (Unspecified Part Rating) | Industrial flash required in BOM |
| **Power Management (Unspecified PN)** | UNSPECIFIED | 70.00 °C | `CONDITIONAL / UNVERIFIED` | N/A (Unspecified Part Rating) | Discrete thermal dissipation budget required |
| **AFE Electronics (Unspecified PN)** | UNSPECIFIED | 70.00 °C | `CONDITIONAL / UNVERIFIED` | N/A (Unspecified Part Rating) | Requires thermal rating verification |

---

## 5. Structural Screening Across Pressure Scenarios

*Authoritative casing design pressure remains unresolved. The results below represent preliminary engineering screening calculations.*

### Pressure Scenarios Evaluated (Architecture A: Inconel 718 + Discrete PEEK Carrier (3.5 mm Wall)):

1. **Scenario A (~10 MPa / 1,450 psi - ~1000 m Hydrostatic Derived Screening Context):**
   - Max von Mises Stress: **59.7 MPa**
   - Strength Basis: `YIELD` (1000 MPa allowable)
   - Strength Screening Ratio: **16.75**
   - Elastic Buckling Safety Factor: **11.33** ($P_{cr} = 113.3\text{ MPa}$)
   - Status: `SCREENING MARGIN (High Margin at 10 MPa)`

2. **Scenario B (20 MPa / 2,900 psi - Intermediate Wellbore Sensitivity):**
   - Max von Mises Stress: **119.4 MPa**
   - Strength Screening Ratio: **8.38**
   - Elastic Buckling Safety Factor: **5.67**
   - Status: `SCREENING MARGIN (High Margin at 20 MPa)`

3. **Scenario C (68.95 MPa / 10,000 psi - Historical Biweekly 5 Screening Benchmark):**
   - Max von Mises Stress: **411.6 MPa**
   - Strength Screening Ratio: **2.43**
   - Elastic Buckling Safety Factor: **1.64**
   - Status: `CONDITIONAL (Buckling FoS < 2.0 reference at 10k psi; 4.0mm wall achieves FoS=2.45 if required)`

---

## 6. CAD Assembly Collision & Interference Analysis

Automated Boolean intersection checks confirmed **zero prohibited interference (0.00 mm³)** across all assembly components with fail-closed kernel checking:
- **Carrier vs Inconel Shell:** 0.000000 mm³ (Carrier outer radius $R = 18.525\text{ mm} < 18.725\text{ mm}$ shell bore radius)
- **Carrier vs Non-Retention General PCM1808 Envelope:** 0.000000 mm³
- **Nominal Electronics vs Inconel Shell:** 0.000000 mm³
- **Nominal Electronics vs Buffer Plugs:** 0.000000 mm³
- **Intentional PCB Retention Interface:** Card guide slots ($0.8\text{ mm}$ edge capture at $X = \pm 14.2$ to $\pm 15.0\text{ mm}$).

---

## 7. HTI-02-DHPC/D Interface Concept & Provisional Details

- **Interface Thread:** Nominal 7/16-20 UNF-2A male adapter concept integrated into front bulkhead.
- **Signal Feedthrough:** Central 3-conductor signal feedthrough bore (2.5 mm diameter).
- **Acoustic Exposure:** External acoustic sensing head (88.9 mm length, 17.475 mm OD) remains exposed to fluid.
- **Total Modeled Tool Length:** **656.9 mm** (Sensor Head 88.9 mm + Bulkhead 40.0 mm + Housing 500.0 mm + Endcap 8.0 mm).
- **Provisional Status:** Thread engagement length (10.16 mm), machining tolerances, O-ring gland dimensions, and pressure-retention calculations remain provisional screening concepts pending supplier-controlled drawings from High Tech, Inc.

---

## 8. Artifacts & Generated Evidence

- **CAD STEP Model:** [`results/compact-casing/cad/compact_casing_assembly.step`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/cad/compact_casing_assembly.step)
- **Trade Study Dataset:** [`results/compact-casing/compact_casing_trade_study.csv`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/compact_casing_trade_study.csv)
- **Visualizations:**
  - 3D CAD Assembly Render: [`results/compact-casing/figures/compact_cad_assembly.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_cad_assembly.png)
  - Transverse Cross-Section (Conformal Clearance & Card Guides): [`results/compact-casing/figures/compact_transverse_pcm1808_section.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_transverse_pcm1808_section.png)
  - Longitudinal Section: [`results/compact-casing/figures/compact_longitudinal_section.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_longitudinal_section.png)
  - Thermal History & Comparison: [`results/compact-casing/figures/compact_thermal_trade_study.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_thermal_trade_study.png)
