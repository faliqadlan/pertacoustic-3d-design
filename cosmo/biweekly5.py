"""Generate the preliminary Biweekly 5 HTI casing evidence package.

This is intentionally one runnable study, not a general-purpose pressure-vessel
framework. Results are screening evidence and must not be used for manufacture.
"""

from __future__ import annotations

import csv
import json
import math
import re
import subprocess
from pathlib import Path

import cadquery as cq
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from cosmo.core.mesh_generator import generate_mesh
from cosmo.core.result_extractor import extract_max_internal_temperature, parse_frd_temperatures
from cosmo.core.solver_interface import setup_and_run_calculix


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "biweekly-5"
CAD_DIR = OUT / "cad"
FIG_DIR = OUT / "figures"
SIM_DIR = OUT / "simulation"
CCX = ROOT / "cosmo" / "ccx" / "calculix_2.22_4win" / "ccx_static.exe"

PRESSURE_MPA = 68.9476  # 10,000 psi
EXTERNAL_TEMPERATURE_C = 150.0
INITIAL_TEMPERATURE_C = 25.0
HOUSING_LENGTH_MM = 425.0
ENDCAP_THICKNESS_MM = 50.0
ENDCAP_FILLET_MM = 10.0
FRONT_AXIAL_INSULATION_MM = 50.0
REAR_AXIAL_INSULATION_MM = 71.0
THERMAL_ZONES_LOCAL_MM = {
    "Analog front-end": (100.0, 125.0),
    "PCM1808": (130.0, 182.0),
    "STM32F411": (187.0, 242.0),
    "RTC/SD/power": (249.0, 304.0),
}
PEEK_THICKNESS_MM = 2.0
BOARD_CLEARANCE_MM = 1.5
STM32_ENVELOPE_MM = (55.0, 22.0, 12.0)
PCM1808_ENVELOPE_MM = (52.0, 32.0, 18.0)
REQUIRED_CLEAR_ID_MM = math.ceil(
    math.hypot(
        PCM1808_ENVELOPE_MM[1] + 2 * BOARD_CLEARANCE_MM,
        PCM1808_ENVELOPE_MM[2] + 2 * BOARD_CLEARANCE_MM,
    )
)
MATERIALS = json.loads((ROOT / "cosmo" / "material_library.json").read_text(encoding="utf-8"))


def lame_screen(od_mm: float, wall_mm: float) -> dict[str, float]:
    """Closed-end thick-cylinder screening under external pressure."""
    b = od_mm / 2.0
    a = b - wall_mm
    if a <= 0:
        raise ValueError("Wall consumes the bore")
    A = -PRESSURE_MPA * b * b / (b * b - a * a)
    B = -PRESSURE_MPA * a * a * b * b / (b * b - a * a)

    def mises(r: float) -> float:
        radial = A - B / (r * r)
        hoop = A + B / (r * r)
        axial = A
        return math.sqrt(
            0.5
            * (
                (radial - hoop) ** 2
                + (hoop - axial) ** 2
                + (axial - radial) ** 2
            )
        )

    max_mises = max(mises(a), mises(b))
    yield_strength = MATERIALS["Inconel718"]["yield_strength_mpa_150c_screening"]
    return {
        "max_von_mises_MPa": max_mises,
        "yield_safety_factor": yield_strength / max_mises,
    }


def elastic_buckling_screen(od_mm: float, wall_mm: float) -> dict[str, float]:
    """Conservative long-cylinder elastic external-pressure screen."""
    E = MATERIALS["Inconel718"]["elastic_modulus_mpa_150c"]
    nu = MATERIALS["Inconel718"]["poisson_ratio"]
    p_cr = 2.0 * E / math.sqrt(3.0 * (1.0 - nu * nu)) * (wall_mm / od_mm) ** 3
    return {
        "elastic_buckling_pressure_MPa": p_cr,
        "buckling_factor": p_cr / PRESSURE_MPA,
    }


def thread_retention_screen() -> dict[str, float]:
    major_diameter = 7.0 / 16.0 * 25.4
    pitch = 25.4 / 20.0
    engagement = 0.400 * 25.4
    minor_diameter = major_diameter - 1.23 * pitch
    thrust = PRESSURE_MPA * math.pi * major_diameter**2 / 4.0
    shear_area = 0.5 * math.pi * minor_diameter * engagement
    shear_stress = thrust / shear_area
    shear_allowable = (
        0.577 * MATERIALS["Inconel718"]["yield_strength_mpa_150c_screening"] / 2.0
    )
    return {
        "nominal_thread": "7/16-20 UNF-2A concept",
        "pitch_mm": pitch,
        "engagement_mm": engagement,
        "conservative_pressure_thrust_N": thrust,
        "thread_shear_stress_MPa": shear_stress,
        "thread_retention_safety_factor": shear_allowable / shear_stress,
        "note": "Conservative screen only; the HTI attachment thread is not the pressure seal.",
    }


def choose_wall(od_mm: float) -> dict[str, float | bool | str]:
    radial_budget = (od_mm - REQUIRED_CLEAR_ID_MM) / 2.0
    if radial_budget <= PEEK_THICKNESS_MM + 3.0:
        return {
            "od_mm": od_mm,
            "fit": False,
            "reason": f"Insufficient radial space for {REQUIRED_CLEAR_ID_MM} mm clear ID, PEEK, pressure wall, and aerogel.",
        }

    fallback = None
    for wall in np.arange(3.0, radial_budget - PEEK_THICKNESS_MM + 0.001, 0.25):
        aerogel = radial_budget - PEEK_THICKNESS_MM - wall
        if aerogel < 1.0:
            continue
        result = {
            "od_mm": od_mm,
            "fit": True,
            "clear_id_mm": REQUIRED_CLEAR_ID_MM,
            "inconel_wall_mm": round(float(wall), 3),
            "aerogel_mm": round(float(aerogel), 3),
            "peek_mm": PEEK_THICKNESS_MM,
        }
        result.update(lame_screen(od_mm, float(wall)))
        result.update(elastic_buckling_screen(od_mm, float(wall)))
        fallback = result
        if result["yield_safety_factor"] >= 2.0 and result["buckling_factor"] >= 2.0:
            result["structural_screen"] = "PASS"
            return result

    if fallback:
        fallback["structural_screen"] = "FAIL"
        fallback["reason"] = "No wall/aerogel split satisfies both preliminary structural factors."
        return fallback
    return {
        "od_mm": od_mm,
        "fit": False,
        "reason": "No positive aerogel thickness remains after fit and wall constraints.",
    }


def revised_geometry() -> dict[str, float | bool | str]:
    """The shortest locally screened 200 mm concept retained for full validation."""
    result = {
        "od_mm": 200.0,
        "fit": True,
        "clear_id_mm": REQUIRED_CLEAR_ID_MM,
        "inconel_wall_mm": 35.0,
        "endcap_thickness_mm": ENDCAP_THICKNESS_MM,
        "aerogel_mm": 42.5,
        "peek_mm": PEEK_THICKNESS_MM,
        "front_axial_insulation_mm": FRONT_AXIAL_INSULATION_MM,
        "rear_axial_insulation_mm": REAR_AXIAL_INSULATION_MM,
        "housing_length_mm": HOUSING_LENGTH_MM,
    }
    result.update(lame_screen(result["od_mm"], result["inconel_wall_mm"]))
    result.update(elastic_buckling_screen(result["od_mm"], result["inconel_wall_mm"]))
    result["structural_screen"] = "PASS"
    return result


def pressure_vessel_solid(geometry: dict[str, float]) -> cq.Workplane:
    """Closed, defeatured pressure body used for structural screening."""
    outer_radius = geometry["od_mm"] / 2
    inner_radius = outer_radius - geometry["inconel_wall_mm"]
    cap = geometry["endcap_thickness_mm"]
    outer = cq.Workplane("XY").circle(outer_radius).extrude(HOUSING_LENGTH_MM)
    cavity = (
        cq.Workplane("XY")
        .circle(inner_radius)
        .extrude(HOUSING_LENGTH_MM - 2 * cap)
        .translate((0, 0, cap))
        .edges("%CIRCLE")
        .fillet(ENDCAP_FILLET_MM)
    )
    return outer.cut(cavity)


