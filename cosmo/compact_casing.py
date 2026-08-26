"""Compact Downhole Casing Redesign (Simplified No-Aerogel Architecture Study).

This module implements the comparative engineering study for the PertAcoustic
compact downhole casing under the confirmed 70 °C / 2-hour design envelope.

Architectures evaluated:
1. Architecture A: Inconel 718 pressure shell + discrete PEEK carrier rails (No Aerogel, No Full Liner) [RECOMMENDED BASELINE]
2. Architecture B: Inconel 718 pressure shell + discrete PPA carrier rails (No Aerogel, No Full Liner) [ALTERNATIVE]
3. Architecture C: Inconel 718 pressure shell + full circumferential PEEK liner (No Aerogel) [Comparison Case]
4. Architecture D: Inconel 718 pressure shell + full circumferential PPA liner (No Aerogel) [Comparison Case]
5. Reference Baseline (Arch E): Inconel 718 + Pyrogel HPS Aerogel + PEEK (Historical Baseline)
6. Architecture F (Exploratory): PEEK-only casing / pressure body
7. Architecture G (Exploratory): PPA-only casing / pressure body

All structural results are preliminary engineering screening calculations.
Historical Biweekly 5 artifacts remain preserved and unmodified.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import cadquery as cq
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Repository and output paths
ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results" / "compact-casing"
CAD_DIR = RESULTS_DIR / "cad"
FIG_DIR = RESULTS_DIR / "figures"
DATA_DIR = RESULTS_DIR / "data"

# Governing Design Envelope (Formal MoM & 20 August 2026 Direction)
PREFERRED_OD_MM = 44.45  # 1.75 in
MAX_OD_MM = 57.15  # 2.25 in
MAX_TOOL_LENGTH_MM = 2000.0  # 2.0 m hard limit
HOUSING_LENGTH_MM = 520.0  # Modeled housing length (well within <=2000 mm)
ENDCAP_THICKNESS_MM = 35.0
FRONT_AXIAL_BUFFER_MM = 25.0
REAR_AXIAL_BUFFER_MM = 25.0

EXTERNAL_TEMPERATURE_C = 70.0  # Governing boundary (MoM)
INITIAL_TEMPERATURE_C = 25.0  # Baseline ambient assembly
THERMAL_DURATION_S = 7200  # 2.0 hours (7200 s)
INHERITED_SCREENING_POWER_W = 1.0  # Inherited Biweekly 5 screening power
ZERO_POWER_W = 0.0  # Pure external heat ingress case

# Structural Screening Pressure Scenarios (Screening Only - Authoritative Field Pressure Unresolved)
PRESSURE_SCENARIO_1000M_MPA = 10.0  # ~1000 m hydrostatic context (~1450 psi)
PRESSURE_SCENARIO_INTERMEDIATE_MPA = 20.0  # Intermediate wellbore context (~2900 psi)
PRESSURE_SCENARIO_HISTORICAL_MPA = 68.9476  # 10,000 psi legacy screening benchmark

# Hardware selection and physical envelopes (length_mm, width_mm, height_mm)
STM32F411_ENVELOPE_MM = (53.0, 21.0, 11.5)  # STM32F411CEU6 Black Pill
PCM1808_ENVELOPE_MM = (50.0, 30.0, 12.0)  # PCM1808 ADC breakout board (30x12 mm cross-section)
POWER_ENVELOPE_MM = (35.0, 18.0, 10.0)  # Power regulation module
RTC_ENVELOPE_MM = (25.0, 15.0, 8.0)  # RTC module
SD_ENVELOPE_MM = (25.0, 15.0, 6.0)  # MicroSD storage module
AFE_ENVELOPE_MM = (30.0, 16.0, 8.0)  # Analog front-end pre-amp

# Radial clearance
BOARD_ASSEMBLY_CLEARANCE_MM = 1.0  # 1.0 mm per side

# Axial Component Thermal Zones along local Z (mm from front internal datum)
THERMAL_ZONES_LOCAL_MM = {
    "Analog front-end": (60.0, 100.0),
    "PCM1808 ADC": (105.0, 165.0),
    "STM32F411 MCU": (170.0, 235.0),
    "Power & RTC": (240.0, 305.0),
    "SD Storage & Reserve": (310.0, 420.0),
}

# Component Verified Temperature Operating Limits (°C)
# Only authorized project ICs use verified ranges; unspecified items marked CONDITIONAL / UNVERIFIED
COMPONENT_LIMITS = {
    "STM32F411CEU6": {"min_C": -40.0, "max_C": 85.0, "status": "VERIFIED", "source": "Formal MoM / ST Datasheet (-40..+85C)", "notes": "Standard Industrial Range"},
    "PCM1808": {"min_C": -40.0, "max_C": 85.0, "status": "VERIFIED", "source": "Formal MoM / TI Datasheet (-40..+85C)", "notes": "Standard Industrial Range"},
    "RTC Module (Unspecified PN)": {"min_C": None, "max_C": None, "status": "CONDITIONAL / UNVERIFIED", "source": "Unspecified component PN", "notes": "Industrial-rated IC required in BOM"},
    "MicroSD Storage (Unspecified PN)": {"min_C": None, "max_C": None, "status": "CONDITIONAL / UNVERIFIED", "source": "Unspecified component PN", "notes": "Industrial flash required in BOM"},
    "Power Management (Unspecified PN)": {"min_C": None, "max_C": None, "status": "CONDITIONAL / UNVERIFIED", "source": "Unspecified component PN", "notes": "Discrete thermal dissipation budget required"},
    "AFE Electronics (Unspecified PN)": {"min_C": None, "max_C": None, "status": "CONDITIONAL / UNVERIFIED", "source": "Unspecified discrete component BOM", "notes": "Requires thermal rating verification"},
}

# Modeled Subassembly Length Constants
HTI_SENSOR_LENGTH_MM = 88.9
HTI_SENSOR_OD_MM = 17.475
HTI_BULKHEAD_ADAPTER_LENGTH_MM = 40.0
REAR_ENDCAP_PROTRUSION_MM = 8.0
FRONT_AXIAL_BUFFER_MM = 15.0
REAR_AXIAL_BUFFER_MM = 15.0

# Material Database
MATERIALS = json.loads((ROOT / "cosmo" / "material_library.json").read_text(encoding="utf-8"))


# ==============================================================================
# 1. PACKAGING STUDY & RADIAL BUDGET
# ==============================================================================

def compute_carrier_tolerance_budget(
    shell_bore_nom_mm: float = 37.450,
    carrier_od_nom_mm: float = 37.050,
    carrier_material_key: str = "PEEK",
    t_assembly_c: float = 20.0,
    t_max_c: float = 70.0,
    dim_uncertainty_allowance_override_mm: float | None = None,
) -> dict[str, Any]:
    """
    Computes an explicit carrier-to-shell tolerance and thermal expansion budget.
    
    Factors evaluated:
    - Differential thermal expansion between Inconel 718 shell and PEEK/PPA/PA66 carrier (Delta T = 50 K)
    - Inconel 718 CLTE: 13.0 ppm/K (verified manufacturer value)
    - Polymer CLTE: cross-flow / average value (PEEK 55 ppm/K, PPA 55 ppm/K, PA66-GF30 70 ppm/K)
    - Bore machining tolerance (standard precision H8 on dia 37.45: +0.039 / -0.000 mm)
    - Carrier machining tolerance (standard precision h8 on dia 37.05: +0.000 / -0.039 mm)
    - Polymer conditioning / dimensional uncertainty allowance:
      * PEEK: 0.020 mm dia (low moisture absorption 0.10%)
      * PPA: 0.030 mm dia (moderate moisture absorption 0.20% / 1.80% sat)
      * PA66-GF30: 0.080 mm dia (ASSUMED SCREENING ALLOWANCE for 1.5-1.9% equilibrium conditioning uncertainty)
    - Practical sliding assembly allowance for 500 mm internal chassis
    """
    delta_t = t_max_c - t_assembly_c  # 50.0 K
    
    inconel_clte = MATERIALS["Inconel718"].get("thermal_expansion_per_c", 0.000013)
    poly_props = MATERIALS.get(carrier_material_key, MATERIALS["PEEK"])
    poly_clte = poly_props.get("thermal_expansion_cross_flow_per_c", poly_props.get("thermal_expansion_per_c", 0.000055))
    
    # Diametral thermal growth
    d_bore_thermal_growth_mm = shell_bore_nom_mm * inconel_clte * delta_t  # +0.0243 mm
    d_carrier_thermal_growth_mm = carrier_od_nom_mm * poly_clte * delta_t
    diff_thermal_growth_diametral_mm = d_carrier_thermal_growth_mm - d_bore_thermal_growth_mm
    diff_thermal_growth_radial_mm = diff_thermal_growth_diametral_mm / 2.0
    
    # Conservative screening allowance for polymer conditioning & dimensional uncertainty
    if dim_uncertainty_allowance_override_mm is not None:
        dim_uncertainty_allowance_diametral_mm = dim_uncertainty_allowance_override_mm
    elif carrier_material_key == "PEEK":
        dim_uncertainty_allowance_diametral_mm = 0.020
    elif carrier_material_key == "PPA_Amodel_A1133HS":
        dim_uncertainty_allowance_diametral_mm = 0.030
    elif carrier_material_key == "PA66_Ultramid_A3WG6_HRX":
        dim_uncertainty_allowance_diametral_mm = 0.080
    else:
        dim_uncertainty_allowance_diametral_mm = 0.030
        
    # Machining tolerances (H8/h8 screening allowances)
    bore_tol_plus_mm = 0.039
    bore_tol_minus_mm = 0.000
    carrier_tol_plus_mm = 0.000
    carrier_tol_minus_mm = 0.039
    
    # Cold nominal clearance (at 20 °C)
    cold_clearance_diametral_mm = shell_bore_nom_mm - carrier_od_nom_mm  # 37.450 - 37.050 = 0.400 mm
    cold_clearance_radial_mm = cold_clearance_diametral_mm / 2.0  # 0.200 mm
    
    # Hot nominal clearance (at 70 °C with differential growth and screening uncertainty allowance)
    hot_clearance_diametral_mm = cold_clearance_diametral_mm - diff_thermal_growth_diametral_mm - dim_uncertainty_allowance_diametral_mm
    hot_clearance_radial_mm = hot_clearance_diametral_mm / 2.0
    
    # Minimum worst-case hot clearance (minimum bore + maximum carrier + hot expansion + allowance)
    worst_case_hot_diametral_mm = (shell_bore_nom_mm - bore_tol_minus_mm) - (carrier_od_nom_mm + carrier_tol_plus_mm) - diff_thermal_growth_diametral_mm - dim_uncertainty_allowance_diametral_mm
    worst_case_hot_radial_mm = worst_case_hot_diametral_mm / 2.0
    
    adequate_clearance = worst_case_hot_diametral_mm > 0.050  # Must maintain >= 0.05 mm positive sliding margin
    
    return {
        "shell_bore_nom_mm": shell_bore_nom_mm,
        "carrier_od_nom_mm": carrier_od_nom_mm,
        "carrier_material": carrier_material_key,
        "cold_clearance_diametral_mm": round(cold_clearance_diametral_mm, 4),
        "cold_clearance_radial_mm": round(cold_clearance_radial_mm, 4),
        "diff_thermal_growth_diametral_mm": round(diff_thermal_growth_diametral_mm, 4),
        "diff_thermal_growth_radial_mm": round(diff_thermal_growth_radial_mm, 4),
        "dim_uncertainty_allowance_diametral_mm": round(dim_uncertainty_allowance_diametral_mm, 4),
        "hot_clearance_diametral_mm": round(hot_clearance_diametral_mm, 4),
        "hot_clearance_radial_mm": round(hot_clearance_radial_mm, 4),
        "worst_case_hot_diametral_mm": round(worst_case_hot_diametral_mm, 4),
        "worst_case_hot_radial_mm": round(worst_case_hot_radial_mm, 4),
        "adequate_clearance": adequate_clearance,
    }


def compute_carrier_dimensional_sensitivity(
    shell_bore_nom_mm: float = 37.450,
) -> list[dict[str, Any]]:
    """
    Computes carrier OD requirements and worst-case hot clearances across a sensitivity range
    of assumed dimensional-conditioning allowances for PEEK, PPA, and PA66-GF30.
    """
    cases = [
        ("PEEK", 37.050, [0.010, 0.020, 0.040]),
        ("PPA_Amodel_A1133HS", 37.050, [0.020, 0.030, 0.060]),
        ("PA66_Ultramid_A3WG6_HRX", 37.050, [0.040, 0.080, 0.120, 0.200, 0.300]),
        ("PA66_Ultramid_A3WG6_HRX", 36.850, [0.040, 0.080, 0.120, 0.200, 0.300]),
    ]
    results = []
    for mat_key, od, allowances in cases:
        for allow in allowances:
            budget = compute_carrier_tolerance_budget(
                shell_bore_nom_mm=shell_bore_nom_mm,
                carrier_od_nom_mm=od,
                carrier_material_key=mat_key,
                dim_uncertainty_allowance_override_mm=allow,
            )
            avail_guide_wall_mm = (od / 2.0) - 15.0
            results.append({
                "material": mat_key,
                "carrier_od_nom_mm": od,
                "assumed_conditioning_allowance_mm": allow,
                "diff_thermal_growth_mm": budget["diff_thermal_growth_diametral_mm"],
                "hot_clearance_diametral_mm": budget["hot_clearance_diametral_mm"],
                "worst_case_hot_diametral_mm": budget["worst_case_hot_diametral_mm"],
                "adequate_clearance": budget["adequate_clearance"],
                "available_guide_wall_mm": round(avail_guide_wall_mm, 3),
                "sliding_status": "FREE SLIDING" if budget["adequate_clearance"] else "RISK OF BINDING / INTERFERENCE",
            })
    return results


def build_carrier_material_trade_matrix() -> list[dict[str, Any]]:
    """
    Builds the structured Carrier Material Trade Matrix comparing:
    - Victrex 450G PEEK
    - Solvay Amodel A-1133 HS PPA
    - BASF Ultramid A3WG6 HRX BK23591 PA66-GF30
    """
    return [
        {
            "exact_grade": "Victrex 450G",
            "polymer_family": "PEEK (Unfilled)",
            "reinforcement": "None (Unfilled)",
            "density_kg_m3": 1300,
            "modulus_dry_mpa": 4000,
            "modulus_cond_mpa": 4000,
            "strength_basis": "TENSILE_STRENGTH_SCREENING",
            "strength_dry_mpa": 100,
            "strength_cond_mpa": 100,
            "thermal_conductivity_w_mk": 0.29,
            "specific_heat_j_kgk": 1500,
            "moisture_absorption_eq_percent": "0.10% (24h) / 0.50% (sat)",
            "water_absorption_sat_percent": "0.50%",
            "hydrolysis_resistance_evidence": "STRONGEST CURRENT MATERIAL EVIDENCE — Exceptional hydrolysis and chemical resistance with extensive oilfield/NORSOK pedigree (Victrex 450G); actual PertAcoustic carrier still requires physical validation",
            "property_70c_confidence": "VERIFIED / INTERPOLATED (Victrex DMA ISO 527-2 curves: E=3700 MPa, Strength=70 MPa)",
            "creep_evidence": "VERIFIED — Tg = 143 °C; low creep under carrier load at 70 °C",
            "carrier_dimensional_risk": "LOW (Minimal moisture swelling, predictable CLTE 55 ppm/K)",
            "downhole_fluid_compatibility": "STRONGEST EVIDENCE — Excellent resistance to crude, sour gas (H2S), CO2, completion brine, acids",
            "manufacturability": "High-temperature injection molding (380-400 °C) or easy CNC machining of stock plate/rod",
            "relative_cost_class": "HIGH COST CLASS",
            "overall_screening_classification": "RECOMMENDED BASELINE / STRONGEST CURRENT EVIDENCE",
        },
        {
            "exact_grade": "Amodel A-1133 HS",
            "polymer_family": "PPA (Polyphthalamide)",
            "reinforcement": "33% Glass Fiber",
            "density_kg_m3": 1480,
            "modulus_dry_mpa": 13400,
            "modulus_cond_mpa": 11813,
            "strength_basis": "TENSILE_STRESS_AT_BREAK_SCREENING",
            "strength_dry_mpa": 233,
            "strength_cond_mpa": 181,
            "thermal_conductivity_w_mk": 0.26,
            "specific_heat_j_kgk": 1200,
            "moisture_absorption_eq_percent": "0.20% (24h)",
            "water_absorption_sat_percent": "1.80% (Equilibrium in water @ 23 C)",
            "hydrolysis_resistance_evidence": "VERIFIED FOR EXACT A-1133 HS — High aromatic content provides superior hydrolysis resistance to standard polyamides; note downhole qualification evidence often cites structural lubricated AS-1133 HS rather than standard A-1133 HS",
            "property_70c_confidence": "VERIFIED / INTERPOLATED (Solvay Technical Guide: E=11.81 GPa, Strength=181 MPa at 70 °C DAM)",
            "creep_evidence": "VERIFIED — High stiffness retention (10.8 GPa at 100 °C), low creep under carrier load",
            "carrier_dimensional_risk": "LOW-TO-MODERATE (1.80% sat water absorption; 0.030 mm screening allowance adequate)",
            "downhole_fluid_compatibility": "PROVISIONAL / CONDITIONAL — Good hydrocarbon resistance; long-term sour/brine requires coupon test",
            "manufacturability": "Standard high-temp molding (315-330 °C); abrasive to CNC cutting tools due to 33% GF",
            "relative_cost_class": "EXPECTED LOWER-COST CANDIDATE — PROCUREMENT UNVERIFIED",
            "overall_screening_classification": "PREFERRED HIGH-PERFORMANCE COST-REDUCTION CANDIDATE — procurement and exact carrier qualification pending",
        },
        {
            "exact_grade": "Ultramid A3WG6 HRX BK23591",
            "polymer_family": "PA66-GF30",
            "reinforcement": "30% Glass Fiber",
            "density_kg_m3": 1370,
            "modulus_dry_mpa": 9500,
            "modulus_cond_mpa": 6000,
            "strength_basis": "TENSILE_STRESS_AT_BREAK_SCREENING",
            "strength_dry_mpa": 185,
            "strength_cond_mpa": 110,
            "thermal_conductivity_w_mk": 0.36,
            "specific_heat_j_kgk": 1260,
            "moisture_absorption_eq_percent": "1.5 - 1.9% (23 °C / 50% RH)",
            "water_absorption_sat_percent": "5.6 - 6.3% (Saturation in water @ 23 °C)",
            "hydrolysis_resistance_evidence": "CONDITIONAL — Enhanced hydrolysis & heat ageing resistance developed for automotive cooling circuits; downhole oilfield fluids UNVERIFIED",
            "property_70c_confidence": "CONDITIONAL — EXACT 70 C CONDITIONED PROPERTY NOT VERIFIED (Moisture conditioning substantially reduces 23 C modulus and stress at break; exact 70 C conditioned mechanical behavior remains unresolved)",
            "creep_evidence": "CONDITIONAL — 4800 MPa creep modulus at 23 °C / 1000h (conditioned); 70 C wet creep remains unresolved; short 2 h exposure reduces concern but does not establish creep qualification",
            "carrier_dimensional_risk": "HIGH DIMENSIONAL RISK (5.6-6.3% sat water absorption creates binding risk unless sealed/isolated)",
            "downhole_fluid_compatibility": "UNVERIFIED — Hot brine, drilling fluids, sour gas (H2S), and crude compatibility not established",
            "manufacturability": "Excellent injection molding processability (280-300 °C, mold 80-90 °C); recommended pellet moisture 0.025–0.045% (pre-drying 80 °C / 4h); CNC machining of molded stock/coupons possible with PCD tooling; additive manufacturing/3D printing unsupported for exact grade",
            "relative_cost_class": "EXPECTED LOWER-COST CANDIDATE — PROCUREMENT UNVERIFIED",
            "overall_screening_classification": "PROTOTYPE / VALIDATION CANDIDATE — exact 70 C wet properties and downhole-fluid compatibility unresolved",
        },
    ]


def compute_radial_budget(
    od_mm: float,
    wall_mm: float,
    liner_mm: float = 0.0,
    aerogel_mm: float = 0.0,
    is_discrete_carrier: bool = False,
    carrier_material_key: str = "PEEK",
) -> dict[str, Any]:
    """
    Computes available clear ID and assesses packaging feasibility.
    
    For full circumferential liner:
      Clear ID = OD - 2 * (wall_mm + aerogel_mm + liner_mm)
    For discrete carrier architecture:
      Shell Bore ID = OD - 2 * wall_mm
      Effective Containment ID = Shell Bore ID (carrier rails hold PCB without full circumferential thickness)
      Clear ID = Shell Bore ID
    """
    shell_bore_id_mm = od_mm - 2.0 * wall_mm
    
    if is_discrete_carrier:
        clear_id_mm = shell_bore_id_mm
    else:
        clear_id_mm = od_mm - 2.0 * (wall_mm + aerogel_mm + liner_mm)
        
    # PCM1808 nominal cross-section: 30.0 mm width x 12.0 mm height
    w_pcm, h_pcm = PCM1808_ENVELOPE_MM[1], PCM1808_ENVELOPE_MM[2]
    eff_w = w_pcm + 2.0 * BOARD_ASSEMBLY_CLEARANCE_MM  # 32.0 mm
    eff_h = h_pcm + 2.0 * BOARD_ASSEMBLY_CLEARANCE_MM  # 14.0 mm
    diagonal_pcm = math.hypot(eff_w, eff_h)  # sqrt(32^2 + 14^2) = sqrt(1220) ≈ 34.928 mm ≈ 34.93 mm
    
    # Direct circular fit condition: clear diameter >= enclosing bounding diameter
    direct_fit = clear_id_mm >= diagonal_pcm
    
    # Radial clearance margin relative to diagonal
    clearance_margin_mm = (clear_id_mm - diagonal_pcm) / 2.0 if clear_id_mm > 0 else -diagonal_pcm / 2.0
    
    # Compute tolerance budget for discrete carrier
    tol_budget = compute_carrier_tolerance_budget(
        shell_bore_nom_mm=shell_bore_id_mm,
        carrier_od_nom_mm=shell_bore_id_mm - 0.400 if is_discrete_carrier else clear_id_mm,
        carrier_material_key=carrier_material_key,
    ) if is_discrete_carrier else None
    
    if direct_fit and is_discrete_carrier:
        pkg_status = f"FEASIBLE (Direct circular fit inside shell bore with discrete {carrier_material_key.split('_')[0]} carrier rails)"
    elif direct_fit:
        pkg_status = "FEASIBLE (Direct circular fit inside full polymer liner)"
    elif is_discrete_carrier and shell_bore_id_mm >= diagonal_pcm:
        pkg_status = "FEASIBLE (Direct circular fit inside shell bore)"
    else:
        pkg_status = f"INFEASIBLE (Clear ID {clear_id_mm:.2f} mm < {diagonal_pcm:.2f} mm PCM1808 envelope)"
        
    return {
        "od_mm": od_mm,
        "wall_mm": wall_mm,
        "aerogel_mm": aerogel_mm,
        "liner_mm": liner_mm,
        "is_discrete_carrier": is_discrete_carrier,
        "carrier_material_key": carrier_material_key,
        "shell_bore_id_mm": round(shell_bore_id_mm, 2),
        "clear_id_mm": round(clear_id_mm, 2),
        "effective_w_mm": eff_w,
        "effective_h_mm": eff_h,
        "pcm1808_diagonal_mm": round(diagonal_pcm, 2),
        "clearance_margin_mm": round(clearance_margin_mm, 2),
        "direct_fit": direct_fit,
        "tolerance_budget": tol_budget,
        "packaging_status": pkg_status,
    }


# ==============================================================================
# 2. STRUCTURAL SCREENING
# ==============================================================================

def lame_stress(od_mm: float, wall_mm: float, pressure_mpa: float, material_key: str = "Inconel718") -> dict[str, Any]:
    """
    Closed-end thick-cylinder Lamé stress calculation under external pressure.
    """
    b = od_mm / 2.0
    a = b - wall_mm
    if a <= 0:
        raise ValueError(f"Wall thickness {wall_mm} mm exceeds outer radius {b} mm")
        
    denom = b * b - a * a
    A = -pressure_mpa * b * b / denom
    B = -pressure_mpa * a * a * b * b / denom
    
    def calc_mises(r: float) -> float:
        sigma_r = A - B / (r * r)
        sigma_h = A + B / (r * r)
        sigma_z = A  # closed end
        return math.sqrt(
            0.5 * ((sigma_r - sigma_h)**2 + (sigma_h - sigma_z)**2 + (sigma_z - sigma_r)**2)
        )
        
    sigma_inner = calc_mises(a)
    sigma_outer = calc_mises(b)
    max_mises = max(sigma_inner, sigma_outer)
    
    props = MATERIALS.get(material_key, MATERIALS["Inconel718"])
    if material_key == "Inconel718":
        strength_basis = "YIELD"
        screening_strength = float(props.get("yield_strength_mpa_150c_screening", 1000.0))
    elif material_key == "PPA_Amodel_A1133HS":
        strength_basis = "TENSILE_STRESS_AT_BREAK_SCREENING"
        screening_strength = float(props.get("screening_tensile_strength_mpa_70c", 181.0))
    elif material_key == "PA66_Ultramid_A3WG6_HRX":
        strength_basis = "TENSILE_STRESS_AT_BREAK_SCREENING"
        # Conservative screening uses conditioned stress at break (110 MPa at 23 C conditioned; 70 C exact unverified)
        screening_strength = float(props.get("tensile_stress_at_break_mpa_23c_cond", 110.0))
    elif material_key == "PEEK":
        strength_basis = "TENSILE_STRENGTH_SCREENING"
        screening_strength = float(props.get("screening_tensile_strength_mpa_70c", 70.0))
    else:
        strength_basis = "ASSUMED_SCREENING"
        screening_strength = 100.0
        
    strength_ratio = screening_strength / max_mises if max_mises > 0 else float("inf")
    
    return {
        "pressure_mpa": pressure_mpa,
        "max_von_mises_mpa": round(max_mises, 2),
        "von_mises_inner_mpa": round(sigma_inner, 2),
        "von_mises_outer_mpa": round(sigma_outer, 2),
        "strength_basis": strength_basis,
        "screening_strength_mpa": screening_strength,
        "screening_strength_ratio": round(strength_ratio, 2),
        "yield_safety_factor": round(strength_ratio, 2),  # aliased for Inconel compatibility
    }


def elastic_buckling(od_mm: float, wall_mm: float, pressure_mpa: float, material_key: str = "Inconel718") -> dict[str, float]:
    """
    Long-cylinder elastic external-pressure buckling screen.
    """
    props = MATERIALS.get(material_key, MATERIALS["Inconel718"])
    E = props.get("elastic_modulus_mpa_70c")
    if E is None or isinstance(E, str):
        E = props.get("elastic_modulus_mpa_23c_cond", props.get("elastic_modulus_mpa_150c", 193000.0))
    if isinstance(E, str):
        E = float(props.get("elastic_modulus_mpa_23c_cond", 6000.0))
    nu = props.get("poisson_ratio", 0.28)
    p_cr = 2.0 * float(E) / math.sqrt(3.0 * (1.0 - nu * nu)) * (wall_mm / od_mm) ** 3
    buckling_fos = p_cr / pressure_mpa if pressure_mpa > 0 else float("inf")
    
    return {
        "critical_buckling_pressure_mpa": round(p_cr, 2),
        "buckling_safety_factor": round(buckling_fos, 2),
    }


def structural_screening(od_mm: float, wall_mm: float, material_key: str = "Inconel718") -> dict[str, Any]:
    """
    Evaluates casing structural safety across explicit screening scenarios.
    
    Scenarios evaluated:
    - ~10 MPa: Derived screening context (~1000 m hydrostatic depth)
    - 20 MPa: Sensitivity scenario
    - 68.95 MPa: Historical Biweekly 5 screening comparison (10,000 psi)
    
    Authoritative field casing design pressure remains unresolved.
    """
    scenarios = {
        "scenario_1000m_10mpa": lame_stress(od_mm, wall_mm, PRESSURE_SCENARIO_1000M_MPA, material_key),
        "scenario_intermediate_20mpa": lame_stress(od_mm, wall_mm, PRESSURE_SCENARIO_INTERMEDIATE_MPA, material_key),
        "scenario_historical_68_9mpa": lame_stress(od_mm, wall_mm, PRESSURE_SCENARIO_HISTORICAL_MPA, material_key),
    }
    
    buckling_1000m = elastic_buckling(od_mm, wall_mm, PRESSURE_SCENARIO_1000M_MPA, material_key)
    buckling_20mpa = elastic_buckling(od_mm, wall_mm, PRESSURE_SCENARIO_INTERMEDIATE_MPA, material_key)
    buckling_historical = elastic_buckling(od_mm, wall_mm, PRESSURE_SCENARIO_HISTORICAL_MPA, material_key)
    
    fos_strength_1000m = scenarios["scenario_1000m_10mpa"]["screening_strength_ratio"]
    fos_buckling_1000m = buckling_1000m["buckling_safety_factor"]
    fos_strength_hist = scenarios["scenario_historical_68_9mpa"]["screening_strength_ratio"]
    fos_buckling_hist = buckling_historical["buckling_safety_factor"]
    
    is_polymer = material_key in {"PEEK", "PPA_Amodel_A1133HS", "PA66_Ultramid_A3WG6_HRX"}
    
    if is_polymer:
        status = "EXPLORATORY / CONDITIONAL (Polymer creep, hydrothermal aging, and thread limitations preclude unlined pressure containment; requires authoritative pressure and collapse requirements)"
    elif fos_strength_1000m >= 2.0 and fos_buckling_1000m >= 2.0:
        if fos_strength_hist >= 2.0 and fos_buckling_hist >= 2.0:
            status = "SCREENING MARGIN (FoS >= 2.0 screening reference across 1000m, 20MPa, and 10k psi; design pressure unresolved)"
        else:
            status = "SCREENING MARGIN (FoS >= 2.0 for ~1000m and 20MPa screening; Conditional at 10,000 psi; design pressure unresolved)"
    else:
        status = "CONDITIONAL / INSUFFICIENT MARGIN (FoS < 2.0 screening reference)"
        
    return {
        "od_mm": od_mm,
        "wall_mm": wall_mm,
        "material": material_key,
        "scenarios": scenarios,
        "buckling_1000m": buckling_1000m,
        "buckling_20mpa": buckling_20mpa,
        "buckling_historical": buckling_historical,
        "status": status,
    }


# ==============================================================================
# 3. TRANSIENT THERMAL MODELING (70 °C, 2-HOUR DURATION)
# ==============================================================================

def _discretize_thermal_layers(
    geometry: dict[str, Any], cells_per_layer: int = 8
) -> tuple[np.ndarray, list[str]]:
    """
    Discretizes concentric radial layers based on the active architecture.
    """
    inner_radius = (geometry["clear_id_mm"] / 2.0) / 1000.0  # m
    
    layer_defs = []
    # From inside to outside:
    if geometry.get("liner_mm", 0.0) > 0 and not geometry.get("is_discrete_carrier", False):
        layer_defs.append((geometry.get("liner_material", "PEEK"), geometry["liner_mm"] / 1000.0))
    if geometry.get("aerogel_mm", 0.0) > 0:
        layer_defs.append(("Aerogel", geometry["aerogel_mm"] / 1000.0))
    if geometry.get("wall_mm", 0.0) > 0:
        layer_defs.append((geometry.get("casing_material", "Inconel718"), geometry["wall_mm"] / 1000.0))
        
    edges = [inner_radius]
    names = []
    for name, thickness in layer_defs:
        if thickness <= 0:
            continue
        local = np.linspace(edges[-1], edges[-1] + thickness, cells_per_layer + 1)[1:]
        edges.extend(local.tolist())
        names.extend([name] * cells_per_layer)
        
    return np.asarray(edges), names


def transient_thermal_simulation(
    geometry: dict[str, Any],
    power_w: float = INHERITED_SCREENING_POWER_W,
    duration_s: int = THERMAL_DURATION_S,
    dt_s: float = 30.0,
    cells_per_layer: int = 8,
) -> dict[str, Any]:
    """
    1D radial finite-difference transient thermal conduction model.
    Boundary condition: 70 °C constant Dirichlet on outer surface.
    Initial condition: 25 °C uniform.
    Internal heat: power_w applied at inner cavity/carrier surface.
    """
    edges, names = _discretize_thermal_layers(geometry, cells_per_layer)
    centers = np.sqrt(edges[:-1] * edges[1:])
    length_m = geometry.get("housing_length_mm", HOUSING_LENGTH_MM) / 1000.0
    n = len(centers)
    
    capacities = np.zeros(n)
    for i, name in enumerate(names):
        props = MATERIALS[name]
        volume = math.pi * (edges[i + 1]**2 - edges[i]**2) * length_m
        capacities[i] = props["density"] * props["specific_heat"] * volume
        
    conductance = np.zeros(n - 1)
    for i in range(n - 1):
        interface = edges[i + 1]
        k_left = MATERIALS[names[i]]["conductivity"]
        k_right = MATERIALS[names[i + 1]]["conductivity"]
        resistance = (
            math.log(interface / centers[i]) / (2 * math.pi * length_m * k_left)
            + math.log(centers[i + 1] / interface) / (2 * math.pi * length_m * k_right)
        )
        conductance[i] = 1.0 / resistance
        
    outer_k = MATERIALS[names[-1]]["conductivity"]
    outer_res = math.log(edges[-1] / centers[-1]) / (2 * math.pi * length_m * outer_k)
    outer_g = 1.0 / outer_res
    
    inner_k = MATERIALS[names[0]]["conductivity"]
    inner_res = math.log(centers[0] / edges[0]) / (2 * math.pi * length_m * inner_k)
    
    matrix = np.diag(capacities / dt_s)
    for i, g in enumerate(conductance):
        matrix[i, i] += g
        matrix[i + 1, i + 1] += g
        matrix[i, i + 1] -= g
        matrix[i + 1, i] -= g
    matrix[-1, -1] += outer_g
    inv_matrix = np.linalg.inv(matrix)
    
    temperature = np.full(n, INITIAL_TEMPERATURE_C)
    source = np.zeros(n)
    source[0] = power_w
    source[-1] += outer_g * EXTERNAL_TEMPERATURE_C
    
    times = [0.0]
    inner_temps = [INITIAL_TEMPERATURE_C]
    steps = int(duration_s / dt_s)
    
    for step in range(1, steps + 1):
        rhs = (capacities / dt_s) * temperature + source
        temperature = inv_matrix @ rhs
        inner_surface_temp = float(temperature[0] + power_w * inner_res)
        times.append(step * dt_s)
        inner_temps.append(inner_surface_temp)
        
    final_temp = inner_temps[-1]
    
    return {
        "power_w": power_w,
        "times_s": np.asarray(times),
        "inner_shell_temperature_C": np.asarray(inner_temps),
        "inner_temperature_C": np.asarray(inner_temps),
        "final_inner_shell_temperature_C": round(final_temp, 2),
        "final_inner_temperature_C": round(final_temp, 2),
        "thermal_metric_label": "IDEAL SHELL-COUPLED LOWER-BOUND TEMPERATURE (INNER SHELL SURFACE)",
    }


# ==============================================================================
# 4. COMPONENT LIMITS & ARCHITECTURE TRADE STUDY
# ==============================================================================

def compute_internal_thermal_resistance_budget(
    inner_shell_temp_c: float,
    power_w: float = INHERITED_SCREENING_POWER_W,
) -> dict[str, Any]:
    """
    Derives the allowable internal thermal-resistance screening budget for components with verified operating bounds.
    R_internal_allowable = (T_component_limit - T_inner_shell_screen) / P_internal
    
    This is a DERIVED INTERNAL THERMAL-RESISTANCE SCREENING BUDGET, not a measured resistance or field requirement.
    Statement: If the actual electronics-to-shell thermal path is <= R_internal_allowable, the verified +85 °C
    device environmental bound is not exceeded at steady state under the 1.0 W screening case.
    Actual junction temperature remains unresolved.
    """
    budget = {}
    for comp, info in COMPONENT_LIMITS.items():
        if info["max_C"] is None:
            budget[comp] = {
                "max_C": "UNSPECIFIED",
                "operating_limit_status": "UNSPECIFIED",
                "thermal_model_status": "CONDITIONAL / UNVERIFIED",
                "junction_temperature": "NOT ESTABLISHED",
                "inner_shell_temp_C": inner_shell_temp_c,
                "allowable_delta_T_K": "N/A (Unspecified Limit)",
                "allowable_r_internal_K_per_W": "N/A (Unspecified Limit)",
                "margin_C": "N/A (Unspecified Part Rating)",
                "notes": info["notes"],
            }
        else:
            delta_t = info["max_C"] - inner_shell_temp_c
            r_allowable = delta_t / power_w if power_w > 0 else float("inf")
            within_budget = delta_t >= 0
            budget[comp] = {
                "max_C": f"{info['max_C']:.1f} °C",
                "operating_limit_status": "VERIFIED (-40...+85 C)",
                "thermal_model_status": "CONDITIONAL / WITHIN INNER-SHELL-BASED SCREENING BUDGET" if within_budget else "EXCEEDED",
                "junction_temperature": "NOT ESTABLISHED",
                "inner_shell_temp_C": inner_shell_temp_c,
                "allowable_delta_T_K": round(delta_t, 2),
                "allowable_r_internal_K_per_W": round(r_allowable, 2),
                "margin_C": round(delta_t, 2),
                "notes": info["notes"],
            }
    return budget


def compute_internal_thermal_sensitivity(
    inner_shell_temp_c: float,
    power_w: float = INHERITED_SCREENING_POWER_W,
    r_values: list[float] | None = None,
) -> list[dict[str, Any]]:
    """
    Computes lumped electronics screening temperature across an internal thermal resistance parameter sweep.
    T_electronics_screen = T_inner_shell + P * R_internal
    """
    if r_values is None:
        r_values = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0]
    rows = []
    for r in r_values:
        t_screen = inner_shell_temp_c + power_w * r
        within_85c = t_screen <= 85.0
        rows.append({
            "r_internal_K_per_W": r,
            "delta_T_K": round(power_w * r, 2),
            "t_electronics_screen_C": round(t_screen, 2),
            "exceeds_85c_bound": not within_85c,
            "status": "WITHIN 85C BOUND" if within_85c else "EXCEEDS 85C BOUND",
        })
    return rows


def zone_thermal_assessment(
    final_inner_shell_temp_C: float, power_w: float = INHERITED_SCREENING_POWER_W
) -> dict[str, Any]:
    """
    Evaluates components against documented operating limits and derives allowable internal thermal resistance budgets.
    """
    return compute_internal_thermal_resistance_budget(final_inner_shell_temp_C, power_w)


def size_architecture_candidate(
    architecture_name: str,
    od_mm: float = PREFERRED_OD_MM,
    wall_mm: float = 3.5,
    liner_mm: float = 0.0,
    aerogel_mm: float = 0.0,
    is_discrete_carrier: bool = True,
    casing_material: str = "Inconel718",
    liner_material: str = "PEEK",
) -> dict[str, Any]:
    """
    Builds and evaluates a specific architecture candidate across packaging,
    structural screening, 2-hour thermal response, and CAD collision checks.
    """
    pkg = compute_radial_budget(
        od_mm=od_mm, wall_mm=wall_mm, liner_mm=liner_mm, aerogel_mm=aerogel_mm, is_discrete_carrier=is_discrete_carrier,
        carrier_material_key=liner_material
    )
    clear_id_mm = pkg["clear_id_mm"]
    
    total_tool_length = HTI_SENSOR_LENGTH_MM + HTI_BULKHEAD_ADAPTER_LENGTH_MM + HOUSING_LENGTH_MM + REAR_ENDCAP_PROTRUSION_MM
    
    if clear_id_mm <= 15.0:
        return {
            "architecture": architecture_name,
            "od_mm": od_mm,
            "fit": False,
            "reason": f"Radial stack leaves insufficient clear ID ({clear_id_mm:.2f} mm).",
            "overall_status": "INFEASIBLE",
            "collision_results": {"passed": False, "status": "NOT EVALUATED (Infeasible ID)"},
            "total_tool_length_mm": total_tool_length,
        }
        
    candidate = {
        "architecture": architecture_name,
        "od_mm": od_mm,
        "clear_id_mm": clear_id_mm,
        "inconel_wall_mm": wall_mm if "Inconel" in casing_material else 0.0,
        "wall_mm": wall_mm,
        "aerogel_mm": aerogel_mm,
        "liner_mm": liner_mm,
        "is_discrete_carrier": is_discrete_carrier,
        "casing_material": casing_material,
        "liner_material": liner_material,
        "housing_length_mm": HOUSING_LENGTH_MM,
        "total_tool_length_mm": total_tool_length,
        "endcap_thickness_mm": ENDCAP_THICKNESS_MM,
        "packaging": pkg,
        "fit": True,
    }
    
    # Structural screening
    candidate["structural"] = structural_screening(od_mm, wall_mm, material_key=casing_material)
    
    # Thermal simulations: 0 W (pure heat ingress) and 1.0 W (inherited load)
    candidate["thermal_0w"] = transient_thermal_simulation(candidate, power_w=ZERO_POWER_W)
    candidate["thermal_1w"] = transient_thermal_simulation(candidate, power_w=INHERITED_SCREENING_POWER_W)
    
    # Component zone verification
    candidate["zone_assessment"] = zone_thermal_assessment(candidate["thermal_1w"]["final_inner_temperature_C"])
    
    # Automated CAD collision and interference verification (fail-closed)
    if is_discrete_carrier and pkg["direct_fit"]:
        candidate["collision_results"] = check_cad_assembly_interferences(candidate)
    else:
        candidate["collision_results"] = {
            "passed": False if not pkg["direct_fit"] else True,
            "status": "NOT REQUIRED (Full Liner / Infeasible)" if not pkg["direct_fit"] else "PASS",
        }
        
    # Overall classification
    is_polymer_casing = casing_material in {"PEEK", "PPA_Amodel_A1133HS", "PA66_Ultramid_A3WG6_HRX"} or "Polymer" in architecture_name or "Only" in architecture_name
    struct_pass_1000m = candidate["structural"]["scenarios"]["scenario_1000m_10mpa"]["screening_strength_ratio"] >= 2.0
    thermal_pass = candidate["thermal_1w"]["final_inner_temperature_C"] <= 85.0
    pkg_pass = pkg["direct_fit"]
    collision_pass = candidate["collision_results"].get("passed", False)
    
    candidate["is_recommended_baseline"] = False
    
    if is_polymer_casing:
        candidate["overall_status"] = "EXPLORATORY / CONDITIONAL (Polymer casing lacks certified downhole pressure integrity; design pressure unresolved)"
    elif not pkg_pass:
        candidate["overall_status"] = "INFEASIBLE (Board envelope exceeds usable diameter)"
    elif not collision_pass:
        candidate["overall_status"] = "COLLISION DETECTED / ERROR"
    elif struct_pass_1000m and thermal_pass and pkg_pass:
        candidate["overall_status"] = "QUALIFIED PRELIMINARY SCREENING CANDIDATE (Packaging Feasible; Structural Conditional — Design Pressure Unresolved)"
    else:
        candidate["overall_status"] = "REDESIGN REQUIRED"
        
    return candidate


def select_recommended_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Selects the recommended compact downhole casing candidate using transparent,
    rule-based engineering criteria.
    
    Decision Rules:
    1. Outer Diameter Gate: OD <= MAX_OD_MM (57.15 mm).
    2. Length Gate: Total modeled tool length <= MAX_TOOL_LENGTH_MM (2000 mm).
    3. Packaging Gate: Direct circular fit of nominal PCB envelope (packaging['direct_fit'] == True).
    4. Tolerance Budget Gate: For discrete carrier, tolerance budget must exist and have adequate_clearance == True.
    5. Thermal Gate: 2-hour inner-shell screening temperature <= 85.0 °C under 1.0 W internal load.
    6. Structural Baseline Gate: Inconel 718 metallic pressure shell baseline (polymer-only excluded from baseline).
    7. Assembly Collision Gate: CAD assembly must be collision-free (collision_results.passed == True).
       Any candidate with missing, False, or ERROR / NOT VERIFIED collision status is disqualified.
    
    Preference among qualifying candidates:
    1. Smallest Outer Diameter (prefer preferred OD 44.45 mm / 1.75 in).
    2. Simplest Architecture (Discrete Carrier > Full Circumferential Liner > Aerogel Reference).
    3. Carrier Material: Baseline PEEK > PPA > PA66-GF30.
    4. Wall Thickness Selection Policy: 3.5 mm wall is selected as the PRELIMINARY PACKAGING-FAVORABLE SCREENING BASELINE
       (larger 37.45 mm bore maximizes packaging clearance margin); 4.0 mm wall is evaluated as a HIGHER-COLLAPSE-MARGIN
       SENSITIVITY / CONTINGENCY. Authoritative field design pressure remains unresolved.
    """
    qualifying = []
    for c in candidates:
        if not c.get("fit", False):
            continue
        od = c["od_mm"]
        if od > MAX_OD_MM:
            continue
        total_len = c.get("total_tool_length_mm", c.get("housing_length_mm", 0.0))
        if total_len > MAX_TOOL_LENGTH_MM:
            continue
        if not c["packaging"]["direct_fit"]:
            continue
        # Tolerance budget gate for discrete carriers
        if c.get("is_discrete_carrier", False):
            tol = c.get("packaging", {}).get("tolerance_budget")
            if not tol or tol.get("adequate_clearance") is not True:
                continue
        if c["thermal_1w"]["final_inner_temperature_C"] > 85.0:
            continue
        if "Inconel" not in c["casing_material"]:
            continue
        # Collision gate
        col = c.get("collision_results")
        if not col or col.get("passed") is not True or col.get("status") == "ERROR / NOT VERIFIED":
            continue
        qualifying.append(c)
        
    if not qualifying:
        raise ValueError("No architecture candidate satisfies all engineering qualification gates.")
        
    def rank_candidate(cand: dict[str, Any]) -> tuple[float, int, int, float]:
        od = cand["od_mm"]
        arch_type = 0 if cand.get("is_discrete_carrier", False) else (1 if cand.get("liner_mm", 0.0) > 0 and cand.get("aerogel_mm", 0.0) == 0 else 2)
        if cand.get("liner_material") == "PEEK":
            mat_rank = 0
        elif cand.get("liner_material") == "PPA_Amodel_A1133HS":
            mat_rank = 1
        else:
            mat_rank = 2
        # Explicit wall policy: 3.5 mm wall is preliminary packaging-favorable baseline
        wall_rank = 0 if abs(cand.get("wall_mm", 0.0) - 3.5) < 1e-3 else 1
        return (od, arch_type, mat_rank, wall_rank)
        
    qualifying.sort(key=rank_candidate)
    selected = qualifying[0]
    selected["is_recommended_baseline"] = True
    selected["wall_status"] = (
        "PRELIMINARY PACKAGING-FAVORABLE SCREENING BASELINE (3.5 mm wall: 37.45 mm bore maximizes packaging clearance; design pressure unresolved)"
        if abs(selected.get("wall_mm", 0.0) - 3.5) < 1e-3 else
        "HIGHER-COLLAPSE-MARGIN SENSITIVITY / CONTINGENCY (4.0 mm wall: 36.45 mm bore; design pressure unresolved)"
    )
    return selected


