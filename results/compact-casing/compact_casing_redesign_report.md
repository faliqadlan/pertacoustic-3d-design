# PertAcoustic Compact Downhole Casing Redesign Report
## Simplified Architecture & Material Trade Study (70 °C / 2-Hour Envelope)

**Document ID:** PERT-REP-COMPACT-002  
**Design Direction:** Simplified 70 °C Operational Environment  
**Status:** Engineering Screening Complete — Review Required  
**Governing Task:** `.agents/tasks/compact-downhole-casing-redesign.md` @ `ad24d9146815f88368d8f6b1d635831d57aed13d`

---

## 1. Executive Summary & Core Engineering Answers

This study investigates whether the compact PertAcoustic downhole casing (44.45 mm / 1.75" preferred OD, <= 57.15 mm max OD, <= 2000 mm length) can meet the 70 °C / 2-hour downhole operational envelope using a **simplified architecture consisting of an Inconel 718 pressure shell with conformal discrete polymer carrier rails and no aerogel**.

### Primary Technical Conclusions:

1. **Can the selected electronics fit directly inside the preferred 44.45 mm OD casing?**
   - **YES.** Using the nominal PCM1808 ADC cross-sectional envelope (30.0 mm width x 12.0 mm height; effective 32.0 x 14.0 mm bounding envelope with 1.0 mm assembly clearance per side), the minimum circumscribed circular diameter is:
     $$\sqrt{32.0^2 + 14.0^2} = \sqrt{1024 + 196} = \sqrt{1220} \approx 34.93\text{ mm}$$
   - Inside the preferred 44.45 mm OD Inconel 718 casing (3.50 mm screening wall), the **bare shell bore is 37.45 mm**.
   - With **conformal discrete PEEK or PPA carrier rails**, the 34.93 mm enclosing diagonal fits directly inside the 37.45 mm shell bore with **+2.52 mm diameter clearance margin (+1.26 mm radial clearance)**.
   - Conformal rails curve along radius $R \le 18.70\text{ mm}$ strictly inside the shell bore, leaving **0.00 mm³ prohibited CAD interference** with both the Inconel shell and the reserved 32.0 x 14.0 mm PCM1808 envelope.
   - *Screening fit based on nominal board envelope; actual PCB component-level verification is required upon physical hardware receipt.*

2. **Does removing aerogel improve the 2-hour thermal behavior under the 70 °C environment?**
   - **YES.** Under the current fixed 70 °C outer-boundary model and 1 W internal-load screening case, the no-aerogel architecture produces a lower 2-hour cavity temperature (**70.57 °C**) than the aerogel reference architecture (**71.72 °C**).
   - In a 70 °C external environment, aerogel acts as an insulating blanket that traps internally generated heat. Without aerogel, heat conducts rapidly through the Inconel shell ($k = 14.7\text{ W/(m·K)}$) into the wellbore fluid.
   - Furthermore, eliminating aerogel reclaims 4.45 mm of radial wall space, enabling direct physical packaging.

3. **Is a discrete PEEK or PPA carrier preferable to a complete cylindrical polymer liner?**
   - **Conformal discrete polymer carrier rails are strongly PREFERRED.**
   - Discrete rails support the electronics along side-guide tracks without taking up radial wall thickness around the entire 360° perimeter, expanding the usable internal diagonal from 34.45 mm to 37.45 mm.
   - Between carrier materials:
     - **Victrex 450G PEEK** is the baseline recommendation due to exceptional hydrolytic stability (0.10% 24h moisture absorption) and long-term chemical inertness.
     - **Solvay Amodel A-1133 HS PPA** (33% GF) provides higher stiffness ($E = 8.25\text{ GPa}$ at 70 °C vs 3.7 GPa for PEEK) and lower raw material cost, but exhibits higher equilibrium moisture absorption (1.80%).

4. **Can the preferred 1.75 in (44.45 mm) OD be retained?**
   - **YES.** At 44.45 mm OD with a 3.5 mm Inconel wall, the bare bore is 37.45 mm, providing ample physical space for all modeled electronics. Tool length is ~620 mm total (<= 2000 mm limit).

5. **What are the limitations of polymer-only PEEK/PPA pressure-body concepts?**
   - **Inconel 718 remains the recommended pressure-shell baseline under current evidence.**
   - Polymer-only pressure housings remain **exploratory pending authoritative pressure, creep-duration, hydrothermal conditioning, and collapse requirements**.
   - Under historical 10,000 psi screening, polymer casings suffer catastrophic elastic collapse (PEEK buckling FoS = 0.29; PPA buckling FoS = 0.61). Even at ~10 MPa screening, viscoelastic creep and thread sealing reliability present unresolved long-term risks.

6. **What remains conditional?**
   - Authoritative field casing design pressure remains unresolved.
   - Component BOM operating ratings for unspecified parts (RTC, MicroSD, Power, AFE) remain conditional.
   - HTI supplier-controlled engagement length, O-ring gland geometry, and thread tolerances remain provisional.

---

## 2. Side-by-Side Architecture Comparison Matrix

Evaluated at 44.45 mm (1.75") Outer Diameter under 70 °C external boundary and 7200 s (2h) exposure:

| Architecture | Casing Material | Carrier / Liner | Full Liner mm | Aerogel mm | Shell Bore ID | Packaging Status | 2h Temp @ 0W | 2h Temp @ 1W | FoS Yield (~10MPa) | FoS Buckle (~10MPa) | FoS Buckle (10k psi) | Classification |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Architecture A [Recommended Baseline]** | **Inconel 718 (3.5mm)** | **Conformal PEEK Rails** | **0.0** | **0.0** | **37.45 mm** | **Direct Fit (+1.26mm margin)** | **70.0 °C** | **70.6 °C** | **16.8** | **11.3** | **1.64** | **FEASIBLE SCREENING CANDIDATE** |
| **Architecture B [Alternative]** | Inconel 718 (3.5mm) | Conformal PPA Rails | 0.0 | 0.0 | 37.45 mm | Direct Fit (+1.26mm margin) | 70.0 °C | 70.6 °C | 16.8 | 11.3 | 1.64 | **FEASIBLE SCREENING CANDIDATE** |
| **Architecture C** | Inconel 718 (3.5mm) | Full PEEK Liner (1.5mm) | 1.5 | 0.0 | 37.45 mm | Infeasible (Clear ID 34.45mm) | 70.0 °C | 70.6 °C | 16.8 | 11.3 | 1.64 | **INFEASIBLE (Liner Corner Clashing)** |
| **Architecture D** | Inconel 718 (3.5mm) | Full PPA Liner (1.5mm) | 1.5 | 0.0 | 37.45 mm | Infeasible (Clear ID 34.45mm) | 70.0 °C | 70.6 °C | 16.8 | 11.3 | 1.64 | **INFEASIBLE (Liner Corner Clashing)** |
| **Reference Baseline (Arch E)** | Inconel 718 (3.5mm) | Aerogel + PEEK Liner | 1.5 | 2.225 | 37.45 mm | Infeasible (Clear ID 30.00mm) | 69.1 °C | 71.7 °C | 16.8 | 11.3 | 1.64 | **CONDITIONAL (Aerogel Heat Trapping)** |
| **Architecture F (Exploratory)** | PEEK-Only (7.2mm) | Integral Polymer Body | 0.0 | 0.0 | 30.00 mm | Infeasible (Clear ID 30.00mm) | 70.0 °C | 70.8 °C | 2.4 | 2.0 | 0.29 | **EXPLORATORY / CONDITIONAL** |
| **Architecture G (Exploratory)** | PPA-Only (7.2mm) | Integral Polymer Body | 0.0 | 0.0 | 30.00 mm | Infeasible (Clear ID 30.00mm) | 70.0 °C | 70.8 °C | 4.6 | 4.3 | 0.61 | **EXPLORATORY / CONDITIONAL** |

---

## 3. Material Properties & Provenance Breakdown

| Material | Property | Value | Unit | Provenance Classification & Source Notes |
|---|---|---|---|---|
| **Inconel 718** | Density | 8190 | kg/m³ | `VERIFIED MANUFACTURER VALUE` (Special Metals bulletin) |
| | Conductivity | 14.7 | W/(m·K) | `VERIFIED MANUFACTURER VALUE` (Special Metals bulletin) |
| | Specific Heat | 460 | J/(kg·K) | `VERIFIED MANUFACTURER VALUE` (Special Metals bulletin) |
| | Modulus @ 150 °C | 193,000 | MPa | `VERIFIED MANUFACTURER VALUE` (Special Metals bulletin) |
| | Poisson's Ratio | 0.28 | - | `VERIFIED MANUFACTURER VALUE` |
| | Yield Strength @ 70-150 °C | 1000 | MPa | `ASSUMED SCREENING VALUE` (Subject to AMS 5662 heat treatment & product form) |
| **Victrex 450G PEEK** | Density | 1300 | kg/m³ | `VERIFIED MANUFACTURER VALUE` (Victrex 450G TDS) |
| | Conductivity | 0.29 | W/(m·K) | `VERIFIED MANUFACTURER VALUE` (Victrex 450G TDS) |
| | Specific Heat | 1500 | J/(kg·K) | `VERIFIED MANUFACTURER VALUE` (Victrex 450G TDS) |
| | Modulus @ 70 °C | 3700 | MPa | `DERIVED / INTERPOLATED SCREENING VALUE` (DMA / ISO 527 curve at 70 °C) |
| | Yield Strength @ 70 °C | 70 | MPa | `DERIVED / INTERPOLATED SCREENING VALUE` (Tensile curve at 70 °C) |
| | Poisson's Ratio | 0.40 | - | `ASSUMED SCREENING VALUE` |
| | Water Absorption (24h / Sat) | 0.10 / 0.50 | % | `VERIFIED MANUFACTURER VALUE` (ASTM D570) |
| **Amodel A-1133 HS PPA** | Density | 1450 | kg/m³ | `VERIFIED MANUFACTURER VALUE` (ISO 1183, Solvay technical bulletin) |
| | Conductivity | 0.26 | W/(m·K) | `VERIFIED MANUFACTURER VALUE` (ASTM C177) |
| | Specific Heat | 1200 | J/(kg·K) | `ASSUMED SCREENING VALUE` (Typical for 33% GF PPA) |
| | Modulus @ 23 °C (DAM) | 11,000 | MPa | `VERIFIED MANUFACTURER VALUE` (DAM ISO 527-2: 11000 MPa) |
| | Modulus @ 70 °C | 8253 | MPa | `DERIVED / INTERPOLATED SCREENING VALUE` (Linear interpolation: $11000 - \frac4777(11000-6500) = 8253.25\text{ MPa}$) |
| | Tensile Strength @ 70 °C | 143 | MPa | `DERIVED / INTERPOLATED SCREENING VALUE` (Tensile stress at break: $195 - \frac4777(195-110) = 143.12\text{ MPa}$) |
| | Poisson's Ratio | 0.36 | - | `ASSUMED SCREENING VALUE` |
| | Water Absorption (24h / Sat) | 0.30 / 1.80 | % | `VERIFIED MANUFACTURER VALUE` (ASTM D570 equilibrium) |

---

## 4. Thermal Screening & Operating Limit Verification

**Thermal Model Boundaries:**
- External Boundary: 70.0 °C constant Dirichlet
- Initial Temperature: 25.0 °C uniform
- Duration: 7200 s (2.0 hours)
- Internal Dissipation Cases: 0.0 W (pure ingress) & 1.0 W (inherited screening baseline)

**Modeled 2-Hour Cavity Temperature (Architecture A):** **70.57 °C**

*Important Thermal Distinction:*
Cavity/environmental screening remains below the documented operating-temperature upper bound; actual device junction temperature is not established by this model.

### Component Operating Limit Verification:

| Component | Part Number / Reference | Verified Operating Limit | 2h Cavity Temp | Verified Status | Margin / Notes |
|---|---|---|---|---|---|
| **MCU** | **STM32F411CEU6** | -40.0 to +85.0 °C | 70.57 °C | `WITHIN BOUND` | +14.43 °C screening margin below +85 °C datasheet bound |
| **ADC** | **PCM1808** | -40.0 to +85.0 °C | 70.57 °C | `WITHIN BOUND` | +14.43 °C screening margin below +85 °C datasheet bound |
| **RTC** | Generic RTC Module | UNSPECIFIED | 70.57 °C | `CONDITIONAL / UNVERIFIED` | N/A (Unspecified Part Rating; Industrial-rated IC required in BOM) |
| **Storage** | Generic MicroSD Card | UNSPECIFIED | 70.57 °C | `CONDITIONAL / UNVERIFIED` | N/A (Unspecified Part Rating; Industrial flash required in BOM) |
| **Power** | Generic LDO / Regulator | UNSPECIFIED | 70.57 °C | `CONDITIONAL / UNVERIFIED` | N/A (Unspecified Part Rating; thermal dissipation budget required) |
| **AFE** | Discrete Front-End | UNSPECIFIED | 70.57 °C | `CONDITIONAL / UNVERIFIED` | N/A (Unspecified discrete passive/op-amp BOM selection) |

---

## 5. Structural Screening Across Pressure Scenarios

*Authoritative casing design pressure remains unresolved. The results below represent preliminary engineering screening calculations.*

### Pressure Scenarios Evaluated (Inconel 718, OD 44.45 mm, Wall 3.50 mm):

1. **Scenario A (~10 MPa / 1,450 psi - ~1000 m Hydrostatic Derived Scenario):**
   - Max von Mises Stress: **59.7 MPa**
   - Yield Safety Factor: **16.75** (vs 1000 MPa yield screening value)
   - Elastic Buckling Safety Factor: **11.33** ($P_{cr} = 113.3\text{ MPa}$)
   - Classification: `SCREENING MARGIN (High Margin at 10 MPa)`

2. **Scenario B (20 MPa / 2,900 psi - Intermediate Wellbore Sensitivity):**
   - Max von Mises Stress: **119.5 MPa**
   - Yield Safety Factor: **8.37**
   - Elastic Buckling Safety Factor: **5.66**
   - Classification: `SCREENING MARGIN (High Margin at 20 MPa)`

3. **Scenario C (68.95 MPa / 10,000 psi - Historical Biweekly 5 Benchmark):**
   - Max von Mises Stress: **411.8 MPa**
   - Yield Safety Factor: **2.43**
   - Elastic Buckling Safety Factor: **1.64**
   - Classification: `CONDITIONAL (Buckling FoS < 2.0 reference at 10k psi; 4.0mm wall achieves FoS=2.45 if required)`

---

## 6. CAD Assembly Collision & Interference Analysis

Automated Boolean intersection checks confirmed **zero prohibited interference (0.00 mm³)** across all assembly components:
- **Carrier vs Inconel Shell:** $0.00\text{ mm}^3$ (Carrier outer radius $R = 18.70\text{ mm} < 18.725\text{ mm}$ shell bore radius)
- **Carrier vs Reserved PCM1808 Clearance Envelope (32x14 mm):** $0.00\text{ mm}^3$
- **Carrier vs Nominal PCM1808 PCB (30x12 mm):** $0.00\text{ mm}^3$
- **Nominal Electronics vs Inconel Shell:** $0.00\text{ mm}^3$
- **Nominal Electronics vs Buffer Plugs:** $0.00\text{ mm}^3$

---

## 7. HTI-02-DHPC/D Interface Concept & Provisional Details

- **Interface Thread:** Nominal 7/16-20 UNF-2A male adapter concept integrated into front bulkhead.
- **Signal Feedthrough:** Central 3-conductor signal feedthrough bore (2.5 mm diameter).
- **Acoustic Exposure:** External acoustic sensing head (88.9 mm length, 17.475 mm OD) remains exposed to fluid.
- **Provisional Status:** Thread engagement length (10.16 mm), machining tolerances, O-ring gland dimensions, and pressure-retention calculations remain provisional screening concepts pending supplier-controlled drawings from High Tech, Inc.

---

## 8. Artifacts & Generated Evidence

- **CAD STEP Model:** [`results/compact-casing/cad/compact_casing_assembly.step`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/cad/compact_casing_assembly.step)
- **Trade Study Dataset:** [`results/compact-casing/compact_casing_trade_study.csv`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/compact_casing_trade_study.csv)
- **Visualizations:**
  - 3D CAD Assembly Render: [`results/compact-casing/figures/compact_cad_assembly.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_cad_assembly.png)
  - Transverse Cross-Section (Conformal Clearance): [`results/compact-casing/figures/compact_transverse_pcm1808_section.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_transverse_pcm1808_section.png)
  - Longitudinal Section: [`results/compact-casing/figures/compact_longitudinal_section.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_longitudinal_section.png)
  - Thermal History & Comparison: [`results/compact-casing/figures/compact_thermal_trade_study.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_thermal_trade_study.png)