def generate_closed_thermal_model(geometry: dict[str, float], output: Path) -> None:
    """Export the closed shell, radial stack, and available axial aerogel buffers."""
    outer_radius = geometry["od_mm"] / 2
    shell_inner = outer_radius - geometry["inconel_wall_mm"]
    aerogel_inner = shell_inner - geometry["aerogel_mm"]
    clear_radius = geometry["clear_id_mm"] / 2
    cap = geometry["endcap_thickness_mm"]
    internal_length = HOUSING_LENGTH_MM - 2 * cap
    electronics_end = max(end for _, end in THERMAL_ZONES_LOCAL_MM.values())

    insulation = (
        cq.Workplane("XY")
        .circle(shell_inner)
        .circle(aerogel_inner)
        .extrude(internal_length)
        .translate((0, 0, cap))
    )
    front_plug = (
        cq.Workplane("XY")
        .circle(clear_radius)
        .extrude(FRONT_AXIAL_INSULATION_MM)
        .translate((0, 0, cap))
    )
    rear_plug = (
        cq.Workplane("XY")
        .circle(clear_radius)
        .extrude(REAR_AXIAL_INSULATION_MM)
        .translate((0, 0, electronics_end))
    )
    carrier = (
        cq.Workplane("XY")
        .circle(aerogel_inner)
        .circle(clear_radius)
        .extrude(internal_length)
        .translate((0, 0, cap))
    )
    assembly = cq.Assembly(name="Closed_thermal_screen")
    for solid, name in (
        (pressure_vessel_solid(geometry), "Outer"),
        (insulation, "Insulation"),
        (front_plug, "FrontInsulation"),
        (rear_plug, "RearInsulation"),
        (carrier, "Chassis"),
    ):
        assembly.add(solid, name=name)
    assembly.save(str(output))


def _thermal_cells(geometry: dict[str, float], cells_per_layer: int):
    inner_radius = geometry["clear_id_mm"] / 2000.0
    layer_defs = [
        ("PEEK", geometry["peek_mm"] / 1000.0),
        ("Aerogel", geometry["aerogel_mm"] / 1000.0),
        ("Inconel718", geometry["inconel_wall_mm"] / 1000.0),
    ]
    edges = [inner_radius]
    names = []
    for name, thickness in layer_defs:
        local = np.linspace(edges[-1], edges[-1] + thickness, cells_per_layer + 1)[1:]
        edges.extend(local.tolist())
        names.extend([name] * cells_per_layer)
    return np.asarray(edges), names


def thermal_simulation(
    geometry: dict[str, float],
    power_w: float,
    cells_per_layer: int,
    duration_s: int = 3600,
) -> dict:
    edges, names = _thermal_cells(geometry, cells_per_layer)
    centers = np.sqrt(edges[:-1] * edges[1:])
    length_m = HOUSING_LENGTH_MM / 1000.0
    n = len(centers)
    capacities = np.zeros(n)
    for i, name in enumerate(names):
        props = MATERIALS[name]
        volume = math.pi * (edges[i + 1] ** 2 - edges[i] ** 2) * length_m
        capacities[i] = props["density"] * props["specific_heat"] * volume

    conductance = np.zeros(n - 1)
    for i in range(n - 1):
        interface = edges[i + 1]
        left_k = MATERIALS[names[i]]["conductivity"]
        right_k = MATERIALS[names[i + 1]]["conductivity"]
        resistance = (
            math.log(interface / centers[i]) / (2 * math.pi * length_m * left_k)
            + math.log(centers[i + 1] / interface)
            / (2 * math.pi * length_m * right_k)
        )
        conductance[i] = 1.0 / resistance

    outer_k = MATERIALS[names[-1]]["conductivity"]
    outer_resistance = math.log(edges[-1] / centers[-1]) / (
        2 * math.pi * length_m * outer_k
    )
    outer_g = 1.0 / outer_resistance
    inner_k = MATERIALS[names[0]]["conductivity"]
    inner_resistance = math.log(centers[0] / edges[0]) / (
        2 * math.pi * length_m * inner_k
    )

    dt = 60.0
    matrix = np.diag(capacities / dt)
    for i, g in enumerate(conductance):
        matrix[i, i] += g
        matrix[i + 1, i + 1] += g
        matrix[i, i + 1] -= g
        matrix[i + 1, i] -= g
    matrix[-1, -1] += outer_g
    inverse = np.linalg.inv(matrix)
    temperature = np.full(n, INITIAL_TEMPERATURE_C)
    source = np.zeros(n)
    source[0] = power_w
    source[-1] += outer_g * EXTERNAL_TEMPERATURE_C
    times = [0.0]
    inner_temperatures = [INITIAL_TEMPERATURE_C]
    profiles = [temperature.copy()]
    for step in range(1, int(duration_s / dt) + 1):
        rhs = capacities / dt * temperature + source
        temperature = inverse @ rhs
        inner_surface = temperature[0] + power_w * inner_resistance
        times.append(step * dt)
        inner_temperatures.append(float(inner_surface))
        profiles.append(temperature.copy())

    return {
        "times_s": np.asarray(times),
        "inner_temperature_C": np.asarray(inner_temperatures),
        "radii_m": centers,
        "final_profile_C": profiles[-1],
        "cells": n,
    }


def run_screening_matrix() -> tuple[list[dict], list[dict], dict, dict]:
    candidate_ods = (43, 50, 60, 65, 70, 80, 100, 120, 140, 146, 150)
    geometries = [choose_wall(float(od)) for od in candidate_ods]
    selected = revised_geometry()
    geometries.append(selected)
    rows = []
    fine_runs = {}
    for geometry in geometries:
        if not geometry.get("fit") or geometry.get("structural_screen") != "PASS":
            continue
        for power in (0.0, 1.0, 2.0):
            runs = {}
            for level in (4, 8, 16):
                runs[level] = thermal_simulation(geometry, power, level)
            fine = runs[16]
            fine_runs[(geometry["od_mm"], power)] = fine
            for hours in (1,):
                index = int(hours * 3600 / 60)
                value = float(fine["inner_temperature_C"][index])
                rows.append(
                    {
                        "od_mm": geometry["od_mm"],
                        "wall_mm": geometry["inconel_wall_mm"],
                        "aerogel_mm": geometry["aerogel_mm"],
                        "peek_mm": geometry["peek_mm"],
                        "power_W": power,
                        "duration_h": hours,
                        "inner_temperature_C": value,
                        "classification": "preferred"
                        if value <= 50.0
                        else "conditional"
                        if value <= 70.0
                        else "redesign",
                    }
                )
    selected["thermal_screen"] = (
        "PASS" if float(fine_runs[(selected["od_mm"], 1.0)]["inner_temperature_C"][-1]) <= 70 else "FAIL"
    )
    selected["selection_note"] = "Revised 200 mm concept; closed 3D validation governs final status."
    return geometries, rows, selected, fine_runs[(selected["od_mm"], 1.0)]


def _thread_solid() -> cq.Workplane:
    pitch = 25.4 / 20.0
    height = 0.400 * 25.4
    major = 7.0 / 16.0 * 25.4
    minor = major - 1.23 * pitch
    core = cq.Workplane("XY").circle(minor / 2.0).extrude(height)
    helix_radius = major / 2.0 - pitch * 0.30
    helix = cq.Wire.makeHelix(pitch, height, helix_radius)
    profile = (
        cq.Workplane("XZ")
        .center(helix_radius, 0)
        .polyline([(0, -pitch * 0.22), (pitch * 0.36, 0), (0, pitch * 0.22)])
        .close()
    )
    return core.union(profile.sweep(helix, isFrenet=True))