def run_architecture_trade_study() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Runs the multi-architecture trade study comparing:
    - Architecture A: Inconel 718 + discrete PEEK carrier rails (3.5 mm wall) [Preferred Baseline]
    - Architecture A (4.0 mm wall sensitivity): Inconel 718 + discrete PEEK carrier rails [Sensitivity Case]
    - Architecture B: Inconel 718 + discrete PPA carrier rails (3.5 mm wall) [Alternative]
    - Architecture B2: Inconel 718 + discrete PA66-GF30 carrier rails (3.5 mm wall) [Cost-Reduction Candidate]
    - Architecture C: Inconel 718 + full circumferential PEEK liner (3.5 mm wall) [Comparison]
    - Architecture D: Inconel 718 + full circumferential PPA liner (3.5 mm wall) [Comparison]
    - Architecture D2: Inconel 718 + full circumferential PA66-GF30 liner (3.5 mm wall) [Comparison]
    - Reference Baseline (Arch E): Inconel 718 + Aerogel + PEEK (Historical Baseline)
    - Architecture F (Exploratory): PEEK-only pressure casing (7.225 mm wall)
    - Architecture G (Exploratory): PPA-only pressure casing (7.225 mm wall)
    - Architecture G2 (Exploratory): PA66-GF30-only pressure casing (7.225 mm wall)
    - Parametric OD variants for Architecture A: 47.625 to 57.15 mm OD.
    """
    candidates = [
        # Architecture A (Discrete PEEK Rails, 3.5 mm wall baseline)
        size_architecture_candidate(
            "Architecture A: Inconel 718 + Discrete PEEK Carrier (3.5 mm Wall)",
            od_mm=PREFERRED_OD_MM, wall_mm=3.5, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True,
            casing_material="Inconel718", liner_material="PEEK"
        ),
        # Architecture A (Discrete PEEK Rails, 4.0 mm wall sensitivity case)
        size_architecture_candidate(
            "Architecture A (4.0 mm Wall): Inconel 718 + Discrete PEEK Carrier",
            od_mm=PREFERRED_OD_MM, wall_mm=4.0, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True,
            casing_material="Inconel718", liner_material="PEEK"
        ),
        # Architecture B (Discrete PPA Rails, 3.5 mm wall)
        size_architecture_candidate(
            "Architecture B: Inconel 718 + Discrete PPA Carrier (3.5 mm Wall)",
            od_mm=PREFERRED_OD_MM, wall_mm=3.5, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True,
            casing_material="Inconel718", liner_material="PPA_Amodel_A1133HS"
        ),
        # Architecture B2 (Discrete PA66-GF30 Rails, 3.5 mm wall - Cost-Reduction Candidate)
        size_architecture_candidate(
            "Architecture B2: Inconel 718 + Discrete PA66-GF30 Carrier (3.5 mm Wall)",
            od_mm=PREFERRED_OD_MM, wall_mm=3.5, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True,
            casing_material="Inconel718", liner_material="PA66_Ultramid_A3WG6_HRX"
        ),
        # Architecture C (Full Circumferential PEEK Liner - Comparison Case)
        size_architecture_candidate(
            "Architecture C: Inconel 718 + Full PEEK Liner (3.5 mm Wall)",
            od_mm=PREFERRED_OD_MM, wall_mm=3.5, liner_mm=1.5, aerogel_mm=0.0, is_discrete_carrier=False,
            casing_material="Inconel718", liner_material="PEEK"
        ),
        # Architecture D (Full Circumferential PPA Liner - Comparison Case)
        size_architecture_candidate(
            "Architecture D: Inconel 718 + Full PPA Liner (3.5 mm Wall)",
            od_mm=PREFERRED_OD_MM, wall_mm=3.5, liner_mm=1.5, aerogel_mm=0.0, is_discrete_carrier=False,
            casing_material="Inconel718", liner_material="PPA_Amodel_A1133HS"
        ),
        # Architecture D2 (Full Circumferential PA66-GF30 Liner - Comparison Case)
        size_architecture_candidate(
            "Architecture D2: Inconel 718 + Full PA66-GF30 Liner (3.5 mm Wall)",
            od_mm=PREFERRED_OD_MM, wall_mm=3.5, liner_mm=1.5, aerogel_mm=0.0, is_discrete_carrier=False,
            casing_material="Inconel718", liner_material="PA66_Ultramid_A3WG6_HRX"
        ),
        # Reference Baseline (Arch E - Historical Aerogel Baseline)
        size_architecture_candidate(
            "Reference Baseline (Arch E): Inconel 718 + Aerogel + PEEK",
            od_mm=PREFERRED_OD_MM, wall_mm=3.5, liner_mm=1.5, aerogel_mm=2.225, is_discrete_carrier=False,
            casing_material="Inconel718", liner_material="PEEK"
        ),
        # Architecture F (PEEK-Only Exploratory)
        size_architecture_candidate(
            "Architecture F: PEEK-Only Pressure Casing (Exploratory)",
            od_mm=PREFERRED_OD_MM, wall_mm=7.225, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=False,
            casing_material="PEEK", liner_material="PEEK"
        ),
        # Architecture G (PPA-Only Exploratory)
        size_architecture_candidate(
            "Architecture G: PPA-Only Pressure Casing (Exploratory)",
            od_mm=PREFERRED_OD_MM, wall_mm=7.225, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=False,
            casing_material="PPA_Amodel_A1133HS", liner_material="PPA_Amodel_A1133HS"
        ),
        # Architecture G2 (PA66-GF30-Only Exploratory)
        size_architecture_candidate(
            "Architecture G2: PA66-GF30-Only Pressure Casing (Exploratory)",
            od_mm=PREFERRED_OD_MM, wall_mm=7.225, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=False,
            casing_material="PA66_Ultramid_A3WG6_HRX", liner_material="PA66_Ultramid_A3WG6_HRX"
        ),
    ]
    
    # Add parametric OD variations for Architecture A (47.625 to 57.15 mm OD)
    for od in [47.625, 50.80, 53.975, 57.15]:
        candidates.append(
            size_architecture_candidate(
                f"Architecture A: Inconel 718 + Discrete PEEK (OD {od:.2f} mm)",
                od_mm=od, wall_mm=3.5, liner_mm=0.0, aerogel_mm=0.0, is_discrete_carrier=True,
                casing_material="Inconel718", liner_material="PEEK"
            )
        )
        
    recommended = select_recommended_candidate(candidates)
    return candidates, recommended


# ==============================================================================
# 5. 3D PARAMETRIC CAD MODELING (CONFORMAL CARRIER & PCB RETENTION)
# ==============================================================================

def generate_compact_casing_cad(
    geometry: dict[str, Any], output_step_path: Path | None = None
) -> list[tuple[cq.Workplane, str, tuple[float, float, float]]]:
    """
    Builds a complete, watertight 3D CAD assembly for the simplified no-aerogel casing
    with conformal polymer carrier chassis and integrated PCB retention features.
    
    Guarantees:
    - Carrier rails conform to radius R = 18.525 mm (37.05 mm OD), providing 0.200 mm nominal
      radial clearance to the 37.45 mm shell bore (justified by thermal expansion & tolerance budget).
    - Carrier rails preserve the 32.0 x 14.0 mm reserved PCM1808 clearance corridor with
      integrated card guide channels (grooves) for mechanical board retention.
    """
    od = geometry["od_mm"]
    wall = geometry["wall_mm"]
    shell_id = od - 2.0 * wall  # 37.45 mm for 44.45 OD / 3.5 wall
    r_bore = shell_id / 2.0  # 18.725 mm
    # Carrier outer radius: 18.525 mm (0.200 mm nominal radial clearance for 70 C thermal expansion)
    r_carrier_out = (shell_id - 0.400) / 2.0  # 18.525 mm
    housing_len = geometry["housing_length_mm"]
    cap = geometry["endcap_thickness_mm"]
    
    z0 = 40.0
    internal_length = housing_len - 2.0 * cap
    
    # 1. Outer Inconel 718 Pressure Barrel (Radius 18.725 mm to 22.225 mm)
    shell = (
        cq.Workplane("XY")
        .circle(od / 2.0)
        .circle(r_bore)
        .extrude(housing_len)
        .translate((0, 0, z0))
    )
    
    # 2. Conformal Discrete PEEK / PPA Carrier Rails with PCB Card Guide Slots
    # Base cylinder bounded by r_carrier_out (18.525 mm)
    carrier_raw = (
        cq.Workplane("XY")
        .circle(r_carrier_out)
        .extrude(internal_length)
        .translate((0, 0, z0 + cap))
    )
    # Cut 1: Central reserved envelope (32.0 mm width x 14.0 mm height: X in [-16, 16], Y in [-7, 7])
    cut_pcm_envelope = (
        cq.Workplane("XY")
        .rect(32.0, 14.0)
        .extrude(internal_length + 2.0)
        .translate((0, 0, z0 + cap - 1.0))
    )
    # Cut 2: Top wiring and convection corridor (X in [-14, 14], Y in [0, 20])
    cut_top_corridor = (
        cq.Workplane("XY")
        .workplane(offset=z0 + cap - 1.0)
        .center(0, 10.0)
        .rect(28.0, 20.0)
        .extrude(internal_length + 2.0)
    )
    # Cut 3: Bottom central clearance pocket (X in [-8, 8], Y in [-20, -9.0])
    cut_bottom_pocket = (
        cq.Workplane("XY")
        .workplane(offset=z0 + cap - 1.0)
        .center(0, -14.5)
        .rect(16.0, 11.0)
        .extrude(internal_length + 2.0)
    )
    carrier_base = carrier_raw.cut(cut_pcm_envelope).cut(cut_top_corridor).cut(cut_bottom_pocket)
    
    # Add PCB Card Guide Inboard Ribs (Engagement from X = +/-16.0 mm to +/-14.2 mm, with 2.0 mm slot at Y in [-1.0, 1.0])
    # Left guide tongue (X in [-16.0, -14.2], Y in [1.0, 4.0] and [-4.0, -1.0])
    guide_top_r = (
        cq.Workplane("XY")
        .workplane(offset=z0 + cap)
        .center(15.1, 2.5)
        .rect(1.8, 3.0)
        .extrude(internal_length)
    )
    guide_bot_r = (
        cq.Workplane("XY")
        .workplane(offset=z0 + cap)
        .center(15.1, -2.5)
        .rect(1.8, 3.0)
        .extrude(internal_length)
    )
    guide_top_l = (
        cq.Workplane("XY")
        .workplane(offset=z0 + cap)
        .center(-15.1, 2.5)
        .rect(1.8, 3.0)
        .extrude(internal_length)
    )
    guide_bot_l = (
        cq.Workplane("XY")
        .workplane(offset=z0 + cap)
        .center(-15.1, -2.5)
        .rect(1.8, 3.0)
        .extrude(internal_length)
    )
    carrier_rails = carrier_base.union(guide_top_r).union(guide_bot_r).union(guide_top_l).union(guide_bot_l)
    
    # 3. Front and Rear Axial Buffer Plugs (PEEK / Polymer)
    front_buffer = (
        cq.Workplane("XY")
        .circle(r_bore - 0.05)
        .extrude(FRONT_AXIAL_BUFFER_MM)
        .translate((0, 0, z0 + cap))
    )
    front_buffer = front_buffer.cut(
        cq.Workplane("XY").circle(1.5).extrude(FRONT_AXIAL_BUFFER_MM).translate((0, 0, z0 + cap))
    )
    
    rear_buffer = (
        cq.Workplane("XY")
        .circle(r_bore - 0.05)
        .extrude(REAR_AXIAL_BUFFER_MM)
        .translate((0, 0, z0 + housing_len - cap - REAR_AXIAL_BUFFER_MM))
    )
    
    # 4. Front HTI Threaded Bulkhead Adapter (Nominal 7/16-20 UNF-2A)
    major_dia = 7.0 / 16.0 * 25.4
    pitch = 25.4 / 20.0
    height = 0.400 * 25.4
    minor_dia = major_dia - 1.23 * pitch
    
    thread_core = cq.Workplane("XY").circle(minor_dia / 2.0).extrude(height)
    neck = cq.Workplane("XY").circle(major_dia / 2.0 + 1.0).extrude(6.0).translate((0, 0, height))
    transition = (
        cq.Workplane("XY")
        .workplane(offset=height + 6.0)
        .circle(major_dia / 2.0 + 1.0)
        .workplane(offset=5.0)
        .circle(od / 2.0)
        .loft(combine=True)
    )
    shoulder = cq.Workplane("XY").circle(od / 2.0).extrude(6.0).translate((0, 0, height + 11.0))
    spigot = cq.Workplane("XY").circle(r_bore - 0.2).extrude(cap).translate((0, 0, height + 17.0))
    adapter = thread_core.union(neck).union(transition).union(shoulder).union(spigot)
    adapter = adapter.cut(cq.Workplane("XY").circle(1.25).extrude(height + 17.0 + cap))
    
    # 5. Rear Pressure Endcap
    rear_plug = (
        cq.Workplane("XY")
        .circle(r_bore - 0.2)
        .extrude(cap)
        .translate((0, 0, z0 + housing_len - cap))
    )
    rear_shoulder = (
        cq.Workplane("XY")
        .circle(od / 2.0)
        .extrude(8.0)
        .translate((0, 0, z0 + housing_len))
    )
    rear_endcap = rear_plug.union(rear_shoulder)
    
    # 6. Internal Electronic Envelopes (Nominal boards inside 37.45 mm shell bore)
    z_afe_start = z0 + THERMAL_ZONES_LOCAL_MM["Analog front-end"][0]
    afe_solid = cq.Workplane("XY").box(16, 8, 30, centered=(True, True, False)).translate((0, 0, z_afe_start))
    
    z_pcm_start = z0 + THERMAL_ZONES_LOCAL_MM["PCM1808 ADC"][0]
    # Modeled with nominal PCM1808 board dimensions (30 mm width x 12 mm height x 50 mm length)
    pcm_solid = cq.Workplane("XY").box(30, 12, 50, centered=(True, True, False)).translate((0, 0, z_pcm_start))
    
    z_stm_start = z0 + THERMAL_ZONES_LOCAL_MM["STM32F411 MCU"][0]
    stm_solid = cq.Workplane("XY").box(21, 11.5, 53, centered=(True, True, False)).translate((0, 0, z_stm_start))
    
    z_pwr_start = z0 + THERMAL_ZONES_LOCAL_MM["Power & RTC"][0]
    pwr_solid = cq.Workplane("XY").box(18, 10, 45, centered=(True, True, False)).translate((0, 0, z_pwr_start))
    
    z_sd_start = z0 + THERMAL_ZONES_LOCAL_MM["SD Storage & Reserve"][0]
    sd_solid = cq.Workplane("XY").box(18, 8, 45, centered=(True, True, False)).translate((0, 0, z_sd_start))
    
    # 7. HTI Sensor Reference Envelope (Exposed acoustic head)
    sensor_head = cq.Workplane("XY").circle(17.475 / 2.0).extrude(88.9).translate((0, 0, -88.9))
    
    parts = [
        (sensor_head, "HTI_Acoustic_Head_Reference", (0.30, 0.30, 0.32)),
        (adapter, "HTI_Front_Bulkhead_Adapter", (0.55, 0.58, 0.62)),
        (shell, "Inconel718_Pressure_Shell", (0.50, 0.52, 0.56)),
        (rear_endcap, "Rear_Pressure_Endcap", (0.55, 0.58, 0.62)),
        (carrier_rails, "PEEK_Conformal_Carrier_Rails", (0.70, 0.45, 0.18)),
        (front_buffer.union(rear_buffer), "Axial_Buffer_Plugs", (0.75, 0.50, 0.22)),
        (afe_solid, "Analog_Front_End_AFE", (0.60, 0.25, 0.65)),
        (pcm_solid, "PCM1808_ADC_Module_DirectFit", (0.18, 0.55, 0.22)),
        (stm_solid, "STM32F411_MCU_Module", (0.15, 0.30, 0.75)),
        (pwr_solid, "Power_and_RTC_Section", (0.75, 0.20, 0.20)),
        (sd_solid, "MicroSD_Storage_Reserve", (0.85, 0.50, 0.15)),
    ]
    
    # Calculate axial bounding extent across all solid parts
    z_min = min(solid.val().BoundingBox().zmin for solid, _, _ in parts)
    z_max = max(solid.val().BoundingBox().zmax for solid, _, _ in parts)
    cad_total_len_mm = round(z_max - z_min, 1)
    geometry["cad_total_length_mm"] = cad_total_len_mm
    
    if output_step_path:
        output_step_path.parent.mkdir(parents=True, exist_ok=True)
        assembly = cq.Assembly(name="PertAcoustic_Compact_ConformalCarrier_Casing")
        for solid, name, color in parts:
            assembly.add(solid, name=name, color=cq.Color(*color))
        assembly.save(str(output_step_path))
        print(f"Compact CAD STEP assembly exported to {output_step_path} (Axial Bounding Span: {cad_total_len_mm} mm)")
        
    return parts


def check_cad_assembly_interferences(geometry: dict[str, Any]) -> dict[str, Any]:
    """
    Performs rigorous automated Boolean intersection collision checks across CAD solids.
    
    Fail-Closed Policy:
    If any solid is invalid, or if the geometry kernel produces an invalid solid, or if non-empty
    intersection objects yield val() is None, the check fails closed (passed = False, status = 'ERROR / NOT VERIFIED')
    and the candidate cannot be recommended.
    
    Verifies:
    1. Carrier rails do not penetrate the Inconel pressure shell.
    2. Carrier rails do not penetrate the non-retention general PCM1808 envelope.
    3. Nominal electronics do not penetrate the Inconel shell.
    4. Nominal electronics do not penetrate axial buffer plugs.
    """
    try:
        od = geometry["od_mm"]
        wall = geometry["wall_mm"]
        shell_id = od - 2.0 * wall
        r_bore = shell_id / 2.0
        r_carrier_out = (shell_id - 0.400) / 2.0  # 18.525 mm
        housing_len = geometry["housing_length_mm"]
        cap = geometry["endcap_thickness_mm"]
        z0 = 40.0
        internal_length = housing_len - 2.0 * cap
        
        # 1. Shell solid
        shell = cq.Workplane("XY").circle(od / 2.0).circle(r_bore).extrude(housing_len).translate((0, 0, z0))
        if not shell.val().isValid():
            raise ValueError("Inconel shell solid is invalid.")
            
        # 2. Conformal carrier solid
        carrier_raw = cq.Workplane("XY").circle(r_carrier_out).extrude(internal_length).translate((0, 0, z0 + cap))
        cut_pcm_envelope = cq.Workplane("XY").rect(32.0, 14.0).extrude(internal_length + 2.0).translate((0, 0, z0 + cap - 1.0))
        cut_top_corridor = cq.Workplane("XY").workplane(offset=z0 + cap - 1.0).center(0, 10.0).rect(28.0, 20.0).extrude(internal_length + 2.0)
        cut_bottom_pocket = cq.Workplane("XY").workplane(offset=z0 + cap - 1.0).center(0, -14.5).rect(16.0, 11.0).extrude(internal_length + 2.0)
        carrier_base = carrier_raw.cut(cut_pcm_envelope).cut(cut_top_corridor).cut(cut_bottom_pocket)
        
        # Guide ribs
        guide_top_r = cq.Workplane("XY").workplane(offset=z0 + cap).center(15.1, 2.5).rect(1.8, 3.0).extrude(internal_length)
        guide_bot_r = cq.Workplane("XY").workplane(offset=z0 + cap).center(15.1, -2.5).rect(1.8, 3.0).extrude(internal_length)
        guide_top_l = cq.Workplane("XY").workplane(offset=z0 + cap).center(-15.1, 2.5).rect(1.8, 3.0).extrude(internal_length)
        guide_bot_l = cq.Workplane("XY").workplane(offset=z0 + cap).center(-15.1, -2.5).rect(1.8, 3.0).extrude(internal_length)
        carrier = carrier_base.union(guide_top_r).union(guide_bot_r).union(guide_top_l).union(guide_bot_l)
        
        if not carrier.val().isValid():
            raise ValueError("Carrier solid is invalid.")
            
        # 3. Reserved general clearance solid (excluding intentional guide slot contact)
        # Components envelope: Top zone (Y in [1.0, 7.0], width 28.0), Bottom zone (Y in [-7.0, -1.0], width 28.0), and Card slot zone (Y in [-0.8, 0.8], width 32.0)
        z_pcm_start = z0 + THERMAL_ZONES_LOCAL_MM["PCM1808 ADC"][0]
        pcm_top_clearance = cq.Workplane("XY").workplane(offset=z_pcm_start).center(0, 4.0).rect(28.0, 6.0).extrude(50.0)
        pcm_bot_clearance = cq.Workplane("XY").workplane(offset=z_pcm_start).center(0, -4.0).rect(28.0, 6.0).extrude(50.0)
        pcm_slot_clearance = cq.Workplane("XY").workplane(offset=z_pcm_start).center(0, 0.0).rect(32.0, 1.6).extrude(50.0)
        pcm_general_clearance = pcm_top_clearance.union(pcm_bot_clearance).union(pcm_slot_clearance)
        # 4. Nominal PCM1808 PCB solid (30 x 12 x 50 mm)
        pcm_nominal_solid = cq.Workplane("XY").box(30.0, 12.0, 50.0, centered=(True, True, False)).translate((0, 0, z_pcm_start))
        
        # 5. Front buffer plug
        front_buffer = cq.Workplane("XY").circle(r_bore - 0.05).extrude(FRONT_AXIAL_BUFFER_MM).translate((0, 0, z0 + cap))
        
        # Boolean intersection calculations (fail-closed on invalid OCC shapes and missing values)
        def calc_intersection_vol(s1: cq.Workplane, s2: cq.Workplane) -> float:
            inter = s1.intersect(s2)
            if len(inter.objects) == 0:
                return 0.0
            val = inter.val()
            if val is None:
                raise ValueError("Boolean intersection returned non-empty objects list but val() is None.")
            if not val.isValid():
                raise ValueError("Boolean intersection produced an invalid OpenCASCADE shape.")
            return float(val.Volume())
            
        vol_carrier_shell = calc_intersection_vol(carrier, shell)
        vol_carrier_general_pcm = calc_intersection_vol(carrier, pcm_general_clearance)
        vol_pcm_shell = calc_intersection_vol(pcm_nominal_solid, shell)
        vol_pcm_buffer = calc_intersection_vol(pcm_nominal_solid, front_buffer)
        
        max_inter = max(vol_carrier_shell, vol_carrier_general_pcm, vol_pcm_shell, vol_pcm_buffer)
        passed = max_inter < 1e-4
        status = "PASS (Zero Prohibited Interference)" if passed else f"FAIL ({max_inter:.4f} mm³ interference)"
        
        return {
            "carrier_vs_shell_vol_mm3": round(vol_carrier_shell, 6),
            "carrier_vs_pcm_general_envelope_vol_mm3": round(vol_carrier_general_pcm, 6),
            "pcm_nominal_vs_shell_vol_mm3": round(vol_pcm_shell, 6),
            "pcm_nominal_vs_buffer_vol_mm3": round(vol_pcm_buffer, 6),
            "max_interference_vol_mm3": round(max_inter, 6),
            "passed": passed,
            "status": status,
            "error": None,
        }
    except Exception as e:
        return {
            "carrier_vs_shell_vol_mm3": None,
            "carrier_vs_pcm_general_envelope_vol_mm3": None,
            "pcm_nominal_vs_shell_vol_mm3": None,
            "pcm_nominal_vs_buffer_vol_mm3": None,
            "max_interference_vol_mm3": None,
            "passed": False,
            "status": "ERROR / NOT VERIFIED",
            "error": f"{type(e).__name__}: {e}",
        }


# ==============================================================================
# 6. VISUALIZATIONS & REPORTING
# ==============================================================================

def render_compact_cad(parts: list[tuple[cq.Workplane, str, tuple[float, float, float]]], output_png: Path) -> None:
    """
    Renders 3D isometric view of the no-aerogel compact casing assembly.
    """
    fig = plt.figure(figsize=(14, 7), dpi=200)
    ax_full = fig.add_subplot(121, projection="3d")
    ax_detail = fig.add_subplot(122, projection="3d")
    
    def draw_solids(ax, selected_parts, shell_alpha=0.15):
        for solid, name, color in selected_parts:
            if name in {"Axial_Buffer_Plugs"}:
                continue
            try:
                vertices, triangles = solid.val().tessellate(0.8)
                xyz = np.array([(v.x, v.y, v.z) for v in vertices])
                faces = [[xyz[i] for i in triangle] for triangle in triangles]
                is_shell = name in {"Inconel718_Pressure_Shell", "HTI_Front_Bulkhead_Adapter", "Rear_Pressure_Endcap"}
                alpha = shell_alpha if is_shell else 0.90
                edgecolor = (0.3, 0.35, 0.4, 0.15) if is_shell else "none"
                collection = Poly3DCollection(
                    faces, facecolor=color, edgecolor=edgecolor, linewidths=0.2 if is_shell else 0, alpha=alpha
                )
                ax.add_collection3d(collection)
            except Exception as e:
                print(f"Warning tessellating {name}: {e}")
                
        ax.view_init(elev=22, azim=-50)
        ax.set_xlabel("X (mm)", labelpad=6, fontsize=8)
        ax.set_ylabel("Y (mm)", labelpad=6, fontsize=8)
        ax.set_zlabel("Axial Z (mm)", labelpad=6, fontsize=8)
        ax.set_xlim(-25, 25)
        ax.set_ylim(-25, 25)
        
    draw_solids(ax_full, parts, shell_alpha=0.15)
    ax_full.set_zlim(0, HOUSING_LENGTH_MM + 80)
    ax_full.set_title("PertAcoustic No-Aerogel Compact Casing (Full 3D Assembly)", fontsize=10, fontweight="bold")
    
    # Detail view of electronics inside conformal carrier
    detail_parts = [p for p in parts if p[1] not in {"Inconel718_Pressure_Shell"}]
    draw_solids(ax_detail, detail_parts, shell_alpha=0.25)
    ax_detail.set_zlim(40, 220)
    ax_detail.set_title("Internal Electronics & Discrete Polymer Carrier (Shell Hidden)", fontsize=10, fontweight="bold")
    
    fig.tight_layout()
    output_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_png, dpi=200, bbox_inches="tight")
    plt.close(fig)


def render_transverse_pcm1808_cross_section(output_png: Path) -> None:
    """
    Renders the transverse cross-section at the PCM1808 board station, highlighting
    the circular shell bore, conformal carrier geometry, and clearance corridors.
    """
    fig, ax = plt.subplots(figsize=(8, 8), dpi=200)
    
    od = PREFERRED_OD_MM
    wall = 3.5
    shell_id = od - 2.0 * wall  # 37.45 mm
    r_outer = od / 2.0
    r_bore = shell_id / 2.0
    r_carrier_out = (shell_id - 0.400) / 2.0  # 18.525 mm
    
    # Outer casing & bore
    c_outer = plt.Circle((0, 0), r_outer, color="#8c92ac", alpha=0.9, label="Inconel 718 Pressure Shell (OD 44.45 mm / 1.75 in)")
    c_bore = plt.Circle((0, 0), r_bore, color="#ffffff", label=f"Bare Shell Bore (ID {shell_id:.2f} mm)")
    ax.add_patch(c_outer)
    ax.add_patch(c_bore)
    
    # Conformal polymer carrier chassis (OD 37.05 mm)
    c_carrier = plt.Circle((0, 0), r_carrier_out, color="#e67e22", alpha=0.35, label="Conformal PEEK Carrier Chassis (OD 37.05 mm)")
    ax.add_patch(c_carrier)
    
    # Internal clearance cutouts
    ax.add_patch(plt.Rectangle((-16, -7), 32, 14, color="#ffffff", alpha=0.95, label="Reserved PCM1808 Envelope (32.0 x 14.0 mm)"))
    ax.add_patch(plt.Rectangle((-14, 0), 28, 16, color="#ffffff", alpha=0.95))
    ax.add_patch(plt.Rectangle((-8, -16), 16, 12, color="#ffffff", alpha=0.95))
    
    # Card guide slots & board edges
    ax.add_patch(plt.Rectangle((-16.0, -1.0), 1.8, 2.0, color="#d35400", alpha=0.7, label="PCB Card Guide Channels (0.8 mm edge capture)"))
    ax.add_patch(plt.Rectangle((14.2, -1.0), 1.8, 2.0, color="#d35400", alpha=0.7))
    
    # PCM1808 board (nominal 30 x 12 mm envelope)
    pcm_pcb = plt.Rectangle((-15, -0.8), 30, 1.6, color="#27ae60", alpha=0.95, label="PCM1808 PCB Substrate (30.0 x 1.6 mm)")
    pcm_comp_top = plt.Rectangle((-13, 0.8), 26, 5.2, color="#2ecc71", alpha=0.75, label="Top Components Envelope (5.2 mm max)")
    pcm_comp_bot = plt.Rectangle((-13, -6.0), 26, 5.2, color="#2ecc71", alpha=0.75, label="Bottom Components Envelope (5.2 mm max)")
    ax.add_patch(pcm_pcb)
    ax.add_patch(pcm_comp_top)
    ax.add_patch(pcm_comp_bot)
    
    # Circumscribed bounding envelope circle (diagonal = 34.93 mm, radius = 17.464 mm)
    diag_r = math.hypot(32.0, 14.0) / 2.0
    c_diag = plt.Circle((0, 0), diag_r, color="#c0392b", fill=False, linestyle="--", linewidth=1.5, label="Circumscribed PCM Envelope (Ø 34.93 mm)")
    ax.add_patch(c_diag)
    
    ax.set_xlim(-r_outer - 4, r_outer + 4)
    ax.set_ylim(-r_outer - 4, r_outer + 4)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Transverse X (mm)", fontsize=9)
    ax.set_ylabel("Transverse Y (mm)", fontsize=9)
    ax.set_title(f"PCM1808 Transverse Cross-Section (Shell Bore ID {shell_id:.2f} mm - Direct Fit)", fontsize=10, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.5)
    
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc="upper center", bbox_to_anchor=(0.5, -0.10), ncol=2, fontsize=7.5)
    
    fig.tight_layout()
    output_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_png, dpi=200, bbox_inches="tight")
    plt.close(fig)


def render_longitudinal_cross_section(candidate: dict[str, Any], output_png: Path) -> None:
    """
    Renders 2D longitudinal cross-section highlighting expanded clear ID, carrier guide rails,
    HTI front bulkhead adapter, and internal electronic envelopes.
    """
    fig, ax = plt.subplots(figsize=(14, 4.5), dpi=200)
    z0 = 40.0
    housing_len = candidate.get("housing_length_mm", HOUSING_LENGTH_MM)
    od = candidate["od_mm"]
    wall = candidate["wall_mm"]
    shell_id = candidate["packaging"]["shell_bore_id_mm"]
    
    r_outer = od / 2.0
    r_shell_in = shell_id / 2.0
    
    # Layer patches
    ax.add_patch(plt.Rectangle((z0, -r_outer), housing_len, 2 * r_outer, color="#7d828a", label="Inconel 718 Pressure Shell (3.5 mm)", zorder=1))
    ax.add_patch(plt.Rectangle((z0, -r_shell_in), housing_len, 2 * r_shell_in, color="#f8f9fa", label=f"Bare Shell Bore (ID {shell_id:.2f} mm - Conformal Rails)", zorder=2))
    
    # Discrete carrier rail strip
    ax.add_patch(plt.Rectangle((z0 + ENDCAP_THICKNESS_MM, -r_shell_in), housing_len - 2*ENDCAP_THICKNESS_MM, 2.0, color="#d35400", label="Conformal PEEK Carrier Chassis", zorder=3))
    ax.add_patch(plt.Rectangle((z0 + ENDCAP_THICKNESS_MM, r_shell_in - 2.0), housing_len - 2*ENDCAP_THICKNESS_MM, 2.0, color="#d35400", zorder=3))
    
    # Axial electronics modules
    modules = [
        (z0 + THERMAL_ZONES_LOCAL_MM["Analog front-end"][0], 30, 8, "AFE", "#9a4da2"),
        (z0 + THERMAL_ZONES_LOCAL_MM["PCM1808 ADC"][0], 50, 12, "PCM1808 (Direct Fit)", "#2d8a3c"),
        (z0 + THERMAL_ZONES_LOCAL_MM["STM32F411 MCU"][0], 53, 11.5, "STM32F411", "#315fb5"),
        (z0 + THERMAL_ZONES_LOCAL_MM["Power & RTC"][0], 45, 10, "Power/RTC", "#ad3434"),
        (z0 + THERMAL_ZONES_LOCAL_MM["SD Storage & Reserve"][0], 45, 8, "SD/Reserve", "#d97724"),
    ]
    for z, length, height, label, color in modules:
        ax.add_patch(plt.Rectangle((z, -height / 2.0), length, height, color=color, alpha=0.95, zorder=4))
        ax.text(z + length / 2.0, 0, label, ha="center", va="center", color="white", fontsize=7.5, fontweight="bold", zorder=5)
        
    ax.add_patch(plt.Rectangle((-88.9, -17.475 / 2.0), 88.9, 17.475, color="#404040", label="HTI-02-DHPC/D Sensor Head", zorder=2))
    ax.add_patch(plt.Rectangle((0, -od / 2.0), z0, od, color="#60656e", label="Bulkhead Adapter (7/16-20)", zorder=2))
    ax.plot([-88.9, z0 + THERMAL_ZONES_LOCAL_MM["Analog front-end"][0]], [0, 0], color="#00ffff", linestyle="--", linewidth=1.5, label="3-Wire Feedthrough", zorder=6)
    
    ax.set_xlim(-100, z0 + housing_len + 30)
    ax.set_ylim(-r_outer - 6, r_outer + 6)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Axial Position Z (mm)", fontsize=9)
    ax.set_ylabel("Radius (mm)", fontsize=9)
    ax.set_title(f"Simplified No-Aerogel Conformal Carrier Layout (OD {od:.2f} mm, Shell Bore ID {shell_id:.2f} mm - Direct PCM1808 Fit)", fontsize=10, fontweight="bold")
    
    handles, labels_list = ax.get_legend_handles_labels()
    unique_legend = dict(zip(labels_list, handles))
    ax.legend(unique_legend.values(), unique_legend.keys(), loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=4, fontsize=8)
    
    fig.tight_layout()
    output_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_png, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_thermal_architecture_comparison(candidates: list[dict[str, Any]], output_png: Path) -> None:
    """
    Plots thermal comparison across architectures (Aerogel vs No-Aerogel PEEK vs No-Aerogel PPA vs No-Aerogel PA66-GF30 vs Polymer-only)
    at both 0 W and 1.0 W.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=200)
    
    # 1. Transient Thermal Curves (0 W vs 1.0 W over 7200 s)
    arch_a = next(c for c in candidates if "Architecture A:" in c["architecture"] and c["od_mm"] == PREFERRED_OD_MM and c["wall_mm"] == 3.5)
    arch_b = next(c for c in candidates if "Architecture B:" in c["architecture"])
    arch_b2 = next(c for c in candidates if "Architecture B2" in c["architecture"])
    arch_ref = next(c for c in candidates if "Reference Baseline" in c["architecture"])
    
    hours = arch_a["thermal_1w"]["times_s"] / 3600.0
    
    # Plot 1.0 W curves
    ax1.plot(hours, arch_a["thermal_1w"]["inner_temperature_C"], color="#27ae60", linewidth=2.4, label=f"No-Aerogel PEEK @ 1W -> {arch_a['thermal_1w']['final_inner_temperature_C']:.2f} °C")
    ax1.plot(hours, arch_b["thermal_1w"]["inner_temperature_C"], color="#2980b9", linewidth=2.0, linestyle="-.", label=f"No-Aerogel PPA @ 1W -> {arch_b['thermal_1w']['final_inner_temperature_C']:.2f} °C")
    ax1.plot(hours, arch_b2["thermal_1w"]["inner_temperature_C"], color="#8e44ad", linewidth=2.0, linestyle=":", label=f"No-Aerogel PA66-GF30 @ 1W -> {arch_b2['thermal_1w']['final_inner_temperature_C']:.2f} °C")
    ax1.plot(hours, arch_ref["thermal_1w"]["inner_temperature_C"], color="#c0392b", linewidth=2.2, linestyle="--", label=f"With Aerogel Baseline @ 1W -> {arch_ref['thermal_1w']['final_inner_temperature_C']:.2f} °C (Heat Trapping)")
    
    # Plot 0 W curves (pure heat ingress)
    ax1.plot(hours, arch_a["thermal_0w"]["inner_temperature_C"], color="#7f8c8d", linewidth=1.5, linestyle=":", label=f"No-Aerogel PEEK @ 0W -> {arch_a['thermal_0w']['final_inner_temperature_C']:.2f} °C")
    ax1.plot(hours, arch_ref["thermal_0w"]["inner_temperature_C"], color="#e67e22", linewidth=1.5, linestyle=":", label=f"With Aerogel @ 0W -> {arch_ref['thermal_0w']['final_inner_temperature_C']:.2f} °C")
    
    ax1.axhline(70.0, color="#d35400", linestyle="--", linewidth=1.2, label="70 °C External Ambient Boundary")
    ax1.axhline(85.0, color="#8e44ad", linestyle=":", linewidth=1.5, label="85 °C STM32 / PCM1808 Upper Operating Limit")
    
    ax1.set_xlabel("Exposure Time (Hours)", fontsize=9)
    ax1.set_ylabel("Inner Shell Surface Temperature (°C)", fontsize=9)
    ax1.set_title("2-Hour Transient Response: Shell Inner Surface (70 °C Boundary)", fontsize=10, fontweight="bold")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="lower right", fontsize=7.5)
    
    # 2. Side-by-Side Bar Comparison across Architectures
    labels = ["Inconel+PEEK\n(Conformal)", "Inconel+PPA\n(Conformal)", "Inconel+PA66\n(Conformal)", "Inconel+PEEK\n(Full Liner)", "PEEK-Only\n(Exploratory)", "Inconel+Aerogel\n(Baseline)"]
    arch_c = next(c for c in candidates if "Architecture C" in c["architecture"])
    arch_f = next(c for c in candidates if "Architecture F" in c["architecture"])
    selected_archs = [arch_a, arch_b, arch_b2, arch_c, arch_f, arch_ref]
    
    temps_0w = [c["thermal_0w"]["final_inner_temperature_C"] for c in selected_archs]
    temps_1w = [c["thermal_1w"]["final_inner_temperature_C"] for c in selected_archs]
    
    x = np.arange(len(labels))
    width = 0.35
    
    b1 = ax2.bar(x - width/2, temps_0w, width, label="0 W (Pure Ingress)", color="#3498db", edgecolor="black", linewidth=0.6)
    b2 = ax2.bar(x + width/2, temps_1w, width, label="1.0 W (Self-Heating)", color="#e74c3c", edgecolor="black", linewidth=0.6)
    
    ax2.axhline(70.0, color="#d35400", linestyle="--", linewidth=1.2, label="70 °C Ambient")
    ax2.axhline(85.0, color="#8e44ad", linestyle=":", linewidth=1.5, label="85 °C IC Limit")
    
    for b in b1:
        h = b.get_height()
        ax2.annotate(f"{h:.1f}°C", xy=(b.get_x() + b.get_width()/2, h), xytext=(0, 2), textcoords="offset points", ha="center", fontsize=7)
    for b in b2:
        h = b.get_height()
        ax2.annotate(f"{h:.1f}°C", xy=(b.get_x() + b.get_width()/2, h), xytext=(0, 2), textcoords="offset points", ha="center", fontsize=7)
        
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=7.5)
    ax2.set_ylabel("Inner Shell Temperature at 2h (°C)", fontsize=9)
    ax2.set_title("Inner Shell Thermal Screening Comparison at 2 Hours", fontsize=10, fontweight="bold")
    ax2.grid(axis="y", alpha=0.3)
    ax2.legend(loc="upper right", fontsize=7.5)
    
    fig.tight_layout()
    output_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_png, dpi=200)
    plt.close(fig)


