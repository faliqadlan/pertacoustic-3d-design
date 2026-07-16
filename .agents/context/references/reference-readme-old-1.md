# Pertacoustic Study: Spectral Noise Logging (SNL) Well Diagnostics

This repository contains the software configuration, design targets, and research artifacts for the **Pertacoustic Study** (Studi Pertacoustic untuk Mengatasi Permasalahan Air), a joint research and development project conducted in collaboration with **Laboratorium Geofisika FMIPA Universitas Gadjah Mada (UGM)** and **PT Pertamina Hulu Energi (PHE) Upstream Innovation**.

---

## Project Overview
The project focuses on developing hardware and software components for high-sensitivity, high-resolution **Spectral Noise Logging (SNL)** using downhole hydrophones. SNL is a passive acoustic diagnostic methodology used to detect and characterize:
- Tubing and casing leaks
- Behind-casing fluid migration (cement channeling)
- Reservoir fluid inflow and production profiles
- Cross-flow behind single or multiple concentric barriers

---

## Repository Structure
*   `2604.05547v1.pdf`: Research reference on closed-loop CAD-CAE agentic optimization (COSMO-Agent).
*   `260619_PERTACOUSTIC_BIWEEKLY_2.pdf`: Biweekly progress report II (UGM & Pertamina Hulu Energi).
*   `FIND-specification-flyer.pdf`: North Side Tools FIND (Flow Identifying Noise Detector) specifications.
*   `commercial_snl_tools.md`: Comparative study of major commercial downhole SNL tools (GOWell SNT, TGT Chorus, Schlumberger HFND, etc.).
*   `pertacoustic_tool_targets.md`: Wellbore environmental operating specifications tailored for PHE oil wells.
*   `downhole_tool_components.md`: Auxiliary components list, specifications, pricing, and system-level budgets.
*   `SESSION_LOG.md`: Session logs and progress summary.

---

## Technical Specifications Target (PHE Oil Wells)
- **Temperature Limits**: 150°C BHT max (supporting standard reservoirs and steamflood EOR like Duri field).
- **Hydrostatic Pressure**: 10,000 PSI max (engineered for standard development and exploratory oil wells).
- **Depth Limit**: 3,500 meters.
- **Fluid Compatibility**: Heavy crude oil (17° to 22° API).
- **Sour Service Certification**: 6% to 25% H2S, 10% CO2.

---

## Persistent Session Memory (Antigravity 2.0)

To prevent the Antigravity agent from starting discussions from scratch when you open a new conversation or switch machines, follow these memory-preservation guidelines:

### 1. Maintain `SESSION_LOG.md` (Episodic Memory)
*   **How it works**: Antigravity automatically scans and reads all markdown files in the workspace at initialization.
*   **Action**: Ensure that `SESSION_LOG.md` is updated at the end of each session. The agent will read this log in any new conversation to immediately recall previous discussions, decisions, and files without requiring you to re-explain.

### 2. Define Workspace Rules in `.agents/AGENTS.md` (Procedural Memory)
*   **How it works**: Workspace-scoped agent rules are automatically loaded into the agent's system instructions at startup.
*   **Action**: Add custom rules in `.agents/AGENTS.md` to define design decisions (e.g., *"We are building Option C (Hybrid Premium AS-1 + Titanium Casing) at ~$4,353 USD"*). This locks the current architecture choice into the agent's behavior.

### 3. Synchronize via GitHub (Cross-Laptop Sync)
*   **How it works**: Git acts as the shared long-term memory across different computers.
*   **Action**: 
    1.  At the end of a session, run: `git add . && git commit -m "sync memory" && git push`
    2.  When opening a new conversation or using a different laptop, run: `git pull` before launching the agent.
    3.  This restores the exact workspace files, agent rules, custom skills, and logs.