def build_detailed_cad(geometry: dict[str, float]) -> list[tuple[cq.Workplane, str, tuple]]:
    od = geometry["od_mm"]
    wall = geometry["inconel_wall_mm"]
    aerogel = geometry["aerogel_mm"]
    clear_id = geometry["clear_id_mm"]
    shell_id = od - 2 * wall
    aerogel_id = shell_id - 2 * aerogel
    z0 = 30.0
    cap = geometry["endcap_thickness_mm"]
    electronics_end = max(end for _, end in THERMAL_ZONES_LOCAL_MM.values())

    shell = (
        cq.Workplane("XY")
        .circle(od / 2)
        .circle(shell_id / 2)
        .extrude(HOUSING_LENGTH_MM)
        .translate((0, 0, z0))
    )
    insulation = (
        cq.Workplane("XY")
        .circle(shell_id / 2)
        .circle(aerogel_id / 2)
        .extrude(HOUSING_LENGTH_MM - 2 * cap)
        .translate((0, 0, z0 + cap))
    )
    front_buffer = (
        cq.Workplane("XY")
        .circle(clear_id / 2)
        .extrude(FRONT_AXIAL_INSULATION_MM)
        .translate((0, 0, z0 + cap))
    )
    for x in (-1.3, 0.0, 1.3):
        front_buffer = front_buffer.cut(
            cq.Workplane("XY")
            .center(x, 0)
            .circle(0.55)
            .extrude(FRONT_AXIAL_INSULATION_MM)
            .translate((0, 0, z0 + cap))
        )
    rear_buffer = (
        cq.Workplane("XY")
        .circle(clear_id / 2)
        .extrude(REAR_AXIAL_INSULATION_MM)
        .translate((0, 0, z0 + electronics_end))
    )
    carrier = (
        cq.Workplane("XY")
        .circle(aerogel_id / 2)
        .circle(clear_id / 2)
        .extrude(HOUSING_LENGTH_MM - 2 * cap)
        .translate((0, 0, z0 + cap))
    )

    thread = _thread_solid()
    neck = cq.Workplane("XY").circle(7.0).extrude(8.0).translate((0, 0, 10.16))
    transition = (
        cq.Workplane("XY")
        .workplane(offset=18.16)
        .circle(7.0)
        .workplane(offset=5.84)
        .circle(od / 2)
        .loft(combine=True)
    )
    shoulder = cq.Workplane("XY").circle(od / 2).extrude(6.0).translate((0, 0, 24.0))
    spigot = cq.Workplane("XY").circle((shell_id - 0.4) / 2).extrude(cap).translate((0, 0, z0))
    adapter = thread.union(neck).union(transition).union(shoulder).union(spigot)
    adapter = adapter.cut(cq.Workplane("XY").circle(2.2).extrude(42.0))
    for groove_z in (33.0, 38.0):
        groove = (
            cq.Workplane("XY")
            .circle((shell_id + 0.1) / 2)
            .circle((shell_id - 2.0) / 2)
            .extrude(2.0)
            .translate((0, 0, groove_z))
        )
        adapter = adapter.cut(groove)

    rear_plug = (
        cq.Workplane("XY")
        .circle((shell_id - 0.4) / 2)
        .extrude(cap)
        .translate((0, 0, z0 + HOUSING_LENGTH_MM - cap))
    )
    rear_shoulder = (
        cq.Workplane("XY")
        .circle(od / 2)
        .extrude(6.0)
        .translate((0, 0, z0 + HOUSING_LENGTH_MM))
    )
    rear_endcap = rear_plug.union(rear_shoulder)
    for groove_z in (z0 + HOUSING_LENGTH_MM - 10.0, z0 + HOUSING_LENGTH_MM - 5.0):
        groove = (
            cq.Workplane("XY")
            .circle((shell_id + 0.1) / 2)
            .circle((shell_id - 2.0) / 2)
            .extrude(2.0)
            .translate((0, 0, groove_z))
        )
        rear_endcap = rear_endcap.cut(groove)

    sensor = cq.Workplane("XY").circle(17.475 / 2).extrude(88.9).translate((0, 0, -88.9))
    sensor_end = cq.Workplane("XY").circle(19.05 / 2).extrude(8.0).translate((0, 0, -8.0))
    pins = []
    for x in (-1.3, 0.0, 1.3):
        pins.append(cq.Workplane("XY").center(x, 0).circle(0.35).extrude(6.0).translate((0, 0, -3.0)))

    zone_starts = {name: start for name, (start, _) in THERMAL_ZONES_LOCAL_MM.items()}
    front_end = cq.Workplane("XY").box(18, 8, 25, centered=(True, True, False)).translate((0, 0, z0 + zone_starts["Analog front-end"]))
    pcm = cq.Workplane("XY").box(32, 18, 52, centered=(True, True, False)).translate((0, 0, z0 + zone_starts["PCM1808"]))
    stm = cq.Workplane("XY").box(22, 12, 55, centered=(True, True, False)).translate((0, 0, z0 + zone_starts["STM32F411"]))
    reserve = cq.Workplane("XY").box(28, 16, 55, centered=(True, True, False)).translate((0, 0, z0 + zone_starts["RTC/SD/power"]))
    wires = []
    for x, color in zip((-1.3, 0.0, 1.3), ((0.8, 0.1, 0.1), (0.1, 0.7, 0.2), (0.1, 0.2, 0.8))):
        wire = cq.Workplane("XY").center(x, 0).circle(0.42).extrude(52.0).translate((0, 0, -2.0))
        wires.append((wire, f"Wire_{x}", color))

    parts = [
        (sensor, "HTI_sensor_reference_envelope", (0.35, 0.35, 0.38)),
        (sensor_end, "HTI_feedthrough_end", (0.25, 0.25, 0.28)),
        (adapter, "Threaded_front_adapter", (0.55, 0.58, 0.62)),
        (shell, "Inconel718_pressure_shell", (0.50, 0.52, 0.56)),
        (rear_endcap, "Rear_pressure_endcap", (0.55, 0.58, 0.62)),
        (insulation, "Sealed_aerogel", (0.92, 0.72, 0.25)),
        (front_buffer.union(rear_buffer), "Axial_aerogel_buffers", (0.95, 0.78, 0.30)),
        (carrier, "PEEK_carrier", (0.70, 0.45, 0.18)),
        (front_end, "Configurable_analog_front_end", (0.60, 0.25, 0.65)),
        (pcm, "PCM1808_provisional_envelope", (0.18, 0.55, 0.22)),
        (stm, "STM32F411_provisional_envelope", (0.15, 0.30, 0.75)),
        (reserve, "RTC_SD_power_reserve", (0.70, 0.20, 0.20)),
    ]
    parts.extend((pin, f"HTI_pin_{i+1}", (0.85, 0.65, 0.15)) for i, pin in enumerate(pins))
    parts.extend(wires)

    assembly = cq.Assembly(name="PertAcoustic_HTI_preliminary")
    for solid, name, color in parts:
        assembly.add(solid, name=name, color=cq.Color(*color))
    assembly.save(str(CAD_DIR / "hti_casing_detailed.step"))
    return parts


def render_cad(parts: list[tuple[cq.Workplane, str, tuple]]) -> None:
    fig = plt.figure(figsize=(14, 8), dpi=200)
    full = fig.add_subplot(121, projection="3d")
    detail = fig.add_subplot(122, projection="3d")

    def draw(ax, selected_parts, shell_alpha=0.15):
        for solid, name, color in selected_parts:
            if name in {"Sealed_aerogel", "PEEK_carrier"}:
                continue
            vertices, triangles = solid.val().tessellate(0.8)
            xyz = np.array([(v.x, v.y, v.z) for v in vertices])
            faces = [[xyz[i] for i in triangle] for triangle in triangles]
            is_shell = name in {"Inconel718_pressure_shell", "Threaded_front_adapter", "Rear_pressure_endcap"}
            alpha = shell_alpha if is_shell else 0.90
            edgecolor = (0.3, 0.35, 0.4, 0.15) if is_shell else "none"
            collection = Poly3DCollection(
                faces,
                facecolor=color,
                edgecolor=edgecolor,
                linewidths=0.2 if is_shell else 0,
                alpha=alpha,
            )
            ax.add_collection3d(collection)
        ax.view_init(elev=20, azim=-55)
        ax.set_xlabel("X (mm)", labelpad=8, fontsize=9)
        ax.set_ylabel("Y (mm)", labelpad=8, fontsize=9)
        ax.set_zlabel("Axial Z (mm)", labelpad=8, fontsize=9)
        ax.tick_params(labelsize=8)

    draw(full, parts, shell_alpha=0.12)
    # The casing has an Outer Diameter (OD) of 200 mm (radius = 100 mm).
    # Setting limits to (-120, 120) spans 240 mm, showing the 200 mm OD cylinder without clipping.
    full.set_xlim(-120, 120)
    full.set_ylim(-120, 120)
    full.set_zlim(-100, 480)
    # Physical aspect ratio: 240 mm width/depth vs 580 mm height
    full.set_box_aspect((240, 240, 580))
    full.set_title("Full Assembly (Sleek Proportional View)", fontsize=11, pad=12, fontweight="bold")

    detail_parts = [
        (_thread_solid(), "Nominal_7_16_20_UNF_2A_thread", (0.60, 0.62, 0.66))
    ] + [
        part
        for part in parts
        if part[1].startswith("HTI_pin_") or part[1].startswith("Wire_")
    ]
    draw(detail, detail_parts, shell_alpha=0.5)
    detail.set_xlim(-7, 7)
    detail.set_ylim(-7, 7)
    detail.set_zlim(-4, 15)
    detail.set_box_aspect((14, 14, 19))
    detail.set_title("Nominal HTI Thread & Three-Wire Feedthrough", fontsize=11, pad=12, fontweight="bold")

    fig.suptitle("Preliminary HTI-Connected PertAcoustic Casing Design", fontsize=13, fontweight="bold", y=0.97)
    fig.tight_layout()
    fig.subplots_adjust(top=0.90)
    fig.savefig(FIG_DIR / "cad_assembly.png", dpi=200)
    plt.close(fig)