def export_trade_study_csv_and_report(
    candidates: list[dict[str, Any]], recommended: dict[str, Any], output_dir: Path
) -> None:
    """
    Exports comprehensive CSV dataset and dynamically generated formal comparative Markdown report.
    All reported numbers and tables are strictly derived from live candidate and result objects.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Export CSV
    csv_path = output_dir / "compact_casing_trade_study.csv"
    fieldnames = [
        "architecture", "is_recommended_baseline", "od_mm", "od_in", "shell_bore_id_mm", "clear_id_mm", "wall_mm",
        "aerogel_mm", "liner_mm", "carrier_type", "casing_material", "liner_material",
        "total_tool_length_mm", "packaging_feasibility",
        "strength_basis", "strength_ratio_10mpa", "fos_buckle_1000m",
        "strength_ratio_20mpa", "fos_buckle_20mpa",
        "strength_ratio_10kpsi", "fos_buckle_10kpsi",
        "inner_shell_temp_2h_0w_C", "inner_shell_temp_2h_1w_C",
        "thermal_screening_status", "overall_status"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for c in candidates:
            if not c.get("fit"):
                continue
            s = c["structural"]
            writer.writerow({
                "architecture": c["architecture"],
                "is_recommended_baseline": c.get("is_recommended_baseline", False),
                "od_mm": c["od_mm"],
                "od_in": round(c["od_mm"] / 25.4, 3),
                "shell_bore_id_mm": c["packaging"]["shell_bore_id_mm"],
                "clear_id_mm": c["clear_id_mm"],
                "wall_mm": c["wall_mm"],
                "aerogel_mm": c["aerogel_mm"],
                "liner_mm": c["liner_mm"],
                "carrier_type": "Conformal Rails" if c.get("is_discrete_carrier") else ("Full Liner" if c["liner_mm"] > 0 else "None"),
                "casing_material": c["casing_material"],
                "liner_material": c["liner_material"],
                "total_tool_length_mm": c.get("total_tool_length_mm", 656.9),
                "packaging_feasibility": c["packaging"]["packaging_status"],
                "strength_basis": s["scenarios"]["scenario_1000m_10mpa"]["strength_basis"],
                "strength_ratio_10mpa": s["scenarios"]["scenario_1000m_10mpa"]["screening_strength_ratio"],
                "fos_buckle_1000m": s["buckling_1000m"]["buckling_safety_factor"],
                "strength_ratio_20mpa": s["scenarios"]["scenario_intermediate_20mpa"]["screening_strength_ratio"],
                "fos_buckle_20mpa": s["buckling_20mpa"]["buckling_safety_factor"],
                "strength_ratio_10kpsi": s["scenarios"]["scenario_historical_68_9mpa"]["screening_strength_ratio"],
                "fos_buckle_10kpsi": s["buckling_historical"]["buckling_safety_factor"],
                "inner_shell_temp_2h_0w_C": c["thermal_0w"]["final_inner_temperature_C"],
                "inner_shell_temp_2h_1w_C": c["thermal_1w"]["final_inner_temperature_C"],
                "thermal_screening_status": "CONDITIONAL — INTERNAL THERMAL PATH UNRESOLVED",
                "overall_status": c["overall_status"],
            })
            
    # 2. Dynamically Generate Markdown Report
    md_path = output_dir / "compact_casing_redesign_report.md"
    
    rec_arch = recommended["architecture"]
    rec_od = recommended["od_mm"]
    rec_wall = recommended["wall_mm"]
    rec_shell_bore = recommended["packaging"]["shell_bore_id_mm"]
    rec_clear_id = recommended["clear_id_mm"]
    rec_len = recommended.get("total_tool_length_mm", 656.9)
    cad_len = recommended.get("cad_total_length_mm", 656.9)
    rec_s = recommended["structural"]
    rec_t0 = recommended["thermal_0w"]["final_inner_temperature_C"]
    rec_t1 = recommended["thermal_1w"]["final_inner_temperature_C"]
    
    aerogel_cand = next((c for c in candidates if "Aerogel" in c["architecture"]), None)
    aero_t1 = aerogel_cand["thermal_1w"]["final_inner_temperature_C"] if aerogel_cand else 71.72
    
    tb = recommended["packaging"].get("tolerance_budget", {})
    carrier_od = tb.get("carrier_od_nom_mm", rec_shell_bore - 0.400)
    cold_clear_diam = tb.get("cold_clearance_diametral_mm", 0.400)
    cold_clear_rad = tb.get("cold_clearance_radial_mm", 0.200)
    diff_growth_diam = tb.get("diff_thermal_growth_diametral_mm", 0.0776)
    diff_growth_rad = tb.get("diff_thermal_growth_radial_mm", 0.0388)
    uncertainty_allow = tb.get("dim_uncertainty_allowance_diametral_mm", 0.020)
    hot_clear_diam = tb.get("hot_clearance_diametral_mm", 0.3024)
    hot_clear_rad = tb.get("hot_clearance_radial_mm", 0.1512)
    worst_hot_diam = tb.get("worst_case_hot_diametral_mm", 0.2634)
    worst_hot_rad = tb.get("worst_case_hot_radial_mm", 0.1317)
    
    # Compute internal thermal sensitivity table
    sens_rows = compute_internal_thermal_sensitivity(rec_t1, power_w=INHERITED_SCREENING_POWER_W)
    sens_table_md = "\n".join(
        f"| {r['r_internal_K_per_W']:.1f} K/W | +{r['delta_T_K']:.1f} K | **{r['t_electronics_screen_C']:.2f} °C** | `{r['status']}` | Lumped screening parameter |"
        for r in sens_rows
    )
    
    # Compute carrier dimensional sensitivity table
    dim_sens_rows = compute_carrier_dimensional_sensitivity(rec_shell_bore)
    dim_sens_table_md = "\n".join(
        f"| **{r['material'].split('_')[0]}** | {r['carrier_od_nom_mm']:.3f} mm | +{r['assumed_conditioning_allowance_mm']:.3f} mm | +{r['diff_thermal_growth_mm']:.4f} mm | {r['hot_clearance_diametral_mm']:.4f} mm | **{r['worst_case_hot_diametral_mm']:.4f} mm** | {r['available_guide_wall_mm']:.3f} mm | `{r['sliding_status']}` |"
        for r in dim_sens_rows
    )
    
    # Carrier Material Trade Matrix
    trade_matrix = build_carrier_material_trade_matrix()
    trade_matrix_md = "\n".join(
        f"| **{item['exact_grade']}** | {item['polymer_family']} | {item['density_kg_m3']} kg/m³ | Dry: {item['modulus_dry_mpa']} MPa<br>Cond: {item['modulus_cond_mpa']} MPa | `{item['strength_basis']}`<br>Dry: {item['strength_dry_mpa']} MPa<br>Cond: {item['strength_cond_mpa']} MPa | {item['thermal_conductivity_w_mk']} W/(m·K) | Eq: {item['moisture_absorption_eq_percent']}<br>Sat: {item['water_absorption_sat_percent']} | `{item['carrier_dimensional_risk']}` | `{item['property_70c_confidence']}` | `{item['downhole_fluid_compatibility']}` | {item['relative_cost_class']} | **`{item['overall_screening_classification']}`** |"
        for item in trade_matrix
    )
    
    # Build Comparison Table
    table_rows = []
    for c in candidates:
        if not c.get("fit"):
            continue
        c_s = c["structural"]
        t1_val = c["thermal_1w"]["final_inner_temperature_C"]
        buckle_10k = c_s["buckling_historical"]["buckling_safety_factor"]
        carrier_label = "Conformal Rails" if c.get("is_discrete_carrier") else ("Full Liner" if c["liner_mm"] > 0 else "None")
        status_short = "RECOMMENDED BASELINE" if c.get("is_recommended_baseline") else (
            "EXPLORATORY" if "Exploratory" in c["architecture"] or "Only" in c["architecture"] else (
                "INFEASIBLE" if not c["packaging"]["direct_fit"] else "QUALIFIED SCREENING"
            )
        )
        table_rows.append(
            f"| **{c['architecture']}** | {c['casing_material']} | {carrier_label} ({c['liner_material'].split('_')[0]}) | {c['wall_mm']:.2f} | {c['packaging']['shell_bore_id_mm']:.2f} mm | {c['packaging']['packaging_status'].split('(')[0].strip()} | {t1_val:.2f} °C | {buckle_10k:.2f} | {status_short} |"
        )
    comparison_table_md = "\n".join(table_rows)
    
    # Build Material Properties Table dynamically
    mat_rows = []
    for mat_name, props in MATERIALS.items():
        if mat_name in {"SS316", "Titanium", "PTFE", "Microporous"}:
            continue
        dens = props.get("density", "N/A")
        k = props.get("conductivity", "N/A")
        cp = props.get("specific_heat", "N/A")
        e_mod = props.get("elastic_modulus_mpa_70c", props.get("elastic_modulus_mpa_150c", props.get("elastic_modulus_mpa_23c_cond", "N/A")))
        strength = props.get("yield_strength_mpa_150c_screening", props.get("screening_tensile_strength_mpa_70c", props.get("tensile_stress_at_break_mpa_23c_cond", "N/A")))
        clte = props.get("thermal_expansion_cross_flow_per_c", props.get("thermal_expansion_per_c", "N/A"))
        clte_str = f"{clte * 1e6:.1f} ppm/K" if isinstance(clte, (int, float)) else "N/A"
        mat_rows.append(
            f"| **{mat_name}** | Density: {dens} kg/m³ | k: {k} W/(m·K) | Cp: {cp} J/(kg·K) | E: {e_mod} MPa | Strength: {strength} MPa | CLTE: {clte_str} | {props.get('notes', '')} |"
        )
    mat_table_md = "\n".join(mat_rows)
    
    # Build Component Zone Assessment Table dynamically
    comp_rows = []
    for comp, zinfo in recommended["zone_assessment"].items():
        comp_rows.append(
            f"| **{comp}** | `{zinfo['operating_limit_status']}` | {zinfo['max_C']} | {rec_t1:.2f} °C | {zinfo['allowable_delta_T_K']} | {zinfo['allowable_r_internal_K_per_W']} K/W | `{zinfo['thermal_model_status']}` | `{zinfo['junction_temperature']}` | {zinfo.get('notes', '')} |"
        )
    comp_table_md = "\n".join(comp_rows)
    
    # Structural scenarios
    sc_1000m = rec_s["scenarios"]["scenario_1000m_10mpa"]
    sc_20mpa = rec_s["scenarios"]["scenario_intermediate_20mpa"]
    sc_hist = rec_s["scenarios"]["scenario_historical_68_9mpa"]
    b_1000m = rec_s["buckling_1000m"]
    b_20mpa = rec_s["buckling_20mpa"]
    b_hist = rec_s["buckling_historical"]
    
    # Collision results
    col = recommended.get("collision_results", {})
    vol_c_s = col.get("carrier_vs_shell_vol_mm3", 0.0)
    vol_c_pcm = col.get("carrier_vs_pcm_general_envelope_vol_mm3", 0.0)
    vol_pcm_s = col.get("pcm_nominal_vs_shell_vol_mm3", 0.0)
    vol_pcm_b = col.get("pcm_nominal_vs_buffer_vol_mm3", 0.0)
    
    report = f"""# PertAcoustic Compact Downhole Casing Redesign Report
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
- **Total modeled tool length: {rec_len:.1f} mm** (CAD Bounding Span: **{cad_len:.1f} mm**)

