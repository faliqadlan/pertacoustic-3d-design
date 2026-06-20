# Hydrophone Sensor Recommendations: Pertacoustic Prototype

This document evaluates commercial-off-the-shelf (COTS) hydrophone elements for integration into the custom Pertacoustic downhole Spectral Noise Logging (SNL) casing prototype, targeting operations in PT Pertamina Hulu Energi (PHE) oil wells.

---

## 1. Sensor Comparison Matrix

| Sensor Model | Frequency Range | Dimensions | Max Operating Temp | Estimated Price | Prototyping Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Aquarian Audio AS-1** | **1 Hz – 100 kHz (±2dB)** [1] | **12 mm OD x 40 mm Length** [1] | +80°C [1] | **$413 USD** [2] | **(Recommended)** Ultra-compact diameter leaves maximum radial clearance inside a 43 mm tool casing for thermal vacuum/oil shielding. Wide linear frequency range covers all downhole leak sounds. |
| **Teledyne RESON TC4013** | **1 Hz – 170 kHz** [3] | Miniature probe design [3] | +80°C [3] | **Several thousand USD** [4] | Reference-grade sensor with excellent flat frequency response. Highly accurate, but represents a higher procurement cost for early-stage prototypes. |
| **High Tech Inc HTI-96-MIN** | **2 Hz – 30 kHz** [5] | 19 mm OD x 63.5 mm Length [5] | +50°C [5] | **~$800 USD** [4] | Standard miniature hydrophone for seismic/borehole logging. Larger diameter leaves less room for casing insulation, and frequency is limited on the ultrasonic end. |

---

## 2. Recommendation Rationale: Aquarian Audio AS-1

For the initial prototype development, the **Aquarian Audio AS-1** is the recommended sensor due to the following key design factors:

1.  **Impedance-Matched Encapsulation**: Encapsulated in polyurethane, which closely matches the acoustic impedance of wellbore fluids (oil/brine), ensuring optimal acoustic coupling with minimal signal reflection at the boundary [1].
2.  **Compact Form Factor**: Its small 12 mm outer diameter is a crucial advantage [1]. In a standard **43 mm (1-11/16") casing**, this leaves a radial clearance of **15.5 mm** on each side. This clearance is necessary to accommodate:
    *   Structural titanium casing wall thickness.
    *   Pressurized elastomer sealing sleeves.
    *   Vacuum gap or insulation layers for heat protection.
3.  **Broadband Performance**: The 100 kHz frequency response covers the standard commercial logging bandwidth (8 Hz – 60 kHz) [1], allowing the tool to capture high-frequency gas bubbles and micro-leaks.

---

## 3. Critical Prototyping Constraint: Thermal Shielding

> [!WARNING]
> **Operating Temperature Limitations**
> All raw hydrophone elements are limited to an operating temperature of **+80°C** [1][3]. Since PHE oil wells (especially steamflood EOR wells like Duri) can reach temperatures up to **150°C** [6], the custom casing must function as a thermal flask (Dewar casing) or include a heat sink/oil buffer to protect the hydrophone during logging runs.

---

## 4. Alternative: Integrated Memory Recorders vs. Custom Tooling

Integrating a self-contained acoustic recorder (hydrophone + data logger + battery) simplifies wiring but introduces major physical and environmental constraints for downhole applications:

### A. Marine Integrated Recorders (e.g., SoundTrap)
*   **Acoustic Recorder (SoundTrap ST300/ST400)**: These systems integrate the hydrophone, battery, and flash memory into a single unit [7]. 
*   **Feasibility Issues**:
    1.  **Diameter Limits**: Standard SoundTrap models have outer diameters of **40 mm to 60 mm** [7]. When placed inside a protective casing, the tool will exceed the maximum cased hole logging restriction of **43 mm (1-11/16")**, meaning it cannot pass through standard $2\frac{3}{8}\text{-inch}$ production tubing.
    2.  **Temperature Limit**: These are designed for marine applications and are only rated up to **+35°C or +40°C** [7]. The internal batteries and flash memory will immediately fail in a **150°C** PHE wellbore [6].

### B. Commercial Downhole Memory Logging Tools (e.g., SLB, Baker Hughes, TGT)
*   **Downhole Memory SNL Tools**: These tools run autonomously on slickline using high-temperature lithium batteries and internal memory boards inside a 43 mm titanium housing rated for 150°C–177°C [8].
*   **Feasibility Issues**:
    1.  **High Procurement Cost**: Commercial units cost tens of thousands of dollars and are typically proprietary service offerings rather than off-the-shelf research sensors [4].
    2.  **Rigid Architecture**: The data logging frequency, telemetry interface, and DSP processing algorithms are closed-source and cannot be customized for academic research and custom CAD/CAE development.

---

## 5. Cost-Savings Analysis: Custom Prototype vs. SoundTrap System

To demonstrate the financial viability of our custom development path, the table below outlines the cost comparison between purchasing a complete marine recorder system (SoundTrap) and building a custom tool based on the **Aquarian Audio AS-1**:

### Cost Comparison Table

| Category | Option 1: Ocean Instruments SoundTrap | Option 2: Custom Prototype (AS-1 Based) | Direct Savings |
| :--- | :--- | :--- | :--- |
| **Raw Sensor Element** | **$1,450 USD** (HP2-HF Hydrophone) [7] | **$413 USD** (Aquarian AS-1) [2] | **$1,037 USD** |
| **Logger / Battery / ADC** | **Included** (in recorder package) [7] | **~$250 USD** (Custom DAQ / Teensy microcontroller) | — |
| **Protective Housing** | **$430 USD** (SeaVent PRV - 500m depth) [7] | **~$150 USD** (Custom titanium cased-hole casing) | **$280 USD** |
| **Total System Unit** | **$3,500 – $7,000 USD** (ST400 STD to ST640 HF) [7] | **~$813 USD** (Est. complete prototype assembly) | **$2,687 – $6,187 USD** |

### Key Savings Takeaways
*   **Standalone Sensor Savings**: Choosing the Aquarian Audio AS-1 instead of the SoundTrap HP2-HF sensor element saves **$1,037 USD** per unit [2][7].
*   **Complete System Savings**: Designing and building the custom casing and logging electronics around the AS-1 yields a minimum cost savings of **$2,687 USD** per tool compared to the basic SoundTrap ST400 STD recorder package, and up to **$6,187 USD** compared to the high-frequency ST640 HF package [2][7].

---

## References
*   [1] [Aquarian Audio - AS-1 Hydrophone Technical Datasheet](https://www.aquarianaudio.com/as-1-hydrophone.html) (Broadband passive hydrophone specifications).
*   [2] [Aquarian Audio - AS-1 Scientific Hydrophone Store Page](https://www.aquarianaudio.com/as-1-hydrophone.html) (Official AS-1 retail pricing).
*   [3] [Teledyne Marine - RESON TC4013 Miniature Reference Hydrophone](https://www.teledynemarine.com/en-us/products/acoustic-sensors/reson-tc4013) (Miniature reference hydrophone specifications).
*   [4] [Seis-Tech - Downhole Seismic Equipment and Market Pricing](https://seis-tech.com) (General commercial hydrophone pricing indicators).
*   [5] [High Tech Inc - HTI-96-MIN Hydrophone Product Specifications](https://hightechincusa.com) (Seismic and borehole hydrophone specifications).
*   [6] [SPE - Heavy Oil Recovery and Steamflooding in Rokan Block](https://onepetro.org) (Duri field thermal profiles).
*   [7] [Ocean Instruments - SoundTrap Price List & Specs](https://oceaninstruments.co.nz/) (Oceanographic acoustic recorder sizing, pricing, and temperature thresholds).
*   [8] [Baker Hughes - Memory Production Logging Platform Specs](https://www.bakerhughes.com) (High-temperature downhole memory tool specifications).
