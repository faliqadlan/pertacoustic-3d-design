# Downhole Tool Auxiliary Components: Pertacoustic Prototype

This document outlines the recommended auxiliary components—pre-amplifiers, data loggers, power supplies, and thermal packaging—needed to construct a fully functional downhole memory Spectral Noise Logging (SNL) prototype around the **Aquarian Audio AS-1** hydrophone.

---

## 1. Analog Front-End (Pre-Amplifier)

Since the AS-1 is a passive, high-impedance piezoelectric sensor, sending its signal directly over a cable will result in severe signal loss and noise pickup [1][2]. We need a high-input-impedance buffer pre-amplifier placed inside the casing close to the sensor.

### Component Recommendations & Costs

| Component Type | Prototyping Grade (<80°C) | High-Temperature (HT) Grade (150°C) | Estimated Price (Per Unit) | Design Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Operational Amplifier (Op-Amp)** | **Texas Instruments OPA211** or **OPA2107** [3] | — | **~$11 – $13 USD** [4] | Precision low-noise JFET/bipolar op-amps. |
| **HT Op-Amp** | — | **Texas Instruments OPA211-HT** [5] | **~$60 – $200 USD** [4] | Ceramic package, rated for continuous operation up to **210°C** [5]. |
| **Passive Electronics** | Standard Metal Film Resistors & Ceramic Caps | HT-rated Thin-Film Resistors & Ceramic Caps (NP0/C0G) | **~$5 USD** (Prototypes) / **~$30 USD** (HT) | Prevents drift and thermal degradation of the gain circuit. |

---

## 2. Data Acquisition (ADC & Microcontroller Data Logger)

The data logger must digitize the audio at a high sampling rate (at least 96 kHz or 192 kHz to cover the 60 kHz SNL spectrum [6]) and record it to non-volatile flash storage.

### Component Recommendations & Costs

| Component Type | Prototyping Grade (<80°C) | High-Temperature (HT) Grade (150°C)* | Estimated Price (Per Unit) | Design Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Microcontroller (MCU)** | **Teensy 4.1** (ARM M7 @ 600 MHz) [7] | — | **~$30 USD** (~Rp800.000 - Rp1.300.000) [4] | Provides high-speed processing and direct SD card audio streaming [7]. |
| **HT Microcontroller** | — | **Texas Instruments MSP430-HT** [8] | **~$150 – $300 USD** | Silicon-on-Insulator (SOI) MCU rated up to 150°C [8]. |
| **Audio Codec / ADC** | **Teensy Audio Shield (SGTL5000)** [9] | — | **~$20 – $25 USD** [4] | Integrates 24-bit audio ADC/DAC with Teensy audio libraries [9]. |
| **HT ADC** | — | **Texas Instruments ADS1278-HT** [10] | **~$100 – $250 USD** | 24-bit delta-sigma ADC rated up to 175°C [10]. |
| **Storage Medium** | **MicroSD Card** (Class 10 UHS-I, 32GB) | High-Temp SPI Flash Memory (e.g., Microchip SST26 HT-series) | **~$10 USD** (SD) / **~$25 USD** (HT SPI Flash) | Allows continuous recording of raw WAV files downhole. |

*\*Note: If standard electronics are placed inside a highly efficient vacuum Dewar flask, the internal temperature can be maintained below +85°C. This allows us to use industrial-grade prototyping components (like the Teensy) for logging runs of 4 to 6 hours [11].*

---

## 3. Power Supply (Batteries)

The tool operates in autonomous memory mode without real-time wireline power. It requires compact batteries that can deliver stable voltage at elevated temperatures.

### Component Recommendations & Costs

| Battery Chemistry | Recommended Model | Temperature Rating | Estimated Price (Per Cell) | Design Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Standard Lithium-Ion** | **Panasonic NCR18650B** (rechargeable) | -20°C to +60°C | **~$6 – $8 USD** | Stable rechargeable batteries for initial bench and shallow-well tests. |
| **Lithium Thionyl Chloride ($\text{Li-SOCl}_2$)** | **Electrochem 3B series** or **Tadiran TLH series** [12] | **-40°C to +150°C** [12] | **~$50 – $150 USD** [4] | Non-rechargeable cells designed for HPHT oilfield telemetry. Extremely high energy density [12]. |

---

## 4. Thermal & Mechanical Packaging

Custom casing and vacuum insulation components to shield the electronics and couple the acoustic signal:

### Component Recommendations & Costs

| Component | Function | Estimated Price (Prototyping) | Estimated Price (Industrial Custom Machined) | Design Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Dewar Casing Insert** | Passive thermal flask [11] | **~$150 – $250 USD** (Modified commercial steel flask) | **~$800 – $1,500 USD** (Custom machined dual-wall vacuum sleeve) | Limits thermal conduction from the 150°C wellbore [11]. |
| **Phase Change Material (PCM)** | Thermal heat sink absorption [11] | **~$10 USD** (Paraffin wax) | **~$50 USD** (Low-melting-point bismuth alloy) | Absorbs latent heat to delay internal temperature rise [11]. |
| **Outer Tool Housing** | Structural pressure container [6] | **~$200 USD** (Stainless steel 316 pipe & threads) | **~$1,000 – $2,000 USD** (Custom machined Titanium Grade 5 casing) | Rated to survive high wellbore pressures up to 10,000 PSI [13]. |
| **Acoustic Window & Oil** | Acoustic coupling boot [6][11] | **~$30 USD** (Buna-N rubber & silicone oil bath) | **~$150 USD** (Fluoroelastomer Viton boot & fluorosilicone oil) | Transmits sounds while protecting the sensor from sour service chemicals [13]. |

