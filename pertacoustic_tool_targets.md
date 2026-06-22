# Technical Design Targets: Wellbore Environmental Specifications for PHE Oil Wells

This document outlines the target downhole environmental operating specifications for a commercial-spec Spectral Noise Logging (SNL) tool, establishing the temperature, pressure, depth, fluid, and corrosion limits specifically tailored for oil production and exploration wells operated by PT Pertamina Hulu Energi (PHE) in Indonesia.

---

## 1. Wellbore Environmental Targets (Oil Focus)

The tool housing and internal electronics are designed to meet standard-to-mid HPHT (High Pressure High Temperature) classifications, ensuring structural, electrical, and sealing integrity in the specific reservoir regimes of mature and exploration oil fields.

### A. Temperature Limits ($T_{max}$)
*   **Target Spec**: **150°C (302°F)** [2][5].
    *   *PHE Asset Rationale*: Most mature oil fields in Indonesia (e.g., PHE ONWJ offshore Java) operate at bottomhole temperatures between 60°C and 100°C [14]. However, a **150°C** ceiling is required to support Enhanced Oil Recovery (EOR) steamflood wells (such as the Duri field in the PHE Rokan block), where injected steam heats the production oil zone up to 150°C [10].

### B. Hydrostatic Pressure Limits ($P_{max}$)
*   **Target Spec**: **10,000 PSI (69 MPa)** [6].
    *   *PHE Asset Rationale*: Standard development oil wells are generally depleted and operate under artificial lift (e.g., ESP, gas lift) at pressures below 3,000 PSI [8]. A **10,000 PSI** rating provides a robust safety margin for these wells and ensures compatibility with deep overpressured exploratory oil zones (e.g., deeper reservoir formations in the Rokan block) [9].

### C. Depth Rating
*   **Target Spec**: **3,500 meters (11,500 feet)** [1][2].
    *   *PHE Asset Rationale*: Covers the depth range of the deepest onshore development and exploratory oil wells in Sumatra and East Kalimantan blocks. 

### D. Fluid Medium (Viscous Crude & API)
*   **Target Spec**: Fully operational in **viscous heavy crude oil (17° to 22° API range)** [10].
    *   *PHE Asset Rationale*: Many of PHE's major oil reserves (e.g., Bakung and Delima formations in the Rokan block) produce high-viscosity heavy crudes. The acoustic window must maintain impedance-matching and the tool seals must resist degradation when operating in heavy oil [6][10].

### E. Corrosion & Acid Gas Resistance
*   **Hydrogen Sulfide ($\text{H}_2\text{S}$)**: Certified for sour service up to **6% concentration** [6].
*   **Carbon Dioxide ($\text{CO}_2$)**: Certified for sour service up to **10% concentration** [6].
    *   *PHE Asset Rationale*: Indonesian mature oil wells exhibit mild-to-moderate sour characteristics. Stainless Steel 316L/Inconel housing components and double Viton elastomer seals are required to prevent corrosive degradation and explosive decompression [3][6].

---

## 2. Sensor Module & OEM Sourcing Targets

Based on procurement constraints (budget < 250M IDR) and design flexibility, the project targets the following sourcing strategies for the acoustic sensor:

### A. Sourcing Strategy
*   **Target:** Procurement from Tier-1 Chinese OEMs (e.g., WELL-SUN, SITAN, Geo-Vista).
*   **Scope:** The project is evaluating both **complete factory-cased tools** and **bare internal sensor/electronics modules** that require custom housing.

### B. Telemetry & Deployment
*   **Target Spec:** Support for **Hybrid Telemetry**. The OEM module should ideally support both **Memory Mode** (running on internal flash memory and HT batteries for slickline deployment) and **Real-Time Wireline Mode** (surface read-out via electrical cable).

### C. Internal Chassis Dimension Constraints
*   **Target Spec:** Maximum internal electronics chassis diameter of **25.4 mm (1.0-inch) slim-hole**.
*   **Rationale:** The final assembled downhole tool must not exceed a **43 mm (1-11/16")** outer diameter to pass through PHE production tubing restrictions. Selecting a 25.4 mm internal chassis guarantees an **8.8 mm radial clearance**, which is strictly required to accommodate the high-pressure structural housing walls and the thermal flask (vacuum/oil) insulation needed to protect the electronics at 150°C.

---

## References
*   [1] [GOWell - SNT (Stationary Noise Tool) Technical Datasheet](https://gowell.energy/stationary-noise-tool/) (Downhole acoustic logging specifications).
*   [2] [TGT Diagnostics - Chorus Acoustic Diagnostics Specs](https://tgtdiagnostics.com/technology/chorus) (Flow diagnostics and frequency ranges).
*   [3] [SPE/JPT - HPHT Downhole Tools Classification and Requirements](https://jpt.spe.org) (Materials for wellbore integrity).
*   [5] [Society of Petroleum Engineers (SPE) - HPHT Wells Overview](https://petrowiki.spe.org/High-pressure_high-temperature_wells) (HPHT logging bounds).
*   [6] [North Side Tools - FIND Technical Specification Flyer PDF](https://northsidetools.com/wp-content/uploads/2023/07/FIND-specification-flyer.pdf) (Split-channels SNL tool specifications).
*   [8] [IAGI (Indonesian Association of Geologists) - Oil Fields Reservoir Pressures](https://www.iagi.or.id) (Depletion in mature wells).
*   [9] [IPA (Indonesian Petroleum Association) - Pore Pressure Forecasting in Sumatra Basins](https://www.ipa.or.id) (Overpressures at depth).
*   [10] [SPE - Heavy Oil Recovery and Steamflooding in Rokan Block](https://onepetro.org) (Duri field thermal profiles).
*   [14] [Pertamina - PHE ONWJ Well Development & Drilling](https://www.pertamina.com) (Miocene reservoir depths).