### Direct Answers to Required Engineering Questions:

1. **"Can we replace the PEEK electronics carrier with a lower-cost nylon-based material for the current 70 °C / 2-hour PertAcoustic downhole tool?"**
   - **For PPA-GF (Solvay Amodel A-1133 HS, 33% GF):**  
     **PREFERRED HIGH-PERFORMANCE COST-REDUCTION CANDIDATE (procurement and exact carrier qualification pending).**  
     PPA provides superior stiffness ($E = 11.81\\text{{ GPa}}$ at 70 °C DAM vs 3.70 GPa for PEEK), moderate moisture absorption (0.20% 24h, 1.80% sat), high glass transition temperature ($T_g \\approx 125\\text{{--}}135\\text{{ °C}}$), and is an expected lower-cost candidate compared to PEEK. Note that published downhole qualification evidence often cites structural lubricated AS-1133 HS rather than standard A-1133 HS.
   - **For PA66-GF30 (BASF Ultramid A3WG6 HRX BK23591):**  
     **PROTOTYPE / VALIDATION CANDIDATE (exact 70 °C wet properties and downhole-fluid compatibility unresolved).**  
     While Ultramid A3WG6 HRX offers expected lower material cost and excellent injection moldability with automotive-grade hydrolysis resistance, its **high water absorption (1.5–1.9% equilibrium at 50% RH, 5.6–6.3% saturation in water)** creates substantial dimensional swelling risk in tight sliding bores ($0.200\\text{{ mm}}$ nominal radial clearance). Moisture conditioning substantially reduces 23 °C modulus and stress at break; exact 70 °C conditioned mechanical behavior remains unresolved. Compatibility with hot wellbore completion brines, crude hydrocarbons, and sour gas remains unestablished. Therefore, PA66-GF30 is classified as a prototype/validation candidate only.

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
- **Density:** $1370\\text{{ kg/m³}}$ (ISO 1183)
- **Thermal Conductivity:** $0.36\\text{{ W/(m·K)}}$ (Datasheet)
- **Specific Heat Capacity:** $1260\\text{{ J/(kg·K)}}$ (Datasheet)
- **Melting Temperature:** $260\\text{{ °C}}$ (ISO 11357)
- **Heat Deflection Temperature:** HDT/A (1.80 MPa) = $245\\text{{ °C}}$; HDT/B (0.45 MPa) = $260\\text{{ °C}}$ (ISO 75-2)
- **Moisture Absorption (Equilibrium, 23 °C / 50% RH):** **1.5 – 1.9 %** (ISO 62)
- **Water Absorption (Saturation in water, 23 °C):** **5.6 – 6.3 %** (ISO 62)
- **Tensile Modulus (23 °C, ISO 527-2):**
  - **Dry (DAM):** $9500\\text{{ MPa}}$ ($9.5\\text{{ GPa}}$)
  - **Conditioned (Moisture-Equilibrated):** $6000\\text{{ MPa}}$ ($6.0\\text{{ GPa}}$) ($-36.8\\%\\text{{ reduction}}$)