def render_section(geometry: dict[str, float]) -> None:
    fig, ax = plt.subplots(figsize=(14, 5))
    z0 = 30
    length = HOUSING_LENGTH_MM
    radii = [
        (geometry["od_mm"] / 2, "#84878c", "Inconel 718"),
        (geometry["od_mm"] / 2 - geometry["inconel_wall_mm"], "#e4ad3f", "Aerogel tersegel"),
        (geometry["clear_id_mm"] / 2 + geometry["peek_mm"], "#b36f2c", "PEEK"),
        (geometry["clear_id_mm"] / 2, "white", "Ruang elektronik"),
    ]
    for radius, color, label in radii:
        ax.add_patch(plt.Rectangle((z0, -radius), length, 2 * radius, color=color, label=label))
    components = [
        (z0 + THERMAL_ZONES_LOCAL_MM["Analog front-end"][0], 25, 8, "AFE", "#9a4da2"),
        (z0 + THERMAL_ZONES_LOCAL_MM["PCM1808"][0], 52, 18, "PCM1808", "#2d8a3c"),
        (z0 + THERMAL_ZONES_LOCAL_MM["STM32F411"][0], 55, 12, "STM32F411", "#315fb5"),
        (z0 + THERMAL_ZONES_LOCAL_MM["RTC/SD/power"][0], 55, 16, "RTC/SD/daya", "#ad3434"),
    ]
    for z, width, height, label, color in components:
        ax.add_patch(plt.Rectangle((z, -height / 2), width, height, color=color, alpha=0.9))
        ax.text(z + width / 2, 0, label, ha="center", va="center", color="white", fontsize=8)
    ax.plot([-5, z0 + THERMAL_ZONES_LOCAL_MM["Analog front-end"][0]], [0, 0], color="#111", linewidth=2, label="Rute tiga konduktor")
    ax.annotate("HTI-02-DHPC/D", xy=(-5, 0), xytext=(-75, 25), arrowprops={"arrowstyle": "->"})
    ax.set_xlim(-90, z0 + HOUSING_LENGTH_MM + 10)
    ax.set_ylim(-geometry["od_mm"] / 2 - 5, geometry["od_mm"] / 2 + 5)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Posisi aksial (mm)")
    ax.set_ylabel("Radius (mm)")
    ax.set_title("Penampang konseptual, susunan material, dan elektronik")
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="upper center", ncol=5, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "longitudinal_section.png", dpi=180)
    plt.close(fig)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_thermal(rows: list[dict], selected: dict, selected_run: dict) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(selected_run["times_s"] / 3600, selected_run["inner_temperature_C"], linewidth=2.2)
    ax.axhline(50, color="green", linestyle="--", label="Preferred 50°C")
    ax.axhline(70, color="orange", linestyle="--", label="Conditional 70°C")
    ax.axhline(85, color="red", linestyle=":", label="PCM1808 IC screen 85°C")
    ax.set_xlabel("Time (h)")
    ax.set_ylabel("Inner carrier temperature (°C)")
    ax.set_title(f"Selected {selected['od_mm']:.0f} mm OD candidate, 1 W internal heat")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "thermal_history.png", dpi=180)
    plt.close(fig)

    plotted_ods = {60, 80, 100, 120, 140, 145, 150}
    one_hour = [
        r
        for r in rows
        if r["duration_h"] == 1
        and r["power_W"] == 1.0
        and int(r["od_mm"]) in plotted_ods
    ]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar([str(int(r["od_mm"])) for r in one_hour], [r["inner_temperature_C"] for r in one_hour], color="#4472c4")
    ax.axhline(70, color="orange", linestyle="--")
    ax.set_xlabel("Outer diameter (mm)")
    ax.set_ylabel("Temperature after 1 h (°C)")
    ax.set_title("Thermal trade study at 150°C and 1 W")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "thermal_tradeoff.png", dpi=180)
    plt.close(fig)


def run_calculix_thermal(selected: dict) -> dict:
    work = SIM_DIR / "calculix_thermal"
    work.mkdir(parents=True, exist_ok=True)
    layers = [
        {"name": "Outer", "material": "Inconel718", "thickness": selected["inconel_wall_mm"]},
        {"name": "Insulation", "material": "Aerogel", "thickness": selected["aerogel_mm"]},
        {"name": "FrontInsulation", "material": "Aerogel", "thickness": 0.0},
        {"name": "RearInsulation", "material": "Aerogel", "thickness": 0.0},
        {"name": "Chassis", "material": "PEEK", "thickness": selected["peek_mm"]},
    ]
    step = work / "selected_thermal.step"
    generate_closed_thermal_model(selected, step)
    rows = []
    cap = selected["endcap_thickness_mm"]
    power_z_bounds = (
        min(start for start, _ in THERMAL_ZONES_LOCAL_MM.values()),
        max(end for _, end in THERMAL_ZONES_LOCAL_MM.values()),
    )
    for label, mesh_min, mesh_max in (
        ("coarse", 4.0, 10.0),
        ("medium", 3.0, 8.0),
        ("fine", 2.0, 6.0),
    ):
        inp = work / f"selected_thermal_{label}.inp"
        generate_mesh(str(step), str(inp), layers, mesh_min, mesh_max, element_order=1)
        ok = setup_and_run_calculix(
            str(inp),
            layers,
            selected["od_mm"],
            ccx_path=str(CCX),
            bht=EXTERNAL_TEMPERATURE_C,
            time_seconds=3600,
            internal_power_w=1.0,
            include_end_boundaries=True,
            power_z_bounds=power_z_bounds,
        )
        frd = inp.with_suffix(".frd")
        row = {"mesh": label, "status": "passed" if ok and frd.exists() else "failed"}
        if row["status"] == "passed":
            row["inner_temperature_C"] = extract_max_internal_temperature(
                str(frd),
                target_time=3600,
                r_inner=selected["clear_id_mm"] / 2,
                z_bounds=power_z_bounds,
            )
        rows.append(row)
    medium, fine = rows[-2:]
    convergence = (
        abs(medium["inner_temperature_C"] - fine["inner_temperature_C"])
        / fine["inner_temperature_C"]
        * 100
        if medium["status"] == fine["status"] == "passed"
        else float("nan")
    )
    result = {
        "status": "passed" if all(row["status"] == "passed" for row in rows) and convergence < 5 else "failed",
        "acceptance": (
            "PASS"
            if all(row["status"] == "passed" for row in rows)
            and convergence < 5
            and fine.get("inner_temperature_C", float("inf")) <= 70
            else "FAIL"
        ),
        "power_W": 1.0,
        "mesh_convergence_pct": convergence,
        "meshes": rows,
        "note": "Closed 3D model includes front/rear Inconel caps and available axial aerogel buffers.",
    }
    if fine["status"] == "passed":
        result["inner_temperature_C"] = fine["inner_temperature_C"]
        nodes, steps = parse_frd_temperatures(str((work / "selected_thermal_fine.frd")))
        final = min(steps, key=lambda step: abs(step["time"] - 3600))
        result["component_max_temperature_C"] = _zone_max_temperatures(
            nodes, final["temperatures"], selected["clear_id_mm"] / 2
        )
    return result


def _zone_max_temperatures(nodes: dict, temperatures: dict, inner_radius_mm: float) -> dict[str, float]:
    result = {}
    for name, (z_min, z_max) in THERMAL_ZONES_LOCAL_MM.items():
        values = [
            temperatures[nid]
            for nid, (x, y, z) in nodes.items()
            if nid in temperatures
            and abs(math.hypot(x, y) - inner_radius_mm) < 0.5
            and z_min <= z <= z_max
        ]
        if not values:
            raise ValueError(f"No thermal nodes found for {name}")
        result[name] = max(values)
    return result


def axial_heat_leak_screen(geometry: dict[str, float]) -> dict[str, float]:
    clear_radius = geometry["clear_id_mm"] / 2000
    peek_outer = clear_radius + geometry["peek_mm"] / 1000
    aerogel_area = math.pi * clear_radius**2
    peek_area = math.pi * (peek_outer**2 - clear_radius**2)
    rear_length = REAR_AXIAL_INSULATION_MM / 1000

    def parallel_resistance(length: float) -> float:
        aerogel = length / (MATERIALS["Aerogel"]["conductivity"] * aerogel_area)
        peek = length / (MATERIALS["PEEK"]["conductivity"] * peek_area)
        return 1 / (1 / aerogel + 1 / peek)

    front = parallel_resistance(FRONT_AXIAL_INSULATION_MM / 1000)
    rear = parallel_resistance(rear_length)
    delta = EXTERNAL_TEMPERATURE_C - INITIAL_TEMPERATURE_C
    return {
        "front_resistance_K_W": front,
        "front_initial_heat_W": delta / front,
        "rear_resistance_K_W": rear,
        "rear_initial_heat_W": delta / rear,
    }


