# HPHT Hydrophone Sensor & Architecture Recommendations: PertAcoustic Prototype

This document evaluates the sensor architecture for the custom PertAcoustic downhole Spectral Noise Logging (SNL) casing prototype, targeting operations in PT Pertamina Hulu Energi (PHE) oil wells at up to **150°C and 14,500 psi**.

---

## 1. The Acoustic Paradox & Dual-Zone Architecture

Our thermal modeling has proven that protecting internal electronics for 1 hour at 150°C requires a high-performance **Dewar Vacuum Flask** architecture. However, a vacuum is a perfect acoustic insulator.

> [!WARNING]
> **The Deafness Trap**
> If an acoustic sensor is placed *inside* the thermal vacuum flask to protect it from the heat, the vacuum gap will completely block all outside sound. The tool will be deaf.

To solve this, the PertAcoustic tool MUST adopt a **Dual-Zone Architecture**:
1. **The Hot Zone:** The acoustic sensor must be mounted *outside* the vacuum flask, directly coupled to the wellbore environment. It will be subjected to the full 150°C and 14,500 psi.
2. **The Cold Zone:** The processing electronics (CPU, ADC, Memory) remain *inside* the vacuum flask, staying below 40°C.

---

## 2. Sensor Selection: True HPHT Hydrophones

Because the sensor must sit in the "Hot Zone," previous recommendations to use commercial-off-the-shelf low-temp hydrophones (like the Aquarian Audio AS-1 rated for 80°C) **must be abandoned**. They will melt and physically fail.

We must procure specialized HPHT hydrophones utilizing Silicon-on-Insulator (SOI), Silicon-on-Sapphire, or high-temperature piezoelectric ceramics (e.g., Lithium Niobate).

### Approved Procurement Options

| Manufacturer & Model | Max Temp | Max Pressure | Est. Cost | Application Assessment |
| :--- | :--- | :--- | :--- | :--- |
| **Avalon Sciences DHH-1/DHH-2** | **205°C** | 10,000+ psi | **$5,000 - $15,000+** | **(Recommended)** Industry standard for VSP and fracture monitoring. Extremely robust. |
| **Marschall Acoustics Instruments** | **180°C** | Custom | **$5,000+** | Custom-engineered for ultra-deep logging. |
| **High Tech Inc. HTI-00-DHPC** | **Custom** | 20,000 psi | **$5,000+** | Wideband, pressure-compensated for small wellbores. |

---

## 3. Bulkhead Sealing: Glass-to-Metal Seals (GTMS)

With the sensor in the 150°C/14,500 psi wellbore and the electronics in the 40°C vacuum, the analog signal wire must cross the pressure boundary. 

> [!IMPORTANT]
> **Hermetic Feedthrough Requirement**
> We will use **Glass-to-Metal Seal (GTMS)** hermetic bulkhead connectors to pass wires through the Titanium/Inconel casing walls. This is the only industry-approved method to maintain extreme vacuum integrity. Utilizing standard elastomer O-rings (like Kalrez) carries a catastrophic risk of extrusion and failure at 14,500 psi, which would instantly implode the flask.

---

## 4. Conclusion

By expanding the prototype budget to accommodate a true HPHT sensor (e.g., Avalon DHH-1) and integrating GTMS bulkheads, the PertAcoustic prototype will match the structural reliability of elite commercial tools (SLB, GOWell, TGT) while successfully surviving the harsh PHE wellbore conditions.