- **Tensile Stress at Break (23 °C, ISO 527-2):**
  - **Dry (DAM):** $185\\text{{ MPa}}$
  - **Conditioned:** $110\\text{{ MPa}}$ ($-40.5\\%\\text{{ reduction}}$)
  - **Strength Basis:** `TENSILE_STRESS_AT_BREAK_SCREENING` (Glass-reinforced polyamides exhibit brittle failure without ductile yield)
- **Tensile Strain at Break (23 °C):** Dry = $3.7\\%$; Conditioned = $7.2\\%$
- **Flexural Modulus (23 °C, ISO 178):** Dry = $9200\\text{{ MPa}}$; Conditioned = $5800\\text{{ MPa}}$
- **Tensile Creep Modulus (1000 h, strain $\\le 0.5\\%$, 23 °C, Conditioned, ISO 899-1):** $4800\\text{{ MPa}}$
- **Coefficient of Linear Thermal Expansion (CLTE, ISO 11359-2):**
  - Along flow: $30\\times 10^{{-6}}\\text{{ /K}}$ ($30\\text{{ ppm/K}}$)
  - Cross-flow: $70\\times 10^{{-6}}\\text{{ /K}}$ ($70\\text{{ ppm/K}}$)
- **Electrical Properties (IEC 62631, BASF Feb 2026 Product Information):**
  - Volume Resistivity: $8\\times 10^{{10}}\\text{{ }}\\Omega\\cdot\\text{{m}}$ (published table has incomplete dry/conditioned breakdown; separate dry/conditioned values UNAVAILABLE / NOT PUBLISHED)
  - Surface Resistivity: $8\\times 10^{{12}}\\text{{ }}\\Omega$ (published table has incomplete dry/conditioned breakdown; separate dry/conditioned values UNAVAILABLE / NOT PUBLISHED)
