"""Generate the preliminary Biweekly 5 HTI casing evidence package.

This is intentionally one runnable study, not a general-purpose pressure-vessel
framework. Results are screening evidence and must not be used for manufacture.
"""

from __future__ import annotations

import csv
import json
import math
import re
import shutil
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
HOUSING_LENGTH_MM = 255.0
FRONT_AXIAL_INSULATION_MM = 6.0
ELECTRONICS_END_Z_MM = 252.0
THERMAL_ZONES_LOCAL_MM = {
    "Analog front-end": (18.0, 43.0),
    "PCM1808": (48.0, 100.0),
    "STM32F411": (105.0, 160.0),
    "RTC/SD/power": (167.0, 222.0),
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


def pressure_vessel_solid(geometry: dict[str, float]) -> cq.Workplane:
    """Closed, defeatured pressure body used for structural screening."""
    outer_radius = geometry["od_mm"] / 2
    inner_radius = outer_radius - geometry["inconel_wall_mm"]
    cap = geometry["inconel_wall_mm"]
    outer = cq.Workplane("XY").circle(outer_radius).extrude(HOUSING_LENGTH_MM)
    cavity = (
        cq.Workplane("XY")
        .circle(inner_radius)
        .extrude(HOUSING_LENGTH_MM - 2 * cap)
        .translate((0, 0, cap))
    )
    return outer.cut(cavity)


def generate_closed_thermal_model(geometry: dict[str, float], output: Path) -> None:
    """Export the closed shell, radial stack, and available axial aerogel buffers."""
    outer_radius = geometry["od_mm"] / 2
    shell_inner = outer_radius - geometry["inconel_wall_mm"]
    aerogel_inner = shell_inner - geometry["aerogel_mm"]
    clear_radius = geometry["clear_id_mm"] / 2
    cap = geometry["inconel_wall_mm"]
    internal_length = HOUSING_LENGTH_MM - 2 * cap
    rear_buffer = HOUSING_LENGTH_MM + 30.0 - cap - ELECTRONICS_END_Z_MM

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
        .extrude(rear_buffer)
        .translate((0, 0, HOUSING_LENGTH_MM - cap - rear_buffer))
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
    candidate_ods = (43, 50, 60, 65, 70, 75, 80, 90, 100, 110, 120, 130, 140, 145, 146, 147, 148, 149, 150)
    geometries = [choose_wall(float(od)) for od in candidate_ods]
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
    selected = None
    for geometry in geometries:
        key = (geometry.get("od_mm"), 1.0)
        if key in fine_runs and float(fine_runs[key]["inner_temperature_C"][-1]) <= 70.0:
            selected = geometry
            break
    if selected is None:
        selected = next(
            geometry for geometry in geometries if geometry.get("structural_screen") == "PASS"
        )
        selected["thermal_screen"] = "FAIL"
        selected["selection_note"] = (
            "Smallest fit/structural reference candidate; no studied solid-aerogel candidate "
            "met the one-hour 70C target without crediting unverified electronics thermal mass."
        )
    else:
        selected["thermal_screen"] = "PASS"
        selected["selection_note"] = "Smallest radial-screen candidate; closed 3D validation is still required."
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
        .extrude(HOUSING_LENGTH_MM - 24)
        .translate((0, 0, z0 + 12))
    )
    front_buffer = (
        cq.Workplane("XY")
        .circle(clear_id / 2)
        .extrude(FRONT_AXIAL_INSULATION_MM)
        .translate((0, 0, z0 + 12))
    )
    for x in (-1.3, 0.0, 1.3):
        front_buffer = front_buffer.cut(
            cq.Workplane("XY")
            .center(x, 0)
            .circle(0.55)
            .extrude(FRONT_AXIAL_INSULATION_MM)
            .translate((0, 0, z0 + 12))
        )
    rear_buffer_length = z0 + HOUSING_LENGTH_MM - 12.0 - ELECTRONICS_END_Z_MM
    rear_buffer = (
        cq.Workplane("XY")
        .circle(clear_id / 2)
        .extrude(rear_buffer_length)
        .translate((0, 0, ELECTRONICS_END_Z_MM))
    )
    carrier = (
        cq.Workplane("XY")
        .circle(aerogel_id / 2)
        .circle(clear_id / 2)
        .extrude(HOUSING_LENGTH_MM - 24)
        .translate((0, 0, z0 + 12))
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
    spigot = cq.Workplane("XY").circle((shell_id - 0.4) / 2).extrude(12.0).translate((0, 0, 30.0))
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
        .extrude(12.0)
        .translate((0, 0, z0 + HOUSING_LENGTH_MM - 12.0))
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

    front_end = cq.Workplane("XY").box(18, 8, 25, centered=(True, True, False)).translate((0, 0, 48))
    pcm = cq.Workplane("XY").box(32, 18, 52, centered=(True, True, False)).translate((0, 0, 78))
    stm = cq.Workplane("XY").box(22, 12, 55, centered=(True, True, False)).translate((0, 0, 135))
    reserve = cq.Workplane("XY").box(28, 16, 55, centered=(True, True, False)).translate((0, 0, 197))
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
    fig = plt.figure(figsize=(13, 7))
    full = fig.add_subplot(121, projection="3d")
    detail = fig.add_subplot(122, projection="3d")

    def draw(ax, selected_parts):
        for solid, name, color in selected_parts:
            if name in {"Sealed_aerogel", "PEEK_carrier"}:
                continue
            vertices, triangles = solid.val().tessellate(0.8)
            xyz = np.array([(v.x, v.y, v.z) for v in vertices])
            faces = [[xyz[i] for i in triangle] for triangle in triangles]
            alpha = 0.18 if name == "Inconel718_pressure_shell" else 0.88
            collection = Poly3DCollection(
                faces,
                facecolor=color,
                edgecolor="none",
                alpha=alpha,
            )
            ax.add_collection3d(collection)
        ax.view_init(elev=18, azim=-55)
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y (mm)")
        ax.set_zlabel("Axial (mm)")

    draw(full, parts)
    full.set_xlim(-40, 40)
    full.set_ylim(-40, 40)
    full.set_zlim(-95, 275)
    full.set_box_aspect((80, 80, 370))
    full.set_title("Full assembly")

    detail_parts = [
        (_thread_solid(), "Nominal_7_16_20_UNF_2A_thread", (0.60, 0.62, 0.66))
    ] + [
        part
        for part in parts
        if part[1].startswith("HTI_pin_") or part[1].startswith("Wire_")
    ]
    draw(detail, detail_parts)
    detail.set_xlim(-7, 7)
    detail.set_ylim(-7, 7)
    detail.set_zlim(-4, 15)
    detail.set_box_aspect((14, 14, 19))
    detail.set_title("Nominal HTI thread and three-wire feedthrough")

    fig.suptitle("Preliminary HTI-connected PertAcoustic casing")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "cad_assembly.png", dpi=180)
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
        (48, 25, 8, "Front-end", "#9a4da2"),
        (78, 52, 18, "PCM1808", "#2d8a3c"),
        (135, 55, 12, "STM32F411", "#315fb5"),
        (197, 55, 16, "RTC/SD/daya", "#ad3434"),
    ]
    for z, width, height, label, color in components:
        ax.add_patch(plt.Rectangle((z, -height / 2), width, height, color=color, alpha=0.9))
        ax.text(z + width / 2, 0, label, ha="center", va="center", color="white", fontsize=8)
    ax.plot([-5, 48], [0, 0], color="#111", linewidth=2, label="Rute tiga konduktor")
    ax.annotate("HTI-02-DHPC/D", xy=(-5, 0), xytext=(-75, 25), arrowprops={"arrowstyle": "->"})
    ax.set_xlim(-90, 275)
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
    cap = selected["inconel_wall_mm"]
    rear_buffer = HOUSING_LENGTH_MM + 30.0 - cap - ELECTRONICS_END_Z_MM
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
            power_z_bounds=(cap + FRONT_AXIAL_INSULATION_MM, HOUSING_LENGTH_MM - cap - rear_buffer),
        )
        frd = inp.with_suffix(".frd")
        row = {"mesh": label, "status": "passed" if ok and frd.exists() else "failed"}
        if row["status"] == "passed":
            row["inner_temperature_C"] = extract_max_internal_temperature(
                str(frd),
                target_time=3600,
                r_inner=selected["clear_id_mm"] / 2,
                z_bounds=(cap + FRONT_AXIAL_INSULATION_MM, HOUSING_LENGTH_MM - cap - rear_buffer),
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
    rear_length = (HOUSING_LENGTH_MM + 30.0 - geometry["inconel_wall_mm"] - ELECTRONICS_END_Z_MM) / 1000

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
            if upper.startswith("*NODE"):
                mode = "node"
                continue
            if upper.startswith("*ELEMENT"):
                mode = "element" if "TYPE=C3D4" in upper else None
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
                elements[int(parts[0])] = tuple(int(v) for v in parts[1:5])
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


def _parse_frd_last_block(path: Path, marker: str, count: int) -> dict[int, tuple[float, ...]]:
    blocks = []
    current = None
    with path.open(errors="ignore") as handle:
        for line in handle:
            if line.startswith(" -4") and marker in line:
                current = {}
                blocks.append(current)
                continue
            if current is not None and line.startswith(" -1"):
                try:
                    nid = int(line[3:13])
                    values = tuple(float(line[13 + i * 12 : 25 + i * 12]) for i in range(count))
                    current[nid] = values
                except ValueError:
                    pass
            elif current is not None and line.startswith(" -3"):
                current = None
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
    scale = selected["inconel_wall_mm"] / 5.25
    for label, mesh_min, mesh_max in (
        ("coarse", 2.0 * scale, 4.0 * scale),
        ("medium", 1.5 * scale, 3.0 * scale),
        ("fine", 1.0 * scale, 2.0 * scale),
    ):
        inp = work / f"pressure_{label}.inp"
        generate_mesh(str(step), str(inp), layers, mesh_min, mesh_max, element_order=1)
        buckling_inp = work / f"buckling_{label}.inp"
        shutil.copyfile(inp, buckling_inp)
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
        append_buckling_case(buckling_inp, selected)
        buckling_job = buckling_inp.stem
        buckling_solved = _run_ccx(work, buckling_job)
        buckling_dat = work / f"{buckling_job}.dat"
        try:
            row["buckling_factor_fea"] = _parse_buckling_factor(buckling_dat)
            row["buckling_status"] = "passed" if buckling_solved else "failed"
        except (OSError, ValueError):
            row["buckling_status"] = "failed"
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
    buckling_change = (
        abs(structural_medium["buckling_factor_fea"] - structural_fine["buckling_factor_fea"])
        / structural_fine["buckling_factor_fea"]
        * 100
        if structural_medium and structural_fine
        else float("nan")
    )
    component_rows = []
    for name, value in thermal_fea.get("component_max_temperature_C", {}).items():
        classification = "preferred" if value <= 50 else "conditional" if value <= 70 else "redesign"
        if name == "PCM1808" and value > 85:
            classification += "; above the 85°C IC ceiling"
        component_rows.append(f"| {name} | {value:.2f} | {classification} |")
    report = f"""# PERTACOUSTIC: Biweekly 5 report

Periode: Biweekly 5

Tanggal: 30 Juli 2026

Status: preliminary engineering. Current design status: {selected['engineering_status']}.

Dokumen ini mencatat hasil desain dan simulation screening. Hasilnya belum dapat dipakai sebagai manufacturing drawing, pressure rating, atau seal qualification.

## 1. Rencana dan realisasi pekerjaan

Biweekly 4 mencatat progress kumulatif 20%. Pekerjaan periode ini meliputi desain casing, interface ke HTI-02-DHPC/D, electronics layout, thermal analysis, dan structural analysis. Persentase progress tidak ditambah karena bobot resmi pekerjaan belum tersedia.

## 2. Ringkasan progress

- Casing menggunakan nominal male thread `7/16-20 UNF-2A` untuk terhubung ke female thread HTI `7/16-20 UNF-2B`.
- Model CAD berisi tiga conductor paths, front analog section, PCM1808, STM32F411, dan ruang RTC/SD/power.
- Material stack tetap Inconel 718, sealed aerogel, dan PEEK. PA12/nylon hanya dipertimbangkan untuk carrier, cable guide, spacer, atau strain relief.
- Radial screening menghasilkan kandidat OD {selected['od_mm']:.0f} mm. Closed 3D models menunjukkan bahwa kandidat ini belum memenuhi thermal dan structural criteria.

## 3. Engineering work

### 3.1 Design basis

HTI mechanical outline dipakai sebagai reference untuk thread dan envelope. Drawing tersebut bertanda "for reference only", jadi datum dan thread tolerance masih harus dikonfirmasi kepada HTI. Preamplifier mode dan pinout juga belum diketahui. Karena itu, model mempertahankan tiga conductor paths dan configurable analog front-end.

Provisional board envelopes adalah 55 x 22 x 12 mm untuk STM32F411 dan 52 x 32 x 18 mm untuk PCM1808. Dengan assembly clearance 1,5 mm, clear ID yang dipakai adalah {REQUIRED_CLEAR_ID_MM} mm. Ukuran board harus diukur langsung sebelum detailed design.

Target electronics temperature adalah 50°C. Rentang 50 sampai 70°C dianggap conditional. Temperatur di atas 70°C membutuhkan redesign. PCM1808 mempunyai operating ceiling 85°C [2], tetapi angka 85°C bukan design target.

Desain dibatasi pada conventional CNC dan laboratory assembly di Laboratorium Geofisika UGM. Vacuum insulation dan added thermal-mass block tidak digunakan.

### 3.2 Mechanical concept

![CAD assembly](figures/cad_assembly.png)

Front adapter terdiri dari nominal thread, shoulder, spigot, tiga cable holes, dan dua preliminary seal grooves. Thread HTI menahan sensor. Pressure seal untuk electronics housing berada pada interface yang terpisah. Groove dimensions, elastomer, backup ring, extrusion gap, dan tolerance stack belum ditetapkan.

Rear pressure endcap sudah ditambahkan ke CAD. Defeatured FEA model memakai closed Inconel vessel agar pressure bekerja pada barrel dan kedua endcaps. Thread, seal contact, dan local groove geometry belum masuk ke FEA.

### 3.3 Electronics layout and materials

![Longitudinal section](figures/longitudinal_section.png)

Axial order pada model adalah HTI, analog front-end, PCM1808, STM32F411, lalu RTC/SD/power. Aerogel berada di dalam Inconel housing dan tidak bersentuhan langsung dengan well fluid.

Inconel properties berasal dari Special Metals [3]. Nilai strength tetap bergantung pada product form dan heat treatment. PEEK memakai Victrex 450G data dengan heat capacity sebagai screening assumption [4]. Pyrogel HPS memakai nominal density 200 kg/m³ dan conductivity 0,024 W/mK pada mean temperature 100°C [5]. Specific heat aerogel 1.000 J/kgK masih merupakan assumption dan perlu dikonfirmasi untuk material yang dibeli.

### 3.4 Geometry and structural screening

| OD (mm) | Fit | Inconel wall (mm) | Aerogel (mm) | Structural status | Note |
|---:|---|---:|---:|---|---|
{chr(10).join(focus_rows)}

Radial screening memilih OD {selected['od_mm']:.0f} mm dengan wall {selected['inconel_wall_mm']} mm, aerogel {selected['aerogel_mm']} mm, PEEK {selected['peek_mm']} mm, dan clear ID {selected['clear_id_mm']} mm. Lamé calculation memberi equivalent stress {fmt(selected['max_von_mises_MPa'])} MPa dan yield safety factor {fmt(selected['yield_safety_factor'])}. Long-cylinder equation memberi buckling factor {fmt(selected['buckling_factor'])}. Kedua calculation hanya mewakili cylindrical wall.

![Structural comparison](figures/structural_comparison.png)

Closed-vessel FEA belum mesh-converged. Coarse, medium, dan fine stress adalah {fmt(structural_coarse['max_nodal_von_mises_MPa'])}, {fmt(structural_medium['max_nodal_von_mises_MPa'])}, dan {fmt(structural_fine['max_nodal_von_mises_MPa'])} MPa. Displacement berubah dari {fmt(structural_coarse['max_displacement_mm'], 3)} menjadi {fmt(structural_fine['max_displacement_mm'], 3)} mm. Medium-to-fine changes masih {fmt(stress_change)}% untuk stress dan {fmt(displacement_change)}% untuk displacement.

Thermo-mechanical load masih memakai radial temperature profile, bukan direct mapping dari closed 3D thermal result. Karena itu, static stress dan displacement dipakai sebagai screening trend. Buckling analysis tidak memakai thermal load dan tetap menjadi independent failure check.

Buckling factors turun dari {fmt(structural_coarse['buckling_factor_fea'])} pada coarse mesh menjadi {fmt(structural_fine['buckling_factor_fea'])} pada fine mesh. Medium-to-fine change adalah {fmt(buckling_change)}%. Semua mesh berada di bawah acceptance factor 2. Karena hasil belum converged, nilai fine mesh tidak dianggap sebagai exact design stress. Kesimpulan FAIL tetap berlaku karena buckling margin tidak tercapai dan trend belum stabil.

Thread retention calculation memberi safety factor {fmt(thread['thread_retention_safety_factor'])}. Calculation ini masih nominal dan belum menggantikan thread tolerance atau seal design.

### 3.5 Thermal analysis

![Thermal history](figures/thermal_history.png)

Radial transient model memakai initial temperature 25°C, external surface 150°C, exposure 1 hour, dan internal heat 0, 1, atau 2 W. Pada 1 W, kandidat OD {selected['od_mm']:.0f} mm menghasilkan {fmt(one_hour['inner_temperature_C'])}°C. Hasil ini hanya berlaku untuk radial heat flow dengan adiabatic ends.

Closed 3D CalculiX model memasukkan front and rear Inconel endcaps, axial aerogel buffers, dan total internal heat 1 W. Fine mesh menghasilkan component-zone temperatures berikut.

| Model input check | Value |
|---|---|
| Initial temperature | 25°C |
| External boundary | 150°C on barrel and both end faces |
| Internal heat | 1 W total nodal CFLUX |
| Exposure time | 3600 s (1 hour) |
| Thermal medium-to-fine change | {fmt(thermal_fea['mesh_convergence_pct'], 4)}% |

| Electronics zone | Maximum inner-boundary temperature after 1 hour (°C) | Screening |
|---|---:|---|
{chr(10).join(component_rows)}

Maximum cavity-boundary temperature adalah {fmt(thermal_fea['inner_temperature_C'])}°C pada analog front-end zone, tepat setelah front axial aerogel buffer setebal {FRONT_AXIAL_INSULATION_MM:.0f} mm. PCM1808 zone boundary mencapai {fmt(thermal_fea['component_max_temperature_C']['PCM1808'])}°C, di atas operating ceiling 85°C. STM32F411 zone boundary mencapai {fmt(thermal_fea['component_max_temperature_C']['STM32F411'])}°C, sedikit di atas 70°C screening limit. Angka ini bukan chip junction temperature karena boards belum dimodelkan sebagai solids.

Perbedaan antara radial model dan closed 3D model berasal dari heat flow melalui endcaps dan axial sections. Menambah radial aerogel membantu bagian tengah housing, tetapi tidak menambah jarak thermal path di depan atau belakang. Karena itu, memperbesar OD saja tidak menyelesaikan temperatur di end zones.

Simple resistance cross-check memberi front axial resistance sekitar {fmt(axial_screen['front_resistance_K_W'], 1)} K/W untuk aerogel dan PEEK dalam parallel path. Pada initial temperature difference 125 K, heat leak awalnya sekitar {fmt(axial_screen['front_initial_heat_W'])} W. Rear path sekitar {fmt(axial_screen['rear_resistance_K_W'], 1)} K/W atau {fmt(axial_screen['rear_initial_heat_W'])} W. Nilai ini memakai ideal contact, tetapi cukup untuk menunjukkan bahwa axial heat leak sebanding dengan, bahkan lebih besar dari, internal heat 1 W.

Thermal mesh convergence memenuhi kriteria. Medium-to-fine change adalah {fmt(thermal_fea['mesh_convergence_pct'], 4)}%. External surface langsung ditahan pada 150°C, sehingga model ini conservative untuk transient heating. Model belum memakai measured electronics heat capacity, contact resistance, cable conduction, atau aerogel compression data. Nilai temperatur harus dibaca sebagai screening result, bukan predicted field-test temperature.

![Thermal OD comparison](figures/thermal_tradeoff.png)

### 3.6 Current result

Current design status adalah {selected['engineering_status']}.

Radial wall calculation lulus, tetapi closed 3D thermal model gagal pada PCM1808 dan end zones. Closed-vessel structural model juga belum memenuhi buckling factor dan mesh convergence criteria. Memperbesar radial aerogel tanpa mengubah endcap geometry atau electronics position tidak cukup.

## 4. Next work

- Measure the actual STM32F411 and PCM1808 boards, including connectors and headers.
- Measure electronics power during logging and standby conditions.
- Move temperature-sensitive electronics farther from both endcaps and increase axial insulation length.
- Redesign the flat end closures, then repeat static and buckling convergence studies.
- Select the actual aerogel, PEEK, Inconel heat treatment, and seal materials that can be purchased.
- Complete seal groove calculation and manufacturing tolerance stack.
- Validate a simple Inconel/aerogel/PEEK coupon in an oven or hot bath before relying on the 3D thermal model.

## 5. References

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
        "derived_OD_mm": [65, 70, 75, 80, 90, 100, 110, 120, 130, 140, 145, 146, 147, 148, 149, 150],
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
    buckling_change = abs(
        structural_medium.get("buckling_factor_fea", float("nan"))
        - structural_fine.get("buckling_factor_fea", float("nan"))
    ) / structural_fine.get("buckling_factor_fea", float("nan")) * 100
    structural_qc = {
        "stress_medium_to_fine_pct": stress_change,
        "displacement_medium_to_fine_pct": displacement_change,
        "buckling_medium_to_fine_pct": buckling_change,
        "acceptance": "PASS" if (
            all(row.get("status") == row.get("buckling_status") == "passed" for row in structural_fea)
            and max(stress_change, displacement_change, buckling_change) < 5
            and structural_fine.get("max_nodal_von_mises_MPa", float("inf"))
            <= MATERIALS["Inconel718"]["yield_strength_mpa_150c_screening"] / 2
            and structural_fine.get("buckling_factor_fea", 0) >= 2
        ) else "FAIL",
    }
    selected["radial_thermal_screen"] = selected.pop("thermal_screen")
    selected["analytical_structural_screen"] = selected.pop("structural_screen")
    selected["thermal_screen"] = thermal_fea["acceptance"]
    selected["structural_screen"] = structural_qc["acceptance"]
    selected["engineering_status"] = (
        "PASS" if thermal_fea["acceptance"] == structural_qc["acceptance"] == "PASS" else "FAIL"
    )
    if selected["engineering_status"] == "FAIL":
        selected["reason"] = "Closed 3D thermal/structural validation failed."
    selected["selection_note"] = "Radial-screen candidate; closed 3D validation governs final status."
    spec["selected_geometry"] = selected
    spec["status"] = "preliminary_fail" if selected["engineering_status"] == "FAIL" else "preliminary_pass"
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