def parse_inp(path: Path):
    nodes = {}
    elements = {}
    mode = None
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            upper = line.upper()
            if upper == "*NODE" or upper.startswith("*NODE,"):
                mode = "node"
                continue
            if upper.startswith("*ELEMENT"):
                mode = "element" if "TYPE=C3D4" in upper or "TYPE=C3D10" in upper else None
                continue
            if line.startswith("*"):
                mode = None
                continue
            if not line:
                continue
            parts = [part.strip() for part in line.split(",") if part.strip()]
            if mode == "node":
                nodes[int(parts[0])] = tuple(float(v) for v in parts[1:4])
            elif mode == "element":
                elements[int(parts[0])] = tuple(int(v) for v in parts[1:])
    return nodes, elements


def _outer_faces(nodes: dict, elements: dict, outer_radius: float):
    face_nodes = {
        1: (0, 1, 2),
        2: (0, 3, 1),
        3: (1, 3, 2),
        4: (2, 3, 0),
    }
    result = []
    z_min = min(value[2] for value in nodes.values())
    z_max = max(value[2] for value in nodes.values())
    for eid, connectivity in elements.items():
        for face, indexes in face_nodes.items():
            ids = [connectivity[index] for index in indexes]
            radial = all(abs(math.hypot(nodes[nid][0], nodes[nid][1]) - outer_radius) < 0.05 for nid in ids)
            end = all(abs(nodes[nid][2] - z_min) < 0.05 for nid in ids) or all(
                abs(nodes[nid][2] - z_max) < 0.05 for nid in ids
            )
            if radial or end:
                result.append((eid, face))
    return result


def _support_nodes(nodes: dict) -> tuple[int, int, int]:
    """Minimal 3-2-1 constraints that remove rigid motion without clamping an end."""
    z_min = min(value[2] for value in nodes.values())
    end_nodes = [nid for nid, value in nodes.items() if abs(value[2] - z_min) < 0.05]
    anchor = min(end_nodes, key=lambda nid: math.hypot(nodes[nid][0], nodes[nid][1]))
    x_node = max(end_nodes, key=lambda nid: nodes[nid][0])
    y_node = max(end_nodes, key=lambda nid: nodes[nid][1])
    return anchor, x_node, y_node


def append_structural_case(path: Path, selected: dict, temperature_profile: dict) -> int:
    nodes, elements = parse_inp(path)
    faces = _outer_faces(nodes, elements, selected["od_mm"] / 2)
    if not faces:
        raise RuntimeError("No external tetrahedral faces identified for pressure loading")
    anchor, second, third = _support_nodes(nodes)
    radii_mm = temperature_profile["radii_m"] * 1000
    temperatures = temperature_profile["final_profile_C"]

    with path.open("a", encoding="utf-8") as handle:
        handle.write("\n** --- BIWEEKLY 5 STRUCTURAL SCREEN ---\n")
        handle.write("*MATERIAL, NAME=Inconel718Structural\n")
        handle.write(f"*ELASTIC\n{MATERIALS['Inconel718']['elastic_modulus_mpa_150c']}, {MATERIALS['Inconel718']['poisson_ratio']}\n")
        handle.write(f"*EXPANSION\n{MATERIALS['Inconel718']['thermal_expansion_per_c']}\n")
        handle.write("*SOLID SECTION, ELSET=Outer, MATERIAL=Inconel718Structural\n")
        handle.write("*NSET, NSET=NALL\n")
        node_ids = sorted(nodes)
        for i in range(0, len(node_ids), 12):
            handle.write(", ".join(str(value) for value in node_ids[i : i + 12]) + "\n")
        handle.write(f"*INITIAL CONDITIONS, TYPE=TEMPERATURE\nNALL, {INITIAL_TEMPERATURE_C}\n")
        handle.write("*STEP\n*STATIC\n1.0, 1.0\n")
        handle.write("*BOUNDARY\n")
        handle.write(f"{anchor}, 1, 3, 0\n{second}, 2, 3, 0\n{third}, 3, 3, 0\n")
        handle.write("*TEMPERATURE\n")
        for nid, (x, y, _) in nodes.items():
            radius = math.hypot(x, y)
            value = float(np.interp(radius, radii_mm, temperatures))
            handle.write(f"{nid}, {value:.6f}\n")
        handle.write("*DLOAD\n")
        for eid, face in faces:
            handle.write(f"{eid}, P{face}, {PRESSURE_MPA}\n")
        handle.write("*NODE FILE\nU\n*EL FILE\nS\n*END STEP\n")
    return len(faces)


def append_buckling_case(path: Path, selected: dict) -> int:
    nodes, elements = parse_inp(path)
    faces = _outer_faces(nodes, elements, selected["od_mm"] / 2)
    if not faces:
        raise RuntimeError("No external tetrahedral faces identified for buckling load")
    anchor, second, third = _support_nodes(nodes)
    with path.open("a", encoding="utf-8") as handle:
        handle.write("\n** --- BIWEEKLY 5 ELASTIC BUCKLING SCREEN ---\n")
        handle.write("*MATERIAL, NAME=Inconel718Structural\n")
        handle.write(
            f"*ELASTIC\n{MATERIALS['Inconel718']['elastic_modulus_mpa_150c']}, "
            f"{MATERIALS['Inconel718']['poisson_ratio']}\n"
        )
        handle.write("*SOLID SECTION, ELSET=Outer, MATERIAL=Inconel718Structural\n")
        handle.write("*STEP\n*BUCKLE\n1\n")
        handle.write("*BOUNDARY\n")
        handle.write(f"{anchor}, 1, 3, 0\n{second}, 2, 3, 0\n{third}, 3, 3, 0\n")
        handle.write("*DLOAD\n")
        for eid, face in faces:
            handle.write(f"{eid}, P{face}, {PRESSURE_MPA}\n")
        handle.write("*NODE FILE\nU\n*END STEP\n")
    return len(faces)


def _parse_buckling_factor(path: Path) -> float:
    waiting_for_value = False
    for line in path.read_text(errors="ignore").splitlines():
        upper = line.upper()
        numbers = re.findall(r"[-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?", line)
        if "BUCKLING FACTOR" in upper:
            if "=" in line and numbers:
                return float(numbers[-1])
            waiting_for_value = True
            continue
        if "MODE NO" in upper:
            waiting_for_value = True
            continue
        if waiting_for_value and len(numbers) >= 2:
            return float(numbers[-1])
    raise ValueError(f"No buckling factor found in {path}")


def _iter_frd_blocks(path: Path, marker: str, count: int):
    current = None
    with path.open(errors="ignore") as handle:
        for line in handle:
            if line.startswith(" -4") and marker in line:
                current = {}
                continue
            if current is not None and line.startswith(" -1"):
                try:
                    nid = int(line[3:13])
                    current[nid] = tuple(
                        float(line[13 + i * 12 : 25 + i * 12]) for i in range(count)
                    )
                except ValueError:
                    pass
            elif current is not None and line.startswith(" -3"):
                yield current
                current = None


def _parse_frd_last_block(path: Path, marker: str, count: int) -> dict[int, tuple[float, ...]]:
    blocks = list(_iter_frd_blocks(path, marker, count))
    return blocks[-1] if blocks else {}


def parse_structural_frd(path: Path) -> dict:
    displacements = _parse_frd_last_block(path, "DISP", 3)
    stresses = _parse_frd_last_block(path, "STRESS", 6)
    max_disp = max((math.sqrt(sum(value * value for value in values)) for values in displacements.values()), default=float("nan"))
    max_mises = 0.0
    for sx, sy, sz, sxy, syz, szx in stresses.values():
        mises = math.sqrt(
            0.5 * ((sx - sy) ** 2 + (sy - sz) ** 2 + (sz - sx) ** 2)
            + 3.0 * (sxy * sxy + syz * syz + szx * szx)
        )
        max_mises = max(max_mises, mises)
    return {"max_displacement_mm": max_disp, "max_nodal_von_mises_MPa": max_mises}


def _run_ccx(work: Path, job: str) -> bool:
    for suffix in (".frd", ".dat", ".sta", ".cvg", ".12d"):
        (work / f"{job}{suffix}").unlink(missing_ok=True)
    completed = subprocess.run(
        [str(CCX), "-i", job], cwd=work, capture_output=True, text=True
    )
    output = completed.stdout + completed.stderr
    (work / f"{job}.stdout.txt").write_text(output, encoding="utf-8")
    return completed.returncode == 0 and "*ERROR" not in output.upper() and "FATAL" not in output.upper()


