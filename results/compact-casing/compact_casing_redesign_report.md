# PertAcoustic Compact Downhole Casing Redesign Report
## Simplified Architecture & Polymer Carrier Material Trade Study (70 °C / 2-Hour Envelope)

**Document ID:** PERT-REP-COMPACT-002  
**Design Direction:** Simplified 70 °C Operational Environment (Inconel 718 + Conformal Polymer Carrier + No Aerogel)  
**Status:** Engineering Screening Complete — Review Required  
**Governing Task:** `.agents/tasks/compact-downhole-casing-redesign.md`

---

## 1. Executive Summary & Direct Engineering Answers

This engineering screening trade study evaluates whether alternative polymer materials can reduce carrier cost while retaining the accepted mechanical architecture:
- **44.45 mm / 1.75 in OD**
- **Inconel 718 metallic pressure shell**
- **3.50 mm preliminary packaging-favorable screening wall**
- **37.45 mm shell bore**
- **Conformal polymer electronics carrier with integrated card guides**
- **No aerogel insulation**
- **Total modeled tool length: 656.9 mm** (CAD Bounding Span: **656.9 mm**)

### Direct Answers to Required Engineering Questions:

1. **"Can we replace the PEEK electronics carrier with a lower-cost nylon-based material for the current 70 °C / 2-hour PertAcoustic downhole tool?"**
   - **For PPA-GF (Solvay Amodel A-1133 HS, 33% GF):**  
     **PREFERRED HIGH-PERFORMANCE COST-REDUCTION CANDIDATE (procurement and exact carrier qualification pending).**  
     PPA provides superior stiffness ($E = 11.81\text{ GPa}$ at 70 °C DAM vs 3.70 GPa for PEEK), moderate moisture absorption (0.20% 24h, 1.80% sat), high glass transition temperature ($T_g \approx 125\text{--}135\text{ °C}$), and is an expected lower-cost candidate compared to PEEK. Note that published downhole qualification evidence often cites structural lubricated AS-1133 HS rather than standard A-1133 HS.
   - **For PA66-GF30 (BASF Ultramid A3WG6 HRX BK23591):**  
     **PROTOTYPE / VALIDATION CANDIDATE (exact 70 °C wet properties and downhole-fluid compatibility unresolved).**  
     While Ultramid A3WG6 HRX offers expected lower material cost and excellent injection moldability with automotive-grade hydrolysis resistance, its **high water absorption (1.5–1.9% equilibrium at 50% RH, 5.6–6.3% saturation in water)** creates substantial dimensional swelling risk in tight sliding bores ($0.200\text{ mm}$ nominal radial clearance). Moisture conditioning substantially reduces 23 °C modulus and stress at break; exact 70 °C conditioned mechanical behavior remains unresolved. Compatibility with hot wellbore completion brines, crude hydrocarbons, and sour gas remains unestablished. Therefore, PA66-GF30 is classified as a prototype/validation candidate only.

2. **"Which material should we manufacture for the first physical carrier prototype?"**
   - **For Downhole Qualification / Primary Functional Tool Baseline:**  
     **Victrex 450G PEEK** provides the **STRONGEST CURRENT MATERIAL EVIDENCE** and remains the **RECOMMENDED CARRIER BASELINE** (actual PertAcoustic carrier still requires physical validation).
   - **For Low-Cost Benchtop / Assembly / Fit Verification Prototype:**  
     **BASF Ultramid A3WG6 HRX PA66-GF30** (or Solvay Amodel A-1133 HS PPA) can be injection molded or CNC-machined from exact-grade molded stock/coupons to verify circuit card retention, connector harness routing, and sliding fit in an Inconel coupon under dry laboratory conditions (note: additive manufacturing / 3D printing is unsupported for the exact A3WG6 HRX granule grade).

---

## 2. Exact PA66-GF30 Screening Material Definition (BASF Ultramid A3WG6 HRX)

The candidate nylon material is based strictly on the official manufacturer datasheet for **BASF Ultramid A3WG6 HRX BK23591**:

- **Grade:** BASF Ultramid A3WG6 HRX BK23591
- **Polymer Family & Reinforcement:** PA66-GF30 (Polyamide 66 reinforced with 30% standard glass fibers)
- **Manufacturer:** BASF Performance Polymers
- **Density:** $1370\text{ kg/m³}$ (ISO 1183)
- **Thermal Conductivity:** $0.36\text{ W/(m·K)}$ (Datasheet)
- **Specific Heat Capacity:** $1260\text{ J/(kg·K)}$ (Datasheet)
- **Melting Temperature:** $260\text{ °C}$ (ISO 11357)
- **Heat Deflection Temperature:** HDT/A (1.80 MPa) = $245\text{ °C}$; HDT/B (0.45 MPa) = $260\text{ °C}$ (ISO 75-2)
- **Moisture Absorption (Equilibrium, 23 °C / 50% RH):** **1.5 – 1.9 %** (ISO 62)
- **Water Absorption (Saturation in water, 23 °C):** **5.6 – 6.3 %** (ISO 62)
- **Tensile Modulus (23 °C, ISO 527-2):**
  - **Dry (DAM):** $9500\text{ MPa}$ ($9.5\text{ GPa}$)
  - **Conditioned (Moisture-Equilibrated):** $6000\text{ MPa}$ ($6.0\text{ GPa}$) ($-36.8\%\text{ reduction}$)
- **Tensile Stress at Break (23 °C, ISO 527-2):**
  - **Dry (DAM):** $185\text{ MPa}$
  - **Conditioned:** $110\text{ MPa}$ ($-40.5\%\text{ reduction}$)
  - **Strength Basis:** `TENSILE_STRESS_AT_BREAK_SCREENING` (Glass-reinforced polyamides exhibit brittle failure without ductile yield)
- **Tensile Strain at Break (23 °C):** Dry = $3.7\%$; Conditioned = $7.2\%$
- **Flexural Modulus (23 °C, ISO 178):** Dry = $9200\text{ MPa}$; Conditioned = $5800\text{ MPa}$
- **Tensile Creep Modulus (1000 h, strain $\le 0.5\%$, 23 °C, Conditioned, ISO 899-1):** $4800\text{ MPa}$
- **Coefficient of Linear Thermal Expansion (CLTE, ISO 11359-2):**
  - Along flow: $30\times 10^{-6}\text{ /K}$ ($30\text{ ppm/K}$)
  - Cross-flow: $70\times 10^{-6}\text{ /K}$ ($70\text{ ppm/K}$)
- **Electrical Properties (IEC 62631, BASF Feb 2026 Product Information):**
  - Volume Resistivity: $8\times 10^{10}\text{ }\Omega\cdot\text{m}$ (published table has incomplete dry/conditioned breakdown; separate dry/conditioned values UNAVAILABLE / NOT PUBLISHED)
  - Surface Resistivity: $8\times 10^{12}\text{ }\Omega$ (published table has incomplete dry/conditioned breakdown; separate dry/conditioned values UNAVAILABLE / NOT PUBLISHED)
- **Processing Conditions (BASF Processing Data Sheet):**
  - Melt Temperature: $280\text{--}300\text{ °C}$ | Mold Temperature: $80\text{--}90\text{ °C}$
  - Pre-drying: $80\text{ °C}$ for 4 hours
  - Recommended Pellet Moisture: **0.025 – 0.045 %**
- **70 °C Property Classification:**  
  `CONDITIONAL — EXACT 70 C CONDITIONED PROPERTY NOT VERIFIED`  
  *(Moisture conditioning substantially reduces 23 °C modulus and stress at break; exact 70 °C conditioned mechanical behavior remains unresolved).*

---

## 3. Hydrolysis-Resistant Grade Context & Wellbore Fluid Compatibility

BASF designates Ultramid A3WG6 HRX as a *glass-fibre-reinforced injection moulding grade with enhanced resistance to hydrolysis and heat ageing*. It was specifically developed for automotive cooling circuits exposed to hot water/glycol mixtures.

> **Engineering Boundary:** Automotive cooling-circuit performance does **NOT** constitute verified downhole oilfield compatibility.

