# Downhole Tool Auxiliary Components: Pertacoustic Prototype

This document outlines the recommended auxiliary components—pre-amplifiers, data loggers, power supplies, and thermal packaging—needed to construct a fully functional downhole memory Spectral Noise Logging (SNL) prototype around the **Aquarian Audio AS-1** hydrophone.

---

## 1. Analog Front-End (Pre-Amplifier)

Since the AS-1 is a passive, high-impedance piezoelectric sensor, sending its signal directly over a cable will result in severe signal loss and noise pickup [1][2]. We need a high-input-impedance buffer pre-amplifier placed inside the casing close to the sensor.

### Recommended Components

| Component Type | Prototyping Grade (<80°C) | High-Temperature (HT) Grade (150°C) | Design Rationale |
| :--- | :--- | :--- | :--- |
| **Operational Amplifier (Op-Amp)** | **Texas Instruments OPA211** or **OPA2107** [3] | **Texas Instruments OPA211-HT** [4] | Precision JFET/bipolar op-amps with ultra-low input bias current and low noise. The OPA211-HT is specifically rated for continuous operation up to **210°C** [4]. |
| **Circuit Configuration** | **Non-inverting Voltage Buffer** (Gain: 40 dB to 60 dB / 100x to 1000x) | **Non-inverting Voltage Buffer** (with HT-rated metal film resistors) | High input impedance (>10 MΩ) prevents low-frequency roll-off from the hydrophone's 5nF capacitive source [1][2]. |

---

## 2. Data Acquisition (ADC & Microcontroller Data Logger)

The data logger must digitize the audio at a high sampling rate (at least 96 kHz or 192 kHz to cover the 60 kHz SNL spectrum [5]) and record it to non-volatile flash storage.

### Recommended Components

| Component Type | Prototyping Grade (<80°C) | High-Temperature (HT) Grade (150°C)* | Design Rationale |
| :--- | :--- | :--- | :--- |
| **Microcontroller (MCU)** | **Teensy 4.0** or **Teensy 4.1** [6] | **Texas Instruments MSP430-HT** or custom SOI (Silicon-on-Insulator) cores [7] | The Teensy 4.x features an ARM Cortex-M7 running at 600 MHz, providing the DSP speed required to process FFTs or stream high-speed audio to an SD card [6]. |
| **Audio Codec / ADC** | **Teensy Audio Shield (SGTL5000)** [8] | **Texas Instruments ADS1278-HT** (24-bit delta-sigma ADC) [9] | The SGTL5000 is a low-power stereo codec with high-quality ADCs that integrates seamlessly with Teensy audio libraries [8]. |
| **Storage Medium** | **MicroSD Card** (Class 10 / UHS-I, formatted to FAT32/exFAT) | **High-Temp SPI Flash Memory** (e.g., Microchip SST26 HT-series) | Allows continuous recording of raw WAV files. Class 10 cards are required to handle writing speeds of ~3.1 Mbps (for 192 kHz / 16-bit mono audio). |

*\*Note: If standard electronics are placed inside a highly efficient vacuum Dewar flask, the internal temperature can be maintained below +85°C. This allows us to use industrial-grade prototyping components (like the Teensy) for logging runs of 4 to 6 hours [7].*

---

## 3. Power Supply (Batteries)

The tool operates in autonomous memory mode without real-time wireline power. It requires compact batteries that can deliver stable voltage at elevated temperatures.

### Recommended Components

| Battery Chemistry | Recommended Model | Temperature Rating | Design Rationale |
| :--- | :--- | :--- | :--- |
| **Standard Lithium-Ion (Prototyping)** | **Panasonic NCR18650B** (rechargeable) | -20°C to +60°C | Easy to charge and highly stable for initial bench and shallow-well tests. |
| **Lithium Thionyl Chloride ($\text{Li-SOCl}_2$) (Downhole)** | **Electrochem 3B series** or **Tadiran TLH series** (non-rechargeable) [10] | **-40°C to +150°C** [10] | The industry standard for downhole memory tools. They feature extremely high energy density, excellent shelf life, and do not suffer thermal runaway or drop voltage at 150°C [10]. |

---

## 4. Thermal & Mechanical Packaging

To bridge the gap between our +80°C COTS sensor limit [1] and the 150°C wellbore [11], we must use passive thermal barriers:

1.  **Double-Walled Vacuum Dewar Casing**:
    *   Acts as a high-performance thermos bottle [7].
    *   Slows down the rate of heat transfer from the 150°C wellbore fluid to the internal electronics cavity.
2.  **Phase Change Material (PCM)**:
    *   Paraffin wax or low-melting-point bismuth-alloy heat sinks placed inside the Dewar flask [7].
    *   As the material melts, it absorbs latent heat, keeping the internal electronics cavity at a stable, safe temperature (typically around +50°C to +70°C) for the logging duration (4–6 hours).
3.  **Acoustic Window & Coupling Oil**:
    *   The hydrophone must be submerged in an **acoustic coupling fluid** (e.g., clean silicone oil or glycerin) inside the tool [7].
    *   The casing must have a thin-walled titanium section or a high-temperature rubber boot (acoustic window) to transmit sound waves from the wellbore fluid into the coupling oil, without exposing the sensor to hydrostatic pressure [5][7].

---

## References
*   [1] [Aquarian Audio - AS-1 Hydrophone Technical Datasheet](https://www.aquarianaudio.com/as-1-hydrophone.html) (AS-1 high impedance and temperature constraints).
*   [2] [Etec - Aquarian AS-1 Technical Specs Sheet](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFY_P2NizF39YJdcSHOda8IIpPF5ta7qx0CEG7vwMoptwaht2whj6KQoCLS8echUIyzdTMAvBzGKQTqX1qyNM_jaC19vDB7zz00j75jMEy-kHWBXW6lANCs-JeC8A==) (High input impedance buffer requirements).
*   [3] [Texas Instruments - OPA2107 Precision Op-Amp Datasheet](https://www.ti.com) (Precision low-noise dual op-amp).
*   [4] [Texas Instruments - OPA211-HT High-Temperature Op-Amp Datasheet](https://www.ti.com) (210°C rated operational amplifier specs).
*   [5] [commercial_snl_tools.md](file:///C:/Users/faliq/Desktop/project-user/antigravity-pertacoustic/commercial_snl_tools.md) (Commercial downhole tool parameters and acoustic ranges).
*   [6] [PJRC - Teensy 4.0/4.1 Microcontroller Specifications](https://www.pjrc.com) (ARM Cortex-M7 microcontroller capabilities).
*   [7] [ICDP - Downhole Memory Tool Thermal Insulation Reference](http://www.icdp-online.org) (Dewar flask and Phase Change Material passive thermal engineering).
*   [8] [PJRC - Teensy Audio Shield Product Page](https://www.pjrc.com) (SGTL5000 audio codec integration details).
*   [9] [Texas Instruments - ADS1278-HT 24-Bit ADC Datasheet](https://www.ti.com) (175°C rated precision ADC specs).
*   [10] [Electrochem - High-Temperature Lithium Cells Datasheet](https://www.electrochem-solutions.com) (Downhole lithium battery specifications and safety ratings).
*   [11] [pertacoustic_tool_targets.md](file:///C:/Users/faliq/Desktop/project-user/antigravity-pertacoustic/pertacoustic_tool_targets.md) (PT Pertamina Hulu Energi wellbore environmental target parameters).