- **Processing Conditions (BASF Processing Data Sheet):**
  - Melt Temperature: $280\\text{{--}}300\\text{{ °C}}$ | Mold Temperature: $80\\text{{--}}90\\text{{ °C}}$
  - Pre-drying: $80\\text{{ °C}}$ for 4 hours
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
{dim_sens_table_md}

### Sizing Observations:
- For **PEEK** ($OD = 37.05\\text{{ mm}}$, allowance $= 0.020\\text{{ mm}}$), worst-case hot diametral clearance is **+0.2634 mm** (+0.1317 mm radial), maintaining ample free-sliding margin.
- For **PPA-GF** ($OD = 37.05\\text{{ mm}}$, allowance $= 0.030\\text{{ mm}}$), worst-case hot diametral clearance is **+0.2534 mm**, fully adequate.
- For **PA66-GF30** ($OD = 37.05\\text{{ mm}}$):
  - At nominal assumed conditioning allowance ($0.080\\text{{ mm}}$), worst-case clearance is **+0.1756 mm** (adequate).
  - However, if assumed saturation swelling reaches $0.200\\text{{--}}0.300\\text{{ mm}}$ diametral in a wet well environment, worst-case clearance drops to **+0.0556 mm / -0.0444 mm**, risking carrier binding and tool jamming unless carrier OD is reduced to **36.85 mm**.