The following downhole environmental exposures remain **UNVERIFIED** for PA66-GF30:
1. **Hot completion brines** ($CaCl_2$, $ZnBr_2$, $NaCl$ solutions at 70 °C).
2. **Crude oil and liquid hydrocarbons** (aromatic swelling and extraction of plasticizers).
3. **Drilling and completion fluids** (oil-based muds, synthetic esters, amine-treated muds).
4. **Sour gas ($H_2S$) and dissolved $CO_2$ acid gas exposure**.
5. **Long-duration immersed dimensional stability at 70 °C** (hydrothermal swelling and microcracking).

---

## 4. Focused Carrier Material Trade Matrix

| Property / Criterion | Victrex 450G PEEK | Solvay Amodel A-1133 HS PPA | BASF Ultramid A3WG6 HRX PA66-GF30 |
|---|---|---|---|
| **Polymer Family** | PEEK (Unfilled) | PPA (Polyphthalamide) | PA66 (Polyamide 66) |
| **Reinforcement** | None (Unfilled) | 33% Glass Fiber | 30% Glass Fiber |
| **Density** | 1300 kg/m³ | 1480 kg/m³ | 1370 kg/m³ |
| **Tensile Modulus (23 °C)** | Dry: 4000 MPa<br>Cond: 4000 MPa | Dry: 13,400 MPa<br>Cond: 11,813 MPa (70C) | Dry: 9500 MPa<br>Cond: 6000 MPa |
| **Strength Basis & Value** | `TENSILE_STRENGTH`<br>Dry: 100 MPa<br>70 °C: 70 MPa | `TENSILE_STRESS_AT_BREAK`<br>Dry: 233 MPa<br>70 °C DAM: 181 MPa | `TENSILE_STRESS_AT_BREAK`<br>Dry: 185 MPa<br>Cond (23C): 110 MPa |
| **Thermal Conductivity** | 0.29 W/(m·K) | 0.26 W/(m·K) | 0.36 W/(m·K) |
| **Specific Heat Capacity** | 1500 J/(kg·K) | 1200 J/(kg·K) | 1260 J/(kg·K) |
| **Moisture Absorption (Eq 50% RH)** | 0.10% (24h) / 0.50% (sat) | 0.20% (24h) / 1.80% (sat) | **1.5 – 1.9 %** |
| **Water Absorption (Saturation in water)** | **0.50%** | **1.80%** | **5.6 – 6.3 %** |
| **CLTE (Cross-flow / Flow)** | 55 / 45 ppm/K | 55 / 22 ppm/K | 70 / 30 ppm/K |
| **70 °C Property Confidence** | `VERIFIED / INTERPOLATED` | `VERIFIED / INTERPOLATED` | `CONDITIONAL — UNVERIFIED WET` |
| **1000h Creep Modulus (23 °C Cond)** | High (Tg = 143 °C) | High (10.8 GPa @ 100 °C) | 4800 MPa (70 °C wet unverified) |
| **Dimensional Risk in Tight Bore** | `LOW` | `LOW-TO-MODERATE` | `HIGH DIMENSIONAL RISK` |
| **Downhole Fluid Compatibility** | `STRONGEST EVIDENCE` | `PROVISIONAL / CONDITIONAL` | `UNVERIFIED / HIGH RISK` |
| **Manufacturability & Processing** | High melt temp (380 °C); excellent CNC | Standard high temp (320 °C); abrasive GF | Excellent molding (280 °C); drying req (0.025-0.045%); GF abrasive |
| **Relative Cost Class** | `HIGH COST CLASS` | `EXPECTED LOWER-COST CANDIDATE — PROCUREMENT UNVERIFIED` | `EXPECTED LOWER-COST CANDIDATE — PROCUREMENT UNVERIFIED` |
| **Overall Carrier Classification** | **`RECOMMENDED BASELINE / STRONGEST CURRENT EVIDENCE`** | **`PREFERRED HIGH-PERFORMANCE COST-REDUCTION CANDIDATE`** | **`PROTOTYPE / VALIDATION CANDIDATE`** |

---

## 5. Carrier Sizing, Tolerance & Dimensional Conditioning Sensitivity

