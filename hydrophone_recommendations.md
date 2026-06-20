# Hydrophone Sensor Recommendations: Pertacoustic Prototype

This document evaluates commercial-off-the-shelf (COTS) hydrophone elements for integration into the custom Pertacoustic downhole Spectral Noise Logging (SNL) casing prototype, targeting operations in PT Pertamina Hulu Energi (PHE) oil wells.

---

## 1. Sensor Comparison Matrix

| Sensor Model | Frequency Range | Dimensions | Max Operating Temp | Prototyping Assessment |
| :--- | :--- | :--- | :--- | :--- |
| **Aquarian Audio AS-1** | **1 Hz – 100 kHz (±2dB)** [1] | **12 mm OD x 40 mm Length** [1] | +80°C [1] | **(Recommended)** Ultra-compact diameter leaves maximum radial clearance inside a 43 mm tool casing for thermal vacuum/oil shielding. Wide linear frequency range covers all downhole leak sounds. |
| **Teledyne RESON TC4013** | **1 Hz – 170 kHz** [2] | Miniature probe design [2] | +80°C [2] | Reference-grade sensor with excellent flat frequency response. Highly accurate, but represents a higher procurement cost for early-stage prototypes. |
| **High Tech Inc HTI-96-MIN** | **2 Hz – 30 kHz** [3] | 19 mm OD x 63.5 mm Length [3] | +50°C [3] | Standard miniature hydrophone for seismic/borehole logging. Larger diameter leaves less room for casing insulation, and frequency is limited on the ultrasonic end. |

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
> All raw hydrophone elements are limited to an operating temperature of **+80°C** [1][2]. Since PHE oil wells (especially steamflood EOR wells like Duri) can reach temperatures up to **150°C** [4], the custom casing must function as a thermal flask (Dewar casing) or include a heat sink/oil buffer to protect the hydrophone during logging runs.

---

## References
*   [1] [Aquarian Audio - AS-1 Hydrophone Technical Datasheet](https://www.aquarianaudio.com/as-1-hydrophone.html) (Broadband passive hydrophone specifications).
*   [2] [Teledyne Marine - RESON TC4013 Miniature Reference Hydrophone](https://www.teledynemarine.com/en-us/products/acoustic-sensors/reson-tc4013) (Miniature reference hydrophone specifications).
*   [3] [High Tech Inc - HTI-96-MIN Hydrophone Product Specifications](https://hightechincusa.com) (Seismic and borehole hydrophone specifications).
*   [4] [SPE - Heavy Oil Recovery and Steamflooding in Rokan Block](https://onepetro.org) (Duri field thermal profiles).