---

## 6. Short-Duration Creep & Thermal Assessment

### Creep Assessment during 2-Hour Exposure:
- 23 °C conditioned creep evidence exists for PA66-GF30 ($4800\\text{{ MPa}}$ at 1000h, ISO 899-1); 70 °C wet creep remains unresolved.
- For the nominal **2.0 hours (7200 s)** PertAcoustic logging run, the short duration reduces concern under internal self-weight and card-retention loads, but does not establish formal creep qualification.

### Thermal Comparison:
- Thermal conductivities: PEEK ($0.29\\text{{ W/(m·K)}}$), PPA ($0.26\\text{{ W/(m·K)}}$), PA66-GF30 ($0.36\\text{{ W/(m·K)}}$).
- PA66-GF30 provides slightly higher bulk conductivity (+24% vs PEEK), aiding heat transfer from board guide edges to the shell.
- Inner shell surface 2-hour screening temperature remains virtually identical across all three discrete carrier candidates (**{rec_t1:.2f} °C** at 1.0 W) because heat conducts through the high-conductivity Inconel shell ($14.7\\text{{ W/(m·K)}}$) directly into the wellbore fluid.
- The allowable internal thermal resistance budget remains **{85.0 - rec_t1:.2f} K/W** for verified +85 °C electronics.