Inside the 37.45 mm Inconel shell bore, the carrier chassis must maintain free sliding during assembly (20 °C) and operation (70 °C) without binding or pinching circuit cards.

### Assumed Dimensional-Conditioning Sensitivity Sweep:
*Note: Dimensional-conditioning allowances represent an explicit sensitivity sweep over assumed radial growth, NOT a direct conversion from water-absorption mass percentage.*

| Material | Carrier Nom OD | Conditioning Diam Allowance | Diff Thermal Growth | Hot Clearance (Nom) | Worst-Case Hot Clearance | Avail Guide Wall | Sliding Status |
|---|---|---|---|---|---|---|---|
| **PEEK** | 37.050 mm | +0.010 mm | +0.0775 mm | 0.3125 mm | **0.3125 mm** | 3.525 mm | `FREE SLIDING` |
| **PEEK** | 37.050 mm | +0.020 mm | +0.0775 mm | 0.3025 mm | **0.3025 mm** | 3.525 mm | `FREE SLIDING` |
| **PEEK** | 37.050 mm | +0.040 mm | +0.0775 mm | 0.2825 mm | **0.2825 mm** | 3.525 mm | `FREE SLIDING` |
| **PPA** | 37.050 mm | +0.020 mm | +0.0775 mm | 0.3025 mm | **0.3025 mm** | 3.525 mm | `FREE SLIDING` |
| **PPA** | 37.050 mm | +0.030 mm | +0.0775 mm | 0.2925 mm | **0.2925 mm** | 3.525 mm | `FREE SLIDING` |
| **PPA** | 37.050 mm | +0.060 mm | +0.0775 mm | 0.2625 mm | **0.2625 mm** | 3.525 mm | `FREE SLIDING` |
| **PA66** | 37.050 mm | +0.040 mm | +0.1053 mm | 0.2547 mm | **0.2547 mm** | 3.525 mm | `FREE SLIDING` |
| **PA66** | 37.050 mm | +0.080 mm | +0.1053 mm | 0.2147 mm | **0.2147 mm** | 3.525 mm | `FREE SLIDING` |
| **PA66** | 37.050 mm | +0.120 mm | +0.1053 mm | 0.1747 mm | **0.1747 mm** | 3.525 mm | `FREE SLIDING` |
| **PA66** | 37.050 mm | +0.200 mm | +0.1053 mm | 0.0947 mm | **0.0947 mm** | 3.525 mm | `FREE SLIDING` |
| **PA66** | 37.050 mm | +0.300 mm | +0.1053 mm | -0.0053 mm | **-0.0053 mm** | 3.525 mm | `RISK OF BINDING / INTERFERENCE` |
| **PA66** | 36.850 mm | +0.040 mm | +0.1046 mm | 0.4554 mm | **0.4554 mm** | 3.425 mm | `FREE SLIDING` |
| **PA66** | 36.850 mm | +0.080 mm | +0.1046 mm | 0.4154 mm | **0.4154 mm** | 3.425 mm | `FREE SLIDING` |
| **PA66** | 36.850 mm | +0.120 mm | +0.1046 mm | 0.3754 mm | **0.3754 mm** | 3.425 mm | `FREE SLIDING` |
| **PA66** | 36.850 mm | +0.200 mm | +0.1046 mm | 0.2954 mm | **0.2954 mm** | 3.425 mm | `FREE SLIDING` |
| **PA66** | 36.850 mm | +0.300 mm | +0.1046 mm | 0.1954 mm | **0.1954 mm** | 3.425 mm | `FREE SLIDING` |

### Sizing Observations:
- For **PEEK** ($OD = 37.05\text{ mm}$, allowance $= 0.020\text{ mm}$), worst-case hot diametral clearance is **+0.2634 mm** (+0.1317 mm radial), maintaining ample free-sliding margin.
- For **PPA-GF** ($OD = 37.05\text{ mm}$, allowance $= 0.030\text{ mm}$), worst-case hot diametral clearance is **+0.2534 mm**, fully adequate.
- For **PA66-GF30** ($OD = 37.05\text{ mm}$):
  - At nominal assumed conditioning allowance ($0.080\text{ mm}$), worst-case clearance is **+0.1756 mm** (adequate).
  - However, if assumed saturation swelling reaches $0.200\text{--}0.300\text{ mm}$ diametral in a wet well environment, worst-case clearance drops to **+0.0556 mm / -0.0444 mm**, risking carrier binding and tool jamming unless carrier OD is reduced to **36.85 mm**.