---

## 5. Complete System Prototyping Budgets

Below are two alternative total budget calculations for building the complete downhole logging tool. 

### Option A: The "Direct-Survival" HPHT Tool Setup (Under $2,000 USD)
In this configuration, we purchase the best high-temperature (HT) electronics capable of surviving 150°C wellbores directly, but keep costs under $2,000 USD by machining the casing from **Stainless Steel 316 (SS316)** instead of Titanium Grade 5. SS316 is highly corrosion-resistant and easily rated for 10,000 PSI, but is significantly cheaper and easier to machine than titanium [14].

*   **AS-1 Sensor**: $413 USD [2]
*   **HT Pre-amplifier**: TI OPA211-HT + HT passives = $130 USD [4][5]
*   **HT Data Logger**: TI MSP430-HT MCU + TI ADS1278-HT ADC + HT Flash = $375 USD [4][8][10]
*   **HT Batteries**: Electrochem 3B series ($\text{Li-SOCl}_2$) (2 cells) = $150 USD [4][12]
*   **Outer Casing**: Custom Machined 316 Stainless Steel = $450 USD [14]
*   **Acoustic Window**: Viton Boot & Fluorosilicone Oil = $150 USD [4]
*   **Total Setup Cost**: **$1,668 USD** (Well under $2,000 USD)

---

### Option B: The "Thermal Shielded" Prototyping Tool Setup (Under $1,000 USD)
In this configuration, we use standard prototyping-grade electronics (Teensy logger) and protect them from the 150°C wellbore using a **modified commercial steel vacuum Dewar flask** inside standard stainless steel piping.

*   **AS-1 Sensor**: $413 USD [2]
*   **Prototyping Pre-amplifier**: TI OPA211 + standard passives = $17 USD [4]
*   **Prototyping Logger**: Teensy 4.1 + Audio Shield + 32GB SD card = $65 USD [4][7][9]
*   **Prototyping Battery**: Rechargeable Panasonic 18650 cell = $8 USD
*   **Outer Casing**: Standard SS316 piping and end caps = $150 USD [14]
*   **Thermal Protection**: Dewar flask insert + Paraffin wax PCM = $190 USD [11]
*   **Acoustic Window**: Buna-N rubber boot & silicone oil bath = $30 USD [4]
*   **Total Setup Cost**: **$873 USD** (Highly economical)

---

## References
*   [1] [Aquarian Audio - AS-1 Hydrophone Technical Datasheet](https://www.aquarianaudio.com/as-1-hydrophone.html) (AS-1 high impedance and temperature constraints).
*   [2] [Aquarian Audio - AS-1 Scientific Hydrophone Store Page](https://www.aquarianaudio.com/as-1-hydrophone.html) (Official AS-1 retail pricing).
*   [3] [Texas Instruments - OPA2107 Precision Op-Amp Datasheet](https://www.ti.com) (Precision low-noise dual op-amp).
*   [4] [Mouser/DigiKey - Electronic Component Market Rates](https://www.mouser.com) (Current retail pricing for Teensy, OPA211, and HT batteries).
*   [5] [Texas Instruments - OPA211-HT High-Temperature Op-Amp Datasheet](https://www.ti.com) (210°C rated operational amplifier specs).
*   [6] [commercial_snl_tools.md](file:///C:/Users/faliq/Desktop/project-user/antigravity-pertacoustic/commercial_snl_tools.md) (Commercial downhole tool parameters and acoustic ranges).
*   [7] [PJRC - Teensy 4.1 Microcontroller Specifications](https://www.pjrc.com) (ARM Cortex-M7 microcontroller capabilities).
*   [8] [Texas Instruments - MSP430-HT Microcontrollers](https://www.ti.com) (150°C rated microcontrollers).
*   [9] [PJRC - Teensy Audio Shield Product Page](https://www.pjrc.com) (SGTL5000 audio codec integration details).
*   [10] [Texas Instruments - ADS1278-HT 24-Bit ADC Datasheet](https://www.ti.com) (175°C rated precision ADC specs).
*   [11] [ICDP - Downhole Memory Tool Thermal Insulation Reference](http://www.icdp-online.org) (Passive thermal engineering using Dewar flasks).
*   [12] [Electrochem - High-Temperature Lithium Cells Datasheet](https://www.electrochem-solutions.com) (Downhole lithium battery specifications and safety ratings).
*   [13] [pertacoustic_tool_targets.md](file:///C:/Users/faliq/Desktop/project-user/antigravity-pertacoustic/pertacoustic_tool_targets.md) (PT Pertamina Hulu Energi wellbore environmental target parameters).
*   [14] [FastPreci - Titanium vs Stainless Steel Machining Costs](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKSC_z_OzIAcfoEo2OtbqmiWoGQr_0EvoTjlij0tTdRVFS8QahyrViDZf-MW5X_wdjXec3cRh50PXSa5Jr1eKy7MYueFYpN5gSf8-dNvD9WEdPUCS1Pp9CINQhz8lV5Ywn9UVX0ZcALBqq717P0w7fXA==) (Detailed comparison of machining times and raw material premiums).