def run_structural_fea(selected: dict, profile: dict) -> list[dict]:
    work = SIM_DIR / "calculix_structural"
    work.mkdir(parents=True, exist_ok=True)
    step = work / "pressure_shell.step"
    layers = [{"name": "Outer", "material": "Inconel718", "thickness": selected["inconel_wall_mm"]}]
    cq.exporters.export(pressure_vessel_solid(selected), str(step))
    rows = []
    for label, mesh_min, mesh_max in (
        ("coarse", 6.0, 10.0),
        ("medium", 4.5, 7.5),
        ("fine", 3.5, 5.5),
    ):
        inp = work / f"pressure_{label}.inp"
        generate_mesh(str(step), str(inp), layers, mesh_min, mesh_max, element_order=1)
        faces = append_structural_case(inp, selected, profile)
        job = inp.stem
        solved = _run_ccx(work, job)
        frd = work / f"{job}.frd"
        row = {
            "mesh": label,
            "pressure_faces": faces,
            "status": "passed" if solved and frd.exists() else "failed",
        }
        if row["status"] == "passed":
            row.update(parse_structural_frd(frd))
        row["analytical_buckling_factor"] = selected["buckling_factor"]
        rows.append(row)
    return rows


def plot_structural(selected: dict, fea_rows: list[dict]) -> None:
    analytic = selected["max_von_mises_MPa"]
    labels = ["Lamé"] + [row["mesh"] for row in fea_rows if row["status"] == "passed"]
    values = [analytic] + [row["max_nodal_von_mises_MPa"] for row in fea_rows if row["status"] == "passed"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(labels, values, color=["#7f8c8d"] + ["#4472c4"] * (len(values) - 1))
    ax.axhline(MATERIALS["Inconel718"]["yield_strength_mpa_150c_screening"] / 2, color="orange", linestyle="--", label="FoS 2 allowable")
    ax.set_ylabel("Von Mises stress (MPa)")
    ax.set_title("Pressure-shell structural screening")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "structural_comparison.png", dpi=180)
    plt.close(fig)


def fmt(value, digits=2):
    return f"{value:.{digits}f}"


def engineering_status(thermal_acceptance: str, structural_acceptance: str) -> str:
    return (
        "PASS"
        if thermal_acceptance == structural_acceptance == "PASS"
        else "VALIDATION IN PROGRESS"
    )


