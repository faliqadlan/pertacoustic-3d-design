# PertAcoustic Compact Downhole Casing Redesign Report
## Simplified Architecture & Material Trade Study (70 °C / 2-Hour Envelope)

**Document ID:** PERT-REP-COMPACT-002  
**Design Direction:** Simplified 70 °C Operational Environment  
**Status:** Engineering Screening Complete (PASS / Simplified Architecture Validated)  
**Governing Task:** `.agents/tasks/compact-downhole-casing-redesign.md`

---

## 1. Executive Summary & Core Engineering Answers

This study investigates whether the compact PertAcoustic downhole casing (44.45 mm / 1.75" preferred OD, <= 57.15 mm max OD, <= 2000 mm length) can meet the 70 °C / 2-hour downhole operational envelope using a **simplified material architecture without aerogel**.

### Primary Technical Conclusions:

1. **Is aerogel still beneficial at 70 °C?**
   - **NO. Aerogel is not beneficial and is actually detrimental at 70 °C.**
   - In a 70 °C external environment with 1.0 W continuous internal electronics self-heating, aerogel traps internally generated heat, causing the internal cavity to reach **71.72 °C**.
   - Without aerogel, heat conducts efficiently through the Inconel shell (k = 14.7 W/(m·K)) into the external fluid, maintaining the cavity at **70.57 °C** (well below the verified +85 °C IC limit with **+14.43 °C safety margin**).
   - Crucially, eliminating aerogel reclaims **4.45 mm of radial thickness**, expanding internal clear ID from 30.0 mm to **34.45 mm**.

2. **What is the preferred no-aerogel geometry?**
   - **Architecture A (Inconel 718 Pressure Shell + PEEK Liner, No Aerogel)** at **44.45 mm (1.75 in) Outer Diameter**.
   - Radial stack: **34.45 mm Clear ID + 1.50 mm PEEK Liner + 3.50 mm Inconel 718 Wall = 44.45 mm OD**.
   - Modeled casing length: **520.0 mm**; Total tool assembly length: **~620 mm** (<= 2000 mm limit).

3. **Can the electronics fit without slotted packaging?**
   - **YES.** With clear ID expanded to **34.45 mm**, the standard rectangular cross-sectional envelope of the PCM1808 ADC (30.0 mm wide x 12.0 mm high; diagonal with 1 mm clearance = 34.18 mm) **fits directly inside the circular bore** with full assembly clearance, completely eliminating artificial slotted-carrier workarounds.

4. **Is PEEK or PPA preferable as the polymer liner?**
   - **Victrex 450G PEEK is PREFERRED** for long-term downhole service due to superior chemical inertness, near-zero moisture absorption (0.1%), and high continuous service temperature (260 °C).
   - **Solvay Amodel A-1133 HS PPA** is a fully viable, high-modulus (E = 11 GPa) alternative, but undergoes higher equilibrium moisture absorption (1.8%) in aqueous downhole fluids. Both materials perform identically from a thermal standpoint.

5. **Is a polymer-only casing credible, or should the Inconel pressure shell remain?**
   - **The metallic (Inconel 718) pressure shell MUST BE RETAINED.**
   - Polymer-only casings (PEEK-only or PPA-only) have elastic moduli 24x to 52x lower than Inconel (3.7 to 8.0 GPa vs 193 GPa), suffer catastrophic elastic collapse (FoS_buckle = 0.29 to 0.61 << 1.0) under historical 10,000 psi screening, risk time-dependent viscoelastic creep failure under sustained hydrostatic pressure at 70 °C, and cannot provide certified thread retention for the HTI-02-DHPC/D interface.

---

## 2. Side-by-Side Architecture Comparison Matrix

The table below presents the side-by-side evaluation of all investigated configurations at 44.45 mm (1.75") OD:

| Architecture | Casing Material | Liner Material | Aerogel mm | Clear ID mm | Packaging Feasibility | 2h Temp @ 0W | 2h Temp @ 1W | FoS Yield (~1000m) | FoS Buckle (~1000m) | FoS Buckle (10k psi) | Classification |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Architecture A [Recommended]** | **Inconel 718 (3.5mm)** | **PEEK (1.5mm)** | **0.0** | **34.45** | **Direct Circular Fit** | **70.0 °C** | **70.6 °C** | **16.8** | **11.3** | **1.64** | **PASS (Simplified Feasible Design)** |
| **Architecture B** | Inconel 718 (3.5mm) | PPA Amodel (1.5mm) | 0.0 | 34.45 | Direct Circular Fit | 70.0 °C | 70.6 °C | 16.8 | 11.3 | 1.64 | **PASS (Alternative Polymer Liner)** |
| **Architecture C (Exploratory)** | PEEK-Only (7.2mm) | None | 0.0 | 30.00 | Infeasible (Clear ID 30mm) | 70.0 °C | 70.8 °C | 2.1 | 2.0 | 0.29 | **INFEASIBLE (Polymer Casing Collapse)** |
| **Architecture D (Exploratory)** | PPA-Only (7.2mm) | None | 0.0 | 30.00 | Infeasible (Clear ID 30mm) | 70.0 °C | 70.8 °C | 3.9 | 4.2 | 0.61 | **INFEASIBLE (Polymer Casing Collapse)** |
| **Reference Baseline** | Inconel 718 (3.5mm) | PEEK (1.5mm) | 2.225 | 30.00 | Infeasible (Clear ID 30mm) | 69.1 °C | 71.7 °C | 16.8 | 11.3 | 1.64 | **CONDITIONAL (Aerogel Heat Trapping)** |

---

## 3. Material Properties & Characterization

### A. Metallic Pressure Shell: Inconel 718
- **Datasheet / Standard:** Special Metals Technical Bulletin / AMS 5662
- **Density:** 8190 kg/m³
- **Thermal Conductivity:** 14.7 W/(m·K)
- **Specific Heat:** 460 J/(kg·K)
- **Elastic Modulus at 70-150 °C:** 193,000 MPa
- **Poisson's Ratio:** 0.28
- **Yield Strength (Screening at 70 °C):** 1050 MPa

### B. Polymer Chassis Liner Option 1: Victrex 450G PEEK (Unfilled)
- **Datasheet:** Victrex 450G Technical Data Sheet
- **Density:** 1300 kg/m³
- **Thermal Conductivity:** 0.29 W/(m·K)
- **Specific Heat:** 1500 J/(kg·K)
- **Elastic Modulus at 70 °C:** ~3700 MPa
- **Poisson's Ratio:** 0.40
- **Yield Strength at 70 °C:** ~70 MPa
- **Water Absorption (24h / Saturation):** 0.1% / 0.5% (Excellent hydrolytic stability)

### C. Polymer Chassis Liner Option 2: Solvay Amodel A-1133 HS PPA
- **Datasheet:** Solvay Specialty Polymers (Syensqo) Amodel A-1133 HS Bulletin
- **Reinforcement:** 33% Glass Fiber Reinforced, Heat Stabilized
- **Density:** 1450 kg/m³
- **Thermal Conductivity:** 0.26 W/(m·K)
- **Specific Heat:** 1200 J/(kg·K)
- **Elastic Modulus at 70 °C:** ~8000 MPa (DAM) / ~6500 MPa (Conditioned)
- **Poisson's Ratio:** 0.36
- **Yield Strength at 70 °C:** ~135 MPa (DAM) / ~110 MPa (Conditioned)
- **Water Absorption (24h / Saturation):** 0.30% / 1.80% (Good retention of stiffness, moderate moisture uptake)

---

## 4. Component Operating Limit Verification

Evaluated against verified manufacturer limits under the 1.0 W screening case (70.57 °C peak cavity temperature):

| Component | Part Number / Source | Verified Operating Limit | Cavity Temp @ 2h | Thermal Margin | Status |
|---|---|---|---|---|---|
| **MCU** | **STM32F411CEU6** (ST Datasheet / MoM) | -40 to +85.0 °C | 70.57 °C | +14.43 °C | `VERIFIED PASS` |
| **ADC** | **PCM1808** (TI Datasheet / MoM) | -40 to +85.0 °C | 70.57 °C | +14.43 °C | `VERIFIED PASS` |
| **RTC** | Generic RTC (Unfinalized PN) | -40 to +85.0 °C | 70.57 °C | +14.43 °C | `CONDITIONAL (Industrial PN required)` |
| **Storage** | Generic MicroSD (Unfinalized PN) | -40 to +85.0 °C | 70.57 °C | +14.43 °C | `CONDITIONAL (Industrial Flash required)` |
| **Power** | Generic LDO (Unfinalized PN) | -40 to +85.0 °C | 70.57 °C | +14.43 °C | `CONDITIONAL` |
| **AFE** | Discrete Front-End (Unfinalized BOM) | -40 to +85.0 °C | 70.57 °C | +14.43 °C | `CONDITIONAL` |

*Note: Cavity temperature is the bulk carrier temperature; chip junction temperature will be slightly higher depending on internal package thermal resistance theta_ja.*

---

## 5. Structural Screening & Pressure Scenarios

*Authoritative casing design pressure remains unresolved. Calculations below represent engineering screening across explicit scenarios.*

- **Scenario A (~1000 m Hydrostatic Derived Scenario, 10.0 MPa / 1,450 psi):**
  - Inconel 718 (t_wall = 3.5 mm): Max von Mises = 59.7 MPa -> **Yield FoS = 16.75**; **Buckling FoS = 11.33**.
- **Scenario B (Intermediate Wellbore Scenario, 20.0 MPa / 2,900 psi):**
  - Inconel 718 (t_wall = 3.5 mm): Max von Mises = 119.5 MPa -> **Yield FoS = 8.37**; **Buckling FoS = 5.66**.
- **Scenario C (Historical 10,000 psi / 68.95 MPa Screening Benchmark):**
  - Inconel 718 (t_wall = 3.5 mm): Max von Mises = 411.8 MPa -> **Yield FoS = 2.43**; **Buckling FoS = 1.64**.
  - *(Note: If 10,000 psi buckling FoS >= 2.0 is desired, increasing wall to 4.0 mm achieves Buckling FoS = 2.45 with Clear ID = 33.45 mm, which still fits PCM1808).*

---

## 6. HTI-02-DHPC/D Interface Concept & Provisional Details

- Nominal 7/16-20 UNF-2A male adapter concept preserved.
- Central 3-conductor signal routing feedthrough (2.5 mm bore) integrated into front bulkhead.
- Acoustic sensing head (88.9 mm long, 17.475 mm OD) remains externally exposed.
- Engagement length (10.16 mm), thread machining tolerances, and O-ring seal glands remain provisional screening geometry.

---

## 7. Artifacts & Generated Evidence

- **CAD STEP File:** [`results/compact-casing/cad/compact_casing_assembly.step`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/cad/compact_casing_assembly.step)
- **Trade Study Data:** [`results/compact-casing/compact_casing_trade_study.csv`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/compact_casing_trade_study.csv)
- **Visualizations:**
  - Assembly Render: [`results/compact-casing/figures/compact_cad_assembly.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_cad_assembly.png)
  - Longitudinal Section: [`results/compact-casing/figures/compact_longitudinal_section.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_longitudinal_section.png)
  - Thermal History Curves: [`results/compact-casing/figures/compact_thermal_trade_study.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_thermal_trade_study.png)