---

## 6. Short-Duration Creep & Thermal Assessment

### Creep Assessment during 2-Hour Exposure:
- 23 °C conditioned creep evidence exists for PA66-GF30 ($4800\text{ MPa}$ at 1000h, ISO 899-1); 70 °C wet creep remains unresolved.
- For the nominal **2.0 hours (7200 s)** PertAcoustic logging run, the short duration reduces concern under internal self-weight and card-retention loads, but does not establish formal creep qualification.

### Thermal Comparison:
- Thermal conductivities: PEEK ($0.29\text{ W/(m·K)}$), PPA ($0.26\text{ W/(m·K)}$), PA66-GF30 ($0.36\text{ W/(m·K)}$).
- PA66-GF30 provides slightly higher bulk conductivity (+24% vs PEEK), aiding heat transfer from board guide edges to the shell.
- Inner shell surface 2-hour screening temperature remains virtually identical across all three discrete carrier candidates (**70.00 °C** at 1.0 W) because heat conducts through the high-conductivity Inconel shell ($14.7\text{ W/(m·K)}$) directly into the wellbore fluid.
- The allowable internal thermal resistance budget remains **15.00 K/W** for verified +85 °C electronics.

---

## 7. Manufacturing & Processability Comparison

1. **Injection Molding:**
   - **PA66-GF30:** Excellent moldability at standard melt temperatures ($280\text{--}300\text{ °C}$) and mold temperatures ($80\text{--}90\text{ °C}$). Requires pre-drying at $80\text{ °C}$ (4 h) to recommended pellet moisture of $0.025\text{--}0.045\%$ to prevent hydrolytic degradation during processing.
   - **PPA-GF:** High-temperature molding ($315\text{--}330\text{ °C}$) with heated molds ($135\text{--}150\text{ °C}$) required to achieve full crystallinity.
   - **PEEK:** Ultra-high-temperature molding ($380\text{--}400\text{ °C}$) requiring specialized high-temp injection equipment and mold heaters ($160\text{--}190\text{ °C}$).
2. **Prototype Manufacturing:**
   - **Unfilled PEEK:** Outstanding machinability from standard stock plate/rod, producing smooth burr-free card grooves.
   - **PPA-GF & PA66-GF30:** Injection molded exact grade, or CNC machining of exact-grade molded stock/coupons using polycrystalline diamond (PCD) or coated carbide tooling (note: additive manufacturing / 3D printing is unsupported for the exact BASF A3WG6 HRX granule grade).

---

## 8. Proposed Future Physical Validation Plan (Wet / 70 °C Testing)

Because PA66 moisture absorption is substantial, the following empirical screening test plan is recommended prior to downhole adoption:

1. **As-Machined / Molded Baseline Inspection:**
   - Measure carrier OD, length, card-guide slot width, and total dry mass ($M_0$).
2. **Water / Brine Conditioning Immersion:**
   - Immerse carrier test coupons in simulated completion brine (3% KCl / NaCl solution) at 23 °C and 70 °C.
   - Measure mass uptake $\Delta M(t)$ and diametral linear expansion $\Delta D(t)$ at 24h, 48h, 168h (1 week), and saturation.
3. **Inconel Bore Sliding Coupon Test:**
   - Slide conditioned wet carrier coupons through an Inconel 718 tube bore coupon (ID $37.45\pm 0.02\text{ mm}$) at 20 °C and inside a 70 °C heated chamber.
   - Verify insertion/extraction force remains $< 20\text{ N}$ without binding.
4. **PCB Card Guide Fit & Retention Test:**
   - Measure PCB card-edge insertion force into the guide slots before and after 70 °C hydrothermal conditioning to verify slot width does not swell shut or pinch circuit boards.

---

## 9. Side-by-Side Architecture Comparison Matrix

Evaluated under 70 °C external boundary and 7200 s (2h) exposure:

| Architecture | Casing Material | Carrier / Liner | Wall mm | Shell Bore ID | Packaging Feasibility | Inner Shell Temp @ 1W | FoS Buckle (10k psi) | Classification |
|---|---|---|---|---|---|---|---|---|
| **Architecture A: Inconel 718 + Discrete PEEK Carrier (3.5 mm Wall)** | Inconel718 | Conformal Rails (PEEK) | 3.50 | 37.45 mm | FEASIBLE | 70.00 °C | 1.64 | RECOMMENDED BASELINE |
| **Architecture A (4.0 mm Wall): Inconel 718 + Discrete PEEK Carrier** | Inconel718 | Conformal Rails (PEEK) | 4.00 | 36.45 mm | FEASIBLE | 70.00 °C | 2.45 | QUALIFIED SCREENING |
| **Architecture B: Inconel 718 + Discrete PPA Carrier (3.5 mm Wall)** | Inconel718 | Conformal Rails (PPA) | 3.50 | 37.45 mm | FEASIBLE | 70.00 °C | 1.64 | QUALIFIED SCREENING |
| **Architecture B2: Inconel 718 + Discrete PA66-GF30 Carrier (3.5 mm Wall)** | Inconel718 | Conformal Rails (PA66) | 3.50 | 37.45 mm | FEASIBLE | 70.00 °C | 1.64 | QUALIFIED SCREENING |
| **Architecture C: Inconel 718 + Full PEEK Liner (3.5 mm Wall)** | Inconel718 | Full Liner (PEEK) | 3.50 | 37.45 mm | INFEASIBLE | 70.09 °C | 1.64 | INFEASIBLE |
| **Architecture D: Inconel 718 + Full PPA Liner (3.5 mm Wall)** | Inconel718 | Full Liner (PPA) | 3.50 | 37.45 mm | INFEASIBLE | 70.10 °C | 1.64 | INFEASIBLE |
| **Architecture D2: Inconel 718 + Full PA66-GF30 Liner (3.5 mm Wall)** | Inconel718 | Full Liner (PA66) | 3.50 | 37.45 mm | INFEASIBLE | 70.07 °C | 1.64 | INFEASIBLE |
| **Reference Baseline (Arch E): Inconel 718 + Aerogel + PEEK** | Inconel718 | Full Liner (PEEK) | 3.50 | 37.45 mm | INFEASIBLE | 71.72 °C | 1.64 | INFEASIBLE |
| **Architecture F: PEEK-Only Pressure Casing (Exploratory)** | PEEK | None (PEEK) | 7.22 | 30.00 mm | INFEASIBLE | 70.41 °C | 0.29 | EXPLORATORY |
| **Architecture G: PPA-Only Pressure Casing (Exploratory)** | PPA_Amodel_A1133HS | None (PPA) | 7.22 | 30.00 mm | INFEASIBLE | 70.46 °C | 0.93 | EXPLORATORY |
| **Architecture G2: PA66-GF30-Only Pressure Casing (Exploratory)** | PA66_Ultramid_A3WG6_HRX | None (PA66) | 7.22 | 30.00 mm | INFEASIBLE | 70.33 °C | 0.47 | EXPLORATORY |
| **Architecture A: Inconel 718 + Discrete PEEK (OD 47.62 mm)** | Inconel718 | Conformal Rails (PEEK) | 3.50 | 40.62 mm | FEASIBLE | 70.00 °C | 1.34 | QUALIFIED SCREENING |
| **Architecture A: Inconel 718 + Discrete PEEK (OD 50.80 mm)** | Inconel718 | Conformal Rails (PEEK) | 3.50 | 43.80 mm | FEASIBLE | 70.00 °C | 1.10 | QUALIFIED SCREENING |
| **Architecture A: Inconel 718 + Discrete PEEK (OD 53.98 mm)** | Inconel718 | Conformal Rails (PEEK) | 3.50 | 46.98 mm | FEASIBLE | 70.00 °C | 0.92 | QUALIFIED SCREENING |
| **Architecture A: Inconel 718 + Discrete PEEK (OD 57.15 mm)** | Inconel718 | Conformal Rails (PEEK) | 3.50 | 50.15 mm | FEASIBLE | 70.00 °C | 0.77 | QUALIFIED SCREENING |