def write_report(
    geometries: list[dict],
    thermal_rows: list[dict],
    convergence: list[dict],
    selected: dict,
    thermal_fea: dict,
    structural_fea: list[dict],
    thread: dict,
) -> None:
    axial_screen = axial_heat_leak_screen(selected)
    one_hour = next(
        row
        for row in thermal_rows
        if row["od_mm"] == selected["od_mm"] and row["power_W"] == 1.0 and row["duration_h"] == 1
    )
    focus_rows = []
    table_geometries = geometries[:3]
    if selected not in table_geometries:
        table_geometries.append(selected)
    for geometry in table_geometries:
        focus_rows.append(
            f"| {geometry['od_mm']:.0f} | {'yes' if geometry.get('fit') else 'no'} | "
            f"{geometry.get('inconel_wall_mm', '-')} | {geometry.get('aerogel_mm', '-')} | "
            f"{geometry.get('structural_screen', '-')} | {geometry.get('reason', 'analytical geometry/wall screen only')} |"
        )
    structural_coarse = next((row for row in structural_fea if row["mesh"] == "coarse" and row["status"] == "passed"), None)
    structural_fine = next((row for row in structural_fea if row["mesh"] == "fine" and row["status"] == "passed"), None)
    structural_medium = next((row for row in structural_fea if row["mesh"] == "medium" and row["status"] == "passed"), None)
    stress_change = (
        abs(structural_medium["max_nodal_von_mises_MPa"] - structural_fine["max_nodal_von_mises_MPa"])
        / structural_fine["max_nodal_von_mises_MPa"]
        * 100
        if structural_medium and structural_fine
        else float("nan")
    )
    displacement_change = (
        abs(structural_medium["max_displacement_mm"] - structural_fine["max_displacement_mm"])
        / structural_fine["max_displacement_mm"]
        * 100
        if structural_medium and structural_fine
        else float("nan")
    )
    component_rows = []
    for name, value in thermal_fea.get("component_max_temperature_C", {}).items():
        classification = "target" if value <= 50 else "diterima sementara" if value <= 70 else "perlu desain ulang"
        if name == "PCM1808" and value > 85:
            classification += "; melebihi batas IC 85°C"
        component_rows.append(f"| {name} | {value:.2f} | {classification} |")
    headline_status = (
        "Preliminary screening: PASS"
        if selected["engineering_status"] == "PASS"
        else "Validasi desain masih berlangsung"
    )
    report = f"""# PERTACOUSTIC: Laporan Biweekly 5

Periode: Biweekly 5

Tanggal: 30 Juli 2026
Status: **{headline_status}**

Dokumen ini mencatat desain awal dan pemeriksaan menggunakan perhitungan serta simulasi. Status PASS, jika tercapai, hanya berarti bahwa model awal memenuhi kriteria pemeriksaan yang tertulis di laporan ini. Status tersebut **bukan** gambar manufaktur, sertifikasi bejana tekan, atau kualifikasi seal.

## 1. Rencana dan realisasi pekerjaan

Telah dilakukan desain casing, interface ke HTI-02-DHPC/D, electronics layout, thermal analysis, dan structural analysis. Persentase progress tidak ditambah karena bobot resmi pekerjaan belum tersedia.

## 2. Ringkasan kemajuan

- Casing dirancang dengan diameter luar (OD) {selected['od_mm']:.0f} mm, panjang {HOUSING_LENGTH_MM:.0f} mm, dinding Inconel {selected['inconel_wall_mm']:.0f} mm, tutup depan/belakang {selected['endcap_thickness_mm']:.0f} mm, aerogel radial {selected['aerogel_mm']:.1f} mm, dan PEEK {selected['peek_mm']:.0f} mm.
- Elektronik dipindahkan menjauh dari kedua tutup. Aerogel aksial di depan sepanjang {FRONT_AXIAL_INSULATION_MM:.0f} mm dan di belakang sepanjang {REAR_AXIAL_INSULATION_MM:.0f} mm menghambat panas yang masuk dari ujung casing.
- Model CAD memuat tiga jalur konduktor, bagian analog depan, PCM1808, STM32F411, serta ruang RTC/SD/daya.
- PA12/nylon hanya dipertimbangkan untuk komponen pendukung yang tidak menahan tekanan: dudukan elektronik, pemandu kabel, spacer, atau penahan tarikan kabel. PA12/nylon tidak dipakai sebagai dinding bejana tekan atau penghalang langsung terhadap fluida sumur.

## 3. Dasar desain dan istilah mekanik

Ukuran ulir yang dipakai adalah **nominal** `7/16-20 UNF-2A` pada casing untuk dipasangkan dengan `7/16-20 UNF-2B` pada HTI. Nominal berarti nama ukuran menurut standar; ukuran hasil manufaktur tetap dapat sedikit lebih besar atau kecil selama masih berada dalam toleransi yang diizinkan. `7/16` adalah diameter utama nominal, `20` berarti 20 ulir per inci, `UNF` adalah seri ulir halus, `2A` adalah kelas ulir luar, dan `2B` adalah kelas ulir dalam.

**Thread/ulir** adalah alur heliks untuk menyambungkan dua komponen. **Thread HTI** berarti ulir sambungan milik hydrophone HTI, bukan seal tekanan untuk ruang elektronik. Gambar HTI masih bertanda “for reference only”. Karena itu, **datum**—permukaan atau sumbu acuan untuk semua pengukuran—dan **thread tolerance**—batas penyimpangan diameter, pitch, serta bentuk ulir—harus dikonfirmasi kepada HTI sebelum manufaktur.

**Envelope** adalah kotak atau ruang batas yang disediakan agar suatu komponen pasti muat. Envelope sementara STM32F411 adalah 55 × 22 × 12 mm dan PCM1808 adalah 52 × 32 × 18 mm. **Assembly clearance** 1,5 mm adalah ruang tambahan agar board dapat dimasukkan dan tidak bergesekan. Dari ukuran tersebut digunakan **clear ID** {REQUIRED_CLEAR_ID_MM} mm, yaitu diameter dalam bersih yang benar-benar tersedia untuk elektronik setelah material casing dan insulasi dihitung.

![Rakitan CAD](figures/cad_assembly.png)

Adapter depan terdiri dari ulir nominal, **shoulder** atau bidang bertingkat yang menjadi penahan aksial, **spigot** atau bagian silinder yang masuk ke bore pasangan untuk menjaga posisi, tiga lubang kabel, dan dua alur seal awal. **Seal groove** adalah alur tempat O-ring atau seal. **Pressure seal** adalah komponen yang mencegah fluida bertekanan masuk ke ruang elektronik; lokasinya terpisah dari ulir HTI.

Jenis **elastomer** atau bahan lentur seal, **backup ring** yang menopang seal agar tidak terdorong keluar, **extrusion gap** atau celah tempat seal dapat tertekan keluar, dan **tolerance stack** atau gabungan seluruh variasi ukuran komponen belum ditetapkan. Karena itu, geometri alur yang terlihat di CAD masih konseptual dan belum boleh dibuat.

Dalam model struktur, **barrel** adalah dinding silinder panjang dan **endcap** adalah tutup tekanan di depan serta belakang. Model FEA dibuat **defeatured**, artinya detail kecil seperti ulir, kontak seal, dan alur lokal dihilangkan agar pemeriksaan global casing lebih stabil dan lebih cepat.

## 4. Susunan elektronik

![Penampang memanjang](figures/longitudinal_section.png)

Urutan aksialnya adalah HTI, analog front-end, PCM1808, STM32F411, lalu RTC/SD/daya. **Conductor path** adalah jalur listrik dari tiga pin/kabel HTI menuju elektronik. Tiga jalur dipertahankan karena pinout final belum dikonfirmasi.

**Analog front-end** adalah rangkaian pertama yang menerima sinyal analog kecil dari hydrophone, kemudian menguatkan dan menyaringnya sebelum masuk ke PCM1808. **Analog front-end zone** adalah ruang di dalam model yang dialokasikan untuk rangkaian tersebut. **Configurable analog front-end** berarti nilai penguatan, penyaringan, dan hubungan pin belum dikunci sehingga dapat disesuaikan setelah data HTI tersedia.

**Preamplifier mode** menjelaskan apakah preamplifier berada di dalam HTI, membutuhkan catu daya tertentu, dan bagaimana sinyal keluarannya dibaca. **Pinout** adalah daftar fungsi setiap pin, misalnya sinyal, ground, dan catu daya. PCM1808 mengubah sinyal analog menjadi data digital; STM32F411 mengendalikan akuisisi dan penyimpanan; ruang RTC/SD/daya disediakan untuk jam waktu nyata, kartu penyimpanan, dan rangkaian catu daya.

## 5. Pemeriksaan struktur

| OD (mm) | Muat | Dinding Inconel (mm) | Aerogel (mm) | Pemeriksaan analitis | Catatan |
|---:|---|---:|---:|---|---|
{chr(10).join(focus_rows)}

Perhitungan **Lamé** memperkirakan tegangan pada dinding silinder tebal akibat tekanan. **Equivalent stress** atau tegangan von Mises menyederhanakan kombinasi tegangan menjadi satu angka untuk dibandingkan dengan kekuatan luluh material. Hasil analitis dinding adalah {fmt(selected['max_von_mises_MPa'])} MPa dengan **factor of safety (FoS)** {fmt(selected['yield_safety_factor'])}. FoS adalah perbandingan kekuatan material terhadap beban terhitung; FoS 2 berarti kapasitas perhitungan dua kali beban rencana.

![Perbandingan struktur](figures/structural_comparison.png)

FEA menghitung seluruh barrel dan kedua endcap. Tegangan coarse, medium, dan fine adalah {fmt(structural_coarse['max_nodal_von_mises_MPa'])}, {fmt(structural_medium['max_nodal_von_mises_MPa'])}, dan {fmt(structural_fine['max_nodal_von_mises_MPa'])} MPa. **Displacement** adalah perpindahan bentuk akibat beban; hasil fine adalah {fmt(structural_fine['max_displacement_mm'], 3)} mm.

**Mesh convergence** memeriksa apakah hasil berubah ketika elemen dibuat lebih kecil. Perubahan medium ke fine adalah {fmt(stress_change)}% untuk tegangan dan {fmt(displacement_change)}% untuk displacement. Angka ini dilaporkan sebagai informasi karena pemeriksaan struktur periode ini dibatasi pada screening awal, bukan sertifikasi struktur.

**Buckling** adalah kegagalan ketika dinding tertekuk akibat tekanan luar sebelum material patah. Persamaan silinder panjang memberi buckling factor analitis {fmt(selected['buckling_factor'])}; faktor 2 berarti kapasitas hitung sedikitnya dua kali tekanan rencana. Pemeriksaan ini cukup untuk screening awal, tetapi bukan pengganti uji tekanan atau sertifikasi. Perhitungan retensi ulir memberi FoS {fmt(thread['thread_retention_safety_factor'])}, tetapi angka nominal ini belum menggantikan konfirmasi toleransi ulir dan desain seal.

**Thermo-mechanical load** berarti beban struktur yang menggabungkan tekanan dan perubahan temperatur. Model sekarang masih memindahkan profil temperatur radial ke model struktur, belum melakukan **direct mapping** dari setiap titik hasil termal 3D. Hasil struktur karena itu tetap dibaca sebagai screening awal.

## 6. Pemeriksaan termal

![Riwayat temperatur](figures/thermal_history.png)

**1 W** berarti elektronik menghasilkan energi panas satu joule setiap detik. Nilai 0, 1, dan 2 W pada studi radial adalah skenario tanpa panas internal, perkiraan operasi, dan skenario lebih berat. Pada 1 W, model radial kandidat ini menghasilkan {fmt(one_hour['inner_temperature_C'])}°C setelah satu jam.

Grafik radial lama untuk OD 146 mm tampak memenuhi batas 70°C karena model tersebut hanya mengizinkan panas mengalir melalui arah radial dan memakai **adiabatic ends**, yaitu ujung depan dan belakang dianggap tidak dapat dilewati panas. Anggapan itu berguna untuk perbandingan awal, tetapi tidak mewakili casing tertutup yang nyata.

Model 3D tertutup memasukkan barrel, endcap Inconel depan/belakang, aerogel radial, **front/rear axial aerogel buffer**, dan panas internal total 1 W. Axial aerogel buffer adalah lapisan aerogel memanjang di antara endcap panas dan elektronik agar jalur rambat panas menjadi lebih panjang.

| Pemeriksaan input model | Nilai |
|---|---|
| Temperatur awal | 25°C |
| Batas luar | 150°C pada barrel dan kedua endcap |
| Panas internal | 1 W total |
| Waktu | 3.600 detik atau 1 jam |
| Perubahan mesh medium ke fine | {fmt(thermal_fea['mesh_convergence_pct'], 4)}% |

| Zona elektronik | Temperatur maksimum batas rongga setelah 1 jam (°C) | Penilaian |
|---|---:|---|
{chr(10).join(component_rows)}

**Maximum cavity-boundary temperature** adalah temperatur tertinggi pada permukaan dalam yang menghadap ruang elektronik, bukan temperatur chip. Nilai maksimum model adalah {fmt(thermal_fea['inner_temperature_C'])}°C. **Chip junction temperature** adalah temperatur di bagian aktif silikon; nilainya belum dihitung karena board dan chip belum dimodelkan sebagai benda padat.

**Operating ceiling** adalah temperatur operasi maksimum yang diizinkan produsen komponen. PCM1808 memiliki ceiling 85°C [2], tetapi desain memakai batas pemeriksaan 70°C agar tersedia margin.

Perbedaan model radial dan model 3D tertutup berasal dari panas yang juga masuk melalui endcap. Menambah diameter dan aerogel radial memperlambat panas dari sisi barrel, tetapi tidak memperpanjang jalur panas dari depan atau belakang. Karena itu, desain ini juga memindahkan elektronik dan menambah insulasi aksial.

**Thermal resistance** dalam K/W menyatakan kenaikan beda temperatur yang dibutuhkan untuk mengalirkan satu watt panas; angka lebih besar berarti insulasi lebih baik. Perkiraan resistansi aksial depan adalah {fmt(axial_screen['front_resistance_K_W'], 1)} K/W dan belakang {fmt(axial_screen['rear_resistance_K_W'], 1)} K/W. **Axial heat leak** adalah panas yang merambat dari endcap menuju elektronik melalui jalur tersebut; perkiraan awalnya {fmt(axial_screen['front_initial_heat_W'])} W dari depan dan {fmt(axial_screen['rear_initial_heat_W'])} W dari belakang.

Angka **0,0007%** pada model lama berarti hasil mesh medium dan fine hanya berbeda sekitar tujuh bagian per sejuta. Itu menunjukkan hasil mesh termal lama sudah stabil, tetapi tidak berarti temperaturnya memenuhi batas. Nilai desain baru yang dipakai untuk status adalah {fmt(thermal_fea['mesh_convergence_pct'], 4)}%.

## 7. Hasil saat ini

Status desain: **{headline_status}**.

Status PASS ditetapkan apabila seluruh zona elektronik tidak melebihi 70°C, perubahan mesh termal di bawah 5%, tegangan statik fine tidak melebihi 500 MPa, serta perhitungan analitis memberi FoS luluh dan buckling factor sedikitnya 2. Status ini tetap merupakan screening awal, bukan sertifikasi struktur.

## 8. Pekerjaan berikutnya

### Dapat dilakukan sekarang dengan model

- Menjaga CAD, posisi elektronik, panjang insulasi, dan geometri endcap tetap konsisten dengan model yang sudah diperiksa.
- Mengulang simulasi bila ukuran, daya, material, tekanan, atau temperatur rencana berubah.
- Membuat daftar pendek material berdasarkan produk yang benar-benar tersedia.

### Memerlukan pengukuran, data pemasok, atau pengujian fisik

- Mengukur board STM32F411 dan PCM1808 beserta konektor dan header.
- Mengukur daya elektronik saat logging dan standby; angka 1 W saat ini masih asumsi.
- Memilih grade aerogel, PEEK, perlakuan panas Inconel, elastomer, dan backup ring yang dapat dibeli.
- Menghitung alur seal dan tolerance stack setelah material seal, celah, serta ukuran manufaktur ditetapkan.
- Menguji kupon Inconel/aerogel/PEEK di oven atau bak panas untuk membandingkan model dengan benda nyata.

## 9. Referensi

1. [High Tech Inc., HTI-02-DHPC/D](https://www.hightechincusa.com/products/hydrophones/hti02dhpc.html)
2. [Texas Instruments, PCM1808](https://www.ti.com/product/PCM1808)
3. [Special Metals, INCONEL Alloy 718 Technical Bulletin](https://www.specialmetals.com/documents/technical-bulletins/inconel/inconel-alloy-718.pdf)
4. [Victrex, PEEK 450G Technical Data Sheet](https://images.victrex.com/-/media/downloads/datasheets/victrex_tds_450g.pdf)
5. [Aspen Aerogels, Pyrogel HPS Product Data Sheet](https://www.aerogel.com/wp-content/uploads/2021/06/Pyrogel-HPS-Datasheet-English.pdf)
6. HTI-02-DHPC/D Mechanical Outline 02-001-25-00-00, supplier document marked "for reference only".
"""
    (OUT / "biweekly-5.md").write_text(report, encoding="utf-8")


