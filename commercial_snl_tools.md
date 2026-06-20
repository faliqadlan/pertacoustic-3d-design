# Commercial Spectral Noise Logging (SNL) Tools: Specifications & Procurement

This document provides a comparative analysis of the primary commercial downhole Spectral Noise Logging (SNL) tools used in well integrity, leak detection, and flow profiling. It outlines technical specifications and standard industrial pricing/procurement models.

> [!NOTE]
> Downhole well logging instruments are specialized industrial assets. Unlike consumer electronics or environmental logging tools, pricing is proprietary, highly customizable, and generally handled via corporate quotations.

---

## 1. Comparative Matrix of Key Commercial SNL Tools

| Provider / Manufacturer | Tool Name | Key Specifications & Architecture | Application Focus | Telemetry & Deployment |
| :--- | :--- | :--- | :--- | :--- |
| **North Side Tools** [5] | **FIND** *(Flow Identifying Noise Detector)* | • **Split-channels architecture**<br>• Outer Diameter (OD): 43 mm (standard)<br>• Combinable with standard PL tools [5] | • Tubing/casing leak detection<br>• Flow behind casing (cement channels) | • Real-Time SRO (Surface Readout) [14]<br>• Memory Mode |
| **TGT Diagnostics** [3] | **HPT-SNL** *(High-Precision Temp & SNL)* | • Combined passive acoustic + thermal sensors [7]<br>• **Multi-barrier detection** (through tubing & casing) [6] | • Well integrity mapping<br>• Reservoir flow allocation [1] | • Wireline (E-line)<br>• Slickline Memory |
| **Halliburton** [5] | **IntelliScope™** | • **Hydrophone array technology**<br>• Advanced **beamforming algorithms** [5] | • Real-time leak location<br>• Multiphase flow profiling [5] | • Real-Time Wireline [5] |
| **Schlumberger (SLB)** [9] | **HFND** *(High-Fidelity Noise Detection)* | • Wideband acoustic hydrophone<br>• Advanced digital signal filtering [9] | • Precision casing leak localization<br>• Downhole bubble detection [9] | • Wireline (E-line)<br>• Slickline Memory |
| **GOWell Energy** [15] | **SNT** *(Stationary Noise Tool)* | • Max Temp: **175°C (347°F)**<br>• Max Pressure: **20,000 PSI**<br>• Wideband passive sensor [15] | • Micro-leak detection<br>• High-pressure well integrity | • Combinable E-line / Memory [15] |
| **Sitan (China)** [21] | **MP Series Noise Tool** | • Slim-hole design (OD: 35 mm - 43 mm)<br>• High-sensitivity piezoelectric receiver [21] | • Geothermal & production wells<br>• Channeling detection [21] | • Wireline & Memory [21] |
| **Hunting PLC** [18] | **NST** *(Noise Spectrum Tool)* | • High-temperature sensor options<br>• Industry-standard combinable chassis [18] | • Standalone leak detection<br>• Secondary flow diagnostics | • Slickline Memory / E-line [18] |

---

## 2. Procurement Models & Pricing Structure

Corporate procurement for well-logging tools generally falls into two categories:

### A. Direct Tool Purchase Model (OEM / Manufacturers)
Mainly targeted at national oil companies (NOCs), wireline service providers, and large operators.
*   **Estimated Capital Expenditure (CapEx)**:
    *   **Memory-only SNL tools**: **$25,000 to $45,000 USD** per tool depending on temperature/pressure ratings.
    *   **Real-time (SRO) wireline-combinable SNL tools**: **$50,000 to $90,000+ USD** per tool, including downhole telemetry modules.
*   **Pricing Factors**: Max operating temperature (standard 150°C vs. high-temp 175°C+), pressure rating (15k vs. 20k PSI), and the inclusion of surface systems or acquisition software.

### B. Service-Based Rental Model (Logging Job)
Used when operators hire a service company to run a diagnostic log in a specific well.
*   **Estimated Operational Expenditure (OpEx)**:
    *   **Basic Logging Run**: **$5,000 to $12,000 USD** per well run (includes mobilization, wireline unit, tool run, and raw log delivery).
    *   **Advanced Diagnostics (e.g., TGT HPT-SNL)**: **$15,000 to $30,000+ USD** per well. This premium covers advanced modeling, spectral processing, and multi-barrier flow interpretation by subject matter experts.

---

## 3. Procurement Considerations

> [!WARNING]
> **Borehole vs. Environmental Instruments**
> Ensure you do not procure "environmental noise loggers" (used for civil construction/traffic monitoring) which are widely rentable for under $100/day. Borehole SNL tools must withstand high downhole pressures, be hermetically sealed, and communicate over wireline telemetry.

### Key Factors to Specify When Requesting Quotes:
1.  **Max Temperature & Pressure (HPHT)**: Standard wells need 150°C and 15,000 PSI. Geothermal or deep gas wells require 175°C+ and 20,000 PSI.
2.  **Deployment Telemetry**:
    *   *Real-time (SRO)*: Allows instant detection of leaks, optimizing stationary logging times.
    *   *Memory Mode*: Highly economical, deployed via slickline or coiled tubing without active conductor lines.
3.  **Data Interpretation Service**: Raw acoustic WAV data is noisy. The cost of data analysis and depth-frequency heatmap generation by specialized analysts is often factored separately into service quotes.