---

## 10. Thermal Screening & Internal Resistance Budgets

- **External Boundary:** 70.0 °C constant Dirichlet on casing outer diameter.
- **Duration:** 7200 s (2.0 hours).
- **Result Type:** `IDEAL SHELL-COUPLED LOWER-BOUND TEMPERATURE (INNER SHELL SURFACE)`
- **Allowable Internal Thermal Resistance Budget:** **15.00 K/W** (for +85 °C IC limits).

### Internal Thermal-Resistance Parameter Sweep:
| Internal Thermal Resistance $R_{\text{internal}}$ | Internal Temperature Rise $\Delta T$ | Electronics Screening Temp | +85 °C IC Limit Status | Notes |
|---|---|---|---|---|
| 0.0 K/W | +0.0 K | **70.00 °C** | `WITHIN 85C BOUND` | Lumped screening parameter |
| 5.0 K/W | +5.0 K | **75.00 °C** | `WITHIN 85C BOUND` | Lumped screening parameter |
| 10.0 K/W | +10.0 K | **80.00 °C** | `WITHIN 85C BOUND` | Lumped screening parameter |
| 15.0 K/W | +15.0 K | **85.00 °C** | `WITHIN 85C BOUND` | Lumped screening parameter |
| 20.0 K/W | +20.0 K | **90.00 °C** | `EXCEEDS 85C BOUND` | Lumped screening parameter |
| 25.0 K/W | +25.0 K | **95.00 °C** | `EXCEEDS 85C BOUND` | Lumped screening parameter |

---

## 11. Structural Screening Across Pressure Scenarios (Architecture A: Inconel 718 + Discrete PEEK Carrier (3.5 mm Wall))

*Authoritative casing design pressure remains unresolved. Sizing is based on preliminary engineering screening. PA66 is NOT ELIGIBLE AS THE CURRENT PRESSURE-SHELL BASELINE. Polymer-only casing remains EXPLORATORY / CONDITIONAL because authoritative field pressure, creep and collapse requirements remain unresolved.*

1. **Scenario A (~10 MPa / 1,450 psi - ~1000 m Hydrostatic Context):**
   - Max von Mises Stress: **59.7 MPa** | Strength Ratio: **16.75** | Buckling FoS: **11.33**
2. **Scenario B (20 MPa / 2,900 psi - Intermediate Sensitivity):**
   - Max von Mises Stress: **119.4 MPa** | Strength Ratio: **8.38** | Buckling FoS: **5.67**
3. **Scenario C (68.95 MPa / 10,000 psi - Historical Biweekly 5 Benchmark):**
   - Max von Mises Stress: **411.6 MPa** | Strength Ratio: **2.43** | Buckling FoS: **1.64**

---

## 12. CAD Assembly & Dimensional Extent

- **Collision Check:** Automated Boolean intersection checks confirmed **zero prohibited interference (0.00 mm³)**.
- **Modeled Subassembly Span:** **656.9 mm** (Limit $\le 2000.0\text{ mm}$).
- **CAD Assembly Bounding Extent:** **656.9 mm** along axial Z.

---

## 13. Artifacts & Generated Evidence

- **CAD STEP Model:** [`results/compact-casing/cad/compact_casing_assembly.step`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/cad/compact_casing_assembly.step)
- **Trade Study Dataset:** [`results/compact-casing/compact_casing_trade_study.csv`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/compact_casing_trade_study.csv)
- **Visualizations:**
  - 3D CAD Assembly Render: [`results/compact-casing/figures/compact_cad_assembly.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_cad_assembly.png)
  - Transverse Cross-Section (Conformal Clearance & Card Guides): [`results/compact-casing/figures/compact_transverse_pcm1808_section.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_transverse_pcm1808_section.png)
  - Longitudinal Section: [`results/compact-casing/figures/compact_longitudinal_section.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_longitudinal_section.png)
  - Thermal History & Comparison: [`results/compact-casing/figures/compact_thermal_trade_study.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_thermal_trade_study.png)