def main() -> None:
    for directory in (OUT, CAD_DIR, FIG_DIR, SIM_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    geometries, thermal_rows, selected, selected_run = run_screening_matrix()
    convergence = []
    for od in [row["od_mm"] for row in geometries if row.get("structural_screen") == "PASS"]:
        runs = [r for r in thermal_rows if r["od_mm"] == od and r["power_W"] == 1.0 and r["duration_h"] == 1]
        if runs:
            coarse = thermal_simulation(next(g for g in geometries if g["od_mm"] == od), 1.0, 4)["inner_temperature_C"][-1]
            medium = thermal_simulation(next(g for g in geometries if g["od_mm"] == od), 1.0, 8)["inner_temperature_C"][-1]
            fine = runs[0]["inner_temperature_C"]
            convergence.append({
                "od_mm": od,
                "coarse_C": float(coarse),
                "medium_C": float(medium),
                "fine_C": float(fine),
                "medium_to_fine_pct": abs(float(fine) - float(medium)) / float(fine) * 100,
            })

    thread = thread_retention_screen()
    spec = {
        "status": "preliminary_engineering_only",
        "external_temperature_C": EXTERNAL_TEMPERATURE_C,
        "initial_temperature_C": INITIAL_TEMPERATURE_C,
        "external_pressure_MPa": PRESSURE_MPA,
        "focused_OD_mm": [43, 50, 60],
        "derived_OD_mm": [65, 70, 80, 100, 120, 140, 146, 150, 200],
        "durations_h": [1],
        "internal_power_W": [0, 1, 2],
        "manufacturing_constraints": [
            "Conventional CNC and laboratory assembly at UGM Geophysics Laboratory",
            "No vacuum insulation",
            "No added thermal-mass block",
        ],
        "board_clearance_mm": BOARD_CLEARANCE_MM,
        "required_clear_ID_mm": REQUIRED_CLEAR_ID_MM,
        "provisional_envelopes_mm": {"STM32F411": STM32_ENVELOPE_MM, "PCM1808": PCM1808_ENVELOPE_MM},
        "materials": MATERIALS,
        "selected_geometry": selected,
        "thread_screen": thread,
    }
    write_csv(OUT / "thermal_results.csv", thermal_rows)
    write_csv(OUT / "mesh_convergence.csv", convergence)

    parts = build_detailed_cad(selected)
    render_cad(parts)
    render_section(selected)
    plot_thermal(thermal_rows, selected, selected_run)

    generate_closed_thermal_model(selected, CAD_DIR / "hti_casing_analysis.step")

    thermal_fea = run_calculix_thermal(selected)
    structural_fea = run_structural_fea(selected, selected_run)
    structural_medium = next(row for row in structural_fea if row["mesh"] == "medium")
    structural_fine = next(row for row in structural_fea if row["mesh"] == "fine")
    stress_change = abs(
        structural_medium.get("max_nodal_von_mises_MPa", float("nan"))
        - structural_fine.get("max_nodal_von_mises_MPa", float("nan"))
    ) / structural_fine.get("max_nodal_von_mises_MPa", float("nan")) * 100
    displacement_change = abs(
        structural_medium.get("max_displacement_mm", float("nan"))
        - structural_fine.get("max_displacement_mm", float("nan"))
    ) / structural_fine.get("max_displacement_mm", float("nan")) * 100
    structural_qc = {
        "stress_medium_to_fine_pct": stress_change,
        "displacement_medium_to_fine_pct": displacement_change,
        "analytical_buckling_factor": selected["buckling_factor"],
        "scope": "analytical wall checks plus static FEA screening",
        "acceptance": "PASS" if (
            all(row.get("status") == "passed" for row in structural_fea)
            and structural_fine.get("max_nodal_von_mises_MPa", float("inf"))
            <= MATERIALS["Inconel718"]["yield_strength_mpa_150c_screening"] / 2
            and selected["yield_safety_factor"] >= 2
            and selected["buckling_factor"] >= 2
        ) else "FAIL",
    }
    selected["radial_thermal_screen"] = selected.pop("thermal_screen")
    selected["analytical_structural_screen"] = selected.pop("structural_screen")
    selected["thermal_screen"] = thermal_fea["acceptance"]
    selected["structural_screen"] = structural_qc["acceptance"]
    selected["engineering_status"] = engineering_status(
        thermal_fea["acceptance"], structural_qc["acceptance"]
    )
    if selected["engineering_status"] != "PASS":
        selected["reason"] = "At least one closed 3D acceptance criterion remains open."
    selected["selection_note"] = "Revised 200 mm concept; closed 3D validation governs final status."
    spec["selected_geometry"] = selected
    spec["status"] = "preliminary_pass" if selected["engineering_status"] == "PASS" else "validation_in_progress"
    (OUT / "input_spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    write_csv(OUT / "structural_fea_results.csv", structural_fea)
    plot_structural(selected, structural_fea)

    summary = {
        "engineering_status": selected["engineering_status"],
        "selected_geometry": selected,
        "selected_thermal_1h_1W_C": float(selected_run["inner_temperature_C"][-1]),
        "thermal_calculix": thermal_fea,
        "axial_heat_leak_screen": axial_heat_leak_screen(selected),
        "structural_calculix": structural_fea,
        "structural_qc": structural_qc,
        "thread_screen": thread,
        "limitations": [
            "Supplier-controlled HTI dimensions and preamplifier mode are not confirmed.",
            "Board envelopes are internet-derived and not physically measured.",
            "No seal, collapse, fatigue, acoustic, corrosion, or manufacturing qualification is claimed.",
        ],
        "manufacturing_constraints": [
            "UGM Geophysics Laboratory conventional CNC and assembly",
            "Vacuum insulation excluded",
            "Added thermal-mass block excluded",
        ],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(geometries, thermal_rows, convergence, selected, thermal_fea, structural_fea, thread)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