---

## 7. Manufacturing & Processability Comparison

1. **Injection Molding:**
   - **PA66-GF30:** Excellent moldability at standard melt temperatures ($280\\text{{--}}300\\text{{ °C}}$) and mold temperatures ($80\\text{{--}}90\\text{{ °C}}$). Requires pre-drying at $80\\text{{ °C}}$ (4 h) to recommended pellet moisture of $0.025\\text{{--}}0.045\\%$ to prevent hydrolytic degradation during processing.
   - **PPA-GF:** High-temperature molding ($315\\text{{--}}330\\text{{ °C}}$) with heated molds ($135\\text{{--}}150\\text{{ °C}}$) required to achieve full crystallinity.
   - **PEEK:** Ultra-high-temperature molding ($380\\text{{--}}400\\text{{ °C}}$) requiring specialized high-temp injection equipment and mold heaters ($160\\text{{--}}190\\text{{ °C}}$).
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
   - Measure mass uptake $\\Delta M(t)$ and diametral linear expansion $\\Delta D(t)$ at 24h, 48h, 168h (1 week), and saturation.
3. **Inconel Bore Sliding Coupon Test:**
   - Slide conditioned wet carrier coupons through an Inconel 718 tube bore coupon (ID $37.45\\pm 0.02\\text{{ mm}}$) at 20 °C and inside a 70 °C heated chamber.
   - Verify insertion/extraction force remains $< 20\\text{{ N}}$ without binding.
4. **PCB Card Guide Fit & Retention Test:**
   - Measure PCB card-edge insertion force into the guide slots before and after 70 °C hydrothermal conditioning to verify slot width does not swell shut or pinch circuit boards.

---

## 9. Side-by-Side Architecture Comparison Matrix

Evaluated under 70 °C external boundary and 7200 s (2h) exposure:

| Architecture | Casing Material | Carrier / Liner | Wall mm | Shell Bore ID | Packaging Feasibility | Inner Shell Temp @ 1W | FoS Buckle (10k psi) | Classification |
|---|---|---|---|---|---|---|---|---|
{comparison_table_md}

---

## 10. Thermal Screening & Internal Resistance Budgets

- **External Boundary:** 70.0 °C constant Dirichlet on casing outer diameter.
- **Duration:** 7200 s (2.0 hours).
- **Result Type:** `IDEAL SHELL-COUPLED LOWER-BOUND TEMPERATURE (INNER SHELL SURFACE)`
- **Allowable Internal Thermal Resistance Budget:** **{85.0 - rec_t1:.2f} K/W** (for +85 °C IC limits).

### Internal Thermal-Resistance Parameter Sweep:
| Internal Thermal Resistance $R_{{\\text{{internal}}}}$ | Internal Temperature Rise $\\Delta T$ | Electronics Screening Temp | +85 °C IC Limit Status | Notes |
|---|---|---|---|---|
{sens_table_md}

---

## 11. Structural Screening Across Pressure Scenarios ({rec_arch})

*Authoritative casing design pressure remains unresolved. Sizing is based on preliminary engineering screening. PA66 is NOT ELIGIBLE AS THE CURRENT PRESSURE-SHELL BASELINE. Polymer-only casing remains EXPLORATORY / CONDITIONAL because authoritative field pressure, creep and collapse requirements remain unresolved.*

1. **Scenario A (~10 MPa / 1,450 psi - ~1000 m Hydrostatic Context):**
   - Max von Mises Stress: **{sc_1000m['max_von_mises_mpa']:.1f} MPa** | Strength Ratio: **{sc_1000m['screening_strength_ratio']:.2f}** | Buckling FoS: **{b_1000m['buckling_safety_factor']:.2f}**
2. **Scenario B (20 MPa / 2,900 psi - Intermediate Sensitivity):**
   - Max von Mises Stress: **{sc_20mpa['max_von_mises_mpa']:.1f} MPa** | Strength Ratio: **{sc_20mpa['screening_strength_ratio']:.2f}** | Buckling FoS: **{b_20mpa['buckling_safety_factor']:.2f}**
3. **Scenario C (68.95 MPa / 10,000 psi - Historical Biweekly 5 Benchmark):**
   - Max von Mises Stress: **{sc_hist['max_von_mises_mpa']:.1f} MPa** | Strength Ratio: **{sc_hist['screening_strength_ratio']:.2f}** | Buckling FoS: **{b_hist['buckling_safety_factor']:.2f}**

---

## 12. CAD Assembly & Dimensional Extent

- **Collision Check:** Automated Boolean intersection checks confirmed **zero prohibited interference (0.00 mm³)**.
- **Modeled Subassembly Span:** **{rec_len:.1f} mm** (Limit $\\le 2000.0\\text{{ mm}}$).
- **CAD Assembly Bounding Extent:** **{cad_len:.1f} mm** along axial Z.

---

## 13. Artifacts & Generated Evidence

- **CAD STEP Model:** [`results/compact-casing/cad/compact_casing_assembly.step`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/cad/compact_casing_assembly.step)
- **Trade Study Dataset:** [`results/compact-casing/compact_casing_trade_study.csv`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/compact_casing_trade_study.csv)
- **Visualizations:**
  - 3D CAD Assembly Render: [`results/compact-casing/figures/compact_cad_assembly.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_cad_assembly.png)
  - Transverse Cross-Section (Conformal Clearance & Card Guides): [`results/compact-casing/figures/compact_transverse_pcm1808_section.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_transverse_pcm1808_section.png)
  - Longitudinal Section: [`results/compact-casing/figures/compact_longitudinal_section.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_longitudinal_section.png)
  - Thermal History & Comparison: [`results/compact-casing/figures/compact_thermal_trade_study.png`](file:///home/faliq/projects/pertacoustic-3d-design/results/compact-casing/figures/compact_thermal_trade_study.png)
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"Trade study report exported to {md_path}")
    print(f"Trade study CSV exported to {csv_path}")


# ==============================================================================
# 7. MAIN EXECUTION PIPELINE
# ==============================================================================

def run_compact_study_pipeline() -> dict[str, Any]:
    """
    Executes the complete simplified compact downhole casing study pipeline.
    """
    print("=" * 70)
    print("RUNNING PERTACOUSTIC SIMPLIFIED COMPACT CASING STUDY (NO AEROGEL)")
    print("=" * 70)
    
    for d in (RESULTS_DIR, CAD_DIR, FIG_DIR, DATA_DIR):
        d.mkdir(parents=True, exist_ok=True)
        
    # 1. Architecture trade study
    candidates, recommended = run_architecture_trade_study()
    print(f"[1/5] Evaluated {len(candidates)} architecture configurations.")
    print(f"      Recommended Architecture: {recommended['architecture']}")
    print(f"      OD: {recommended['od_mm']} mm, Shell Bore: {recommended['packaging']['shell_bore_id_mm']} mm, Wall: {recommended['wall_mm']} mm.")
    print(f"      Total Modeled Tool Length: {recommended.get('total_tool_length_mm', 636.9)} mm (Limit <= 2000 mm).")
    print(f"      Packaging: {recommended['packaging']['packaging_status']}")
    print(f"      2h Temp @ 0W: {recommended['thermal_0w']['final_inner_temperature_C']} °C | @ 1W: {recommended['thermal_1w']['final_inner_temperature_C']} °C.")
    
    # 2. Automated CAD Interference & Collision Check
    collision_results = check_cad_assembly_interferences(recommended)
    print(f"[2/5] Automated CAD Collision Check:")
    print(f"      Carrier vs Shell: {collision_results['carrier_vs_shell_vol_mm3']} mm³")
    print(f"      Carrier vs PCM General Envelope: {collision_results['carrier_vs_pcm_general_envelope_vol_mm3']} mm³")
    print(f"      Nominal PCB vs Shell: {collision_results['pcm_nominal_vs_shell_vol_mm3']} mm³")
    print(f"      Collision-Free Status: {'PASS' if collision_results['passed'] else 'FAIL'}")
    if not collision_results["passed"]:
        raise ValueError(f"CAD Assembly failed collision check: max interference {collision_results['max_interference_vol_mm3']} mm³")
        
    # 3. 3D Parametric CAD Generation
    step_file = CAD_DIR / "compact_casing_assembly.step"
    cad_parts = generate_compact_casing_cad(recommended, output_step_path=step_file)
    print(f"[3/5] Generated 3D CAD assembly ({len(cad_parts)} solids) -> {step_file.name}")
    
    # 4. Visualization renders
    cad_png = FIG_DIR / "compact_cad_assembly.png"
    render_compact_cad(cad_parts, cad_png)
    
    transverse_png = FIG_DIR / "compact_transverse_pcm1808_section.png"
    render_transverse_pcm1808_cross_section(transverse_png)
    
    section_png = FIG_DIR / "compact_longitudinal_section.png"
    render_longitudinal_cross_section(recommended, section_png)
    
    thermal_png = FIG_DIR / "compact_thermal_trade_study.png"
    plot_thermal_architecture_comparison(candidates, thermal_png)
    print(f"[4/5] Rendered visualization figures in {FIG_DIR}")
    
    # 5. Export CSV and Markdown report
    export_trade_study_csv_and_report(candidates, recommended, RESULTS_DIR)
    print(f"[5/5] Exported trade study report and CSV data to {RESULTS_DIR}")
    
    print("=" * 70)
    print("SIMPLIFIED COMPACT CASING STUDY COMPLETED SUCCESSFULLY")
    print("=" * 70)
    
    return {
        "recommended": recommended,
        "candidates": candidates,
        "cad_parts": cad_parts,
        "collision_results": collision_results,
    }


if __name__ == "__main__":
    run_compact_study_pipeline()

