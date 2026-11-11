"""Integrated PertAcoustic concept, not a pressure-qualified instrument.

Run from the checkout with ``python -m cosmo.integrated_downhole``. All dimensions
are millimetres. Supplier interfaces and module envelopes remain provisional.
Historical compact-casing generators and results are never regenerated here.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
import math
from pathlib import Path
import platform
import subprocess
from typing import Any

import cadquery as cq
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from matplotlib.collections import PolyCollection
import numpy as np

from cosmo.compact_casing import (
    AFE_ENVELOPE_MM, PCM1808_ENVELOPE_MM, POWER_ENVELOPE_MM,
    RTC_ENVELOPE_MM, SD_ENVELOPE_MM, STM32F411_ENVELOPE_MM,
    compute_required_circular_diameter, structural_screening,
)
from cosmo.integrated_report import design_report

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "667ccd59cf6657a75dfe3cc2b4c67488737ef028"
EXECUTION_START = "3424b6d1f4d1fb6fad891760914d6d2c319ab3ca"
DEFAULT_OUTPUT = ROOT / "results" / "integrated-downhole"
STEEL = (0.48, 0.55, 0.62)
DARK_STEEL = (0.23, 0.31, 0.39)
POLYMER = (0.77, 0.55, 0.27)
BOARD = (0.12, 0.50, 0.39)
POWER = (0.28, 0.42, 0.70)
SENSOR = (0.21, 0.25, 0.30)
WIRE = (0.83, 0.39, 0.16)
SEAL = (0.92, 0.68, 0.22)
VOLUME_TOL_MM3 = 1e-4

SOURCES = {
    "HTI": "https://www.hightechincusa.com/products/hydrophones/hti02dhpc.html",
    "Sondex": "https://dam.bakerhughes.com/m/51dd2829b101fada/original/Sondex-noise-tool-spec.pdf",
    "Saft": "https://saft4u.saft.com/en/download_file/8bdd6f76-c9c5-422e-95bd-a18e0a12d80f/English",
    "TI": "https://www.ti.com/lit/ds/symlink/pcm1808.pdf",
    "IEC1": "https://webstore.iec.ch/en/publication/32074",
    "IEC2": "https://webstore.iec.ch/en/publication/33276",
}


@dataclass(frozen=True)
class Parameters:
    od_mm: float = 44.45
    wall_mm: float = 3.50
    electronics_barrel_mm: float = 390.0
    battery_barrel_mm: float = 200.0
    sensor_diameter_mm: float = 17.4752  # 0.688 in, public HTI nominal envelope
    sensor_length_mm: float = 88.9  # 3.5 in, public HTI nominal envelope
    cell_diameter_mm: float = 33.4
    cell_length_mm: float = 61.6  # conservative CAD reservation; termination TBD
    external_c: float = 70.0
    duration_s: float = 7200.0

    @property
    def bore_mm(self) -> float:
        return self.od_mm - 2 * self.wall_mm

    @property
    def stations(self) -> dict[str, float]:
        electronics_end = 175.0 + self.electronics_barrel_mm
        battery_start = electronics_end + 20.0
        battery_end = battery_start + self.battery_barrel_mm
        return {
            "nose_start": 0.0, "guard_start": 22.0, "sensor_start": 32.0,
            "bulkhead_start": 140.0, "boundary_start": 153.0,
            "boundary_end": 165.0, "electronics_start": 175.0,
            "electronics_end": electronics_end, "battery_start": battery_start,
            "battery_end": battery_end, "cap_end": battery_end + 30.0,
            "eye_start": battery_end + 44.0, "total_length": battery_end + 78.0,
        }

    def validate(self) -> None:
        if any(not math.isfinite(v) or v <= 0 for v in asdict(self).values()):
            raise ValueError("All design parameters must be finite and positive")
        if self.od_mm > 57.15 or self.wall_mm >= self.od_mm / 2:
            raise ValueError("Invalid shell envelope")
        if self.bore_mm < compute_required_circular_diameter(30.0, 12.0):
            raise ValueError("Bore cannot contain the inherited ADC clearance envelope")
        if self.electronics_barrel_mm < 390.0:
            raise ValueError("Electronics stack and harness turn require at least 390 mm barrel")
        if self.battery_barrel_mm < 2 * self.cell_length_mm + 73.0:
            raise ValueError("Battery, contacts and supports exceed available length")
        if self.cell_diameter_mm + 2.4 >= self.bore_mm - 0.85:
            raise ValueError("Battery holder needs cell clearance and wall allowance")
        if self.sensor_diameter_mm + 4 >= self.od_mm - 4:
            raise ValueError("Insufficient sensor-to-guard clearance")
        if 32 + self.sensor_length_mm + 2 >= 140:
            raise ValueError("Sensor and guard window exceed the wet-head reservation")
        if self.stations["total_length"] > 2000:
            raise ValueError("Complete instrument exceeds 2,000 mm")
        if self.external_c != 70.0 or self.duration_s != 7200:
            raise ValueError("The governing thermal envelope is 70 C / 7,200 s")


@dataclass
class Part:
    name: str
    label: str
    module: str
    kind: str
    material: str
    provenance: str
    solid: cq.Workplane
    color: tuple[float, float, float]
    exploded_offset_mm: tuple[float, float, float] = (0, 0, 0)


@dataclass
class Design:
    parameters: Parameters
    parts: list[Part] = field(default_factory=list)
    components: list[dict[str, Any]] = field(default_factory=list)

    def by_name(self, name: str) -> Part:
        for part in self.parts:
            if part.name == name:
                return part
        raise ValueError(f"Missing required assembly part: {name}")


def cylinder(radius: float, z: float, length: float) -> cq.Workplane:
    return cq.Workplane("XY").circle(radius).extrude(length).translate((0, 0, z))


def tube(ro: float, ri: float, z: float, length: float) -> cq.Workplane:
    return cq.Workplane("XY").circle(ro).circle(ri).extrude(length).translate((0, 0, z))


def block(w: float, h: float, z: float, length: float, x=0.0, y=0.0) -> cq.Workplane:
    return cq.Workplane("XY").box(w, h, length, centered=(True, True, False)).translate((x, y, z))


def wire_between(a, b, radius=0.55) -> cq.Workplane:
    vector = cq.Vector(*b) - cq.Vector(*a)
    if vector.Length <= 0:
        raise ValueError("Wire segment must have positive length")
    return cq.Workplane(obj=cq.Solid.makeCylinder(radius, vector.Length, cq.Vector(*a), vector.normalized()))


def union_all(solids: list[cq.Workplane]) -> cq.Workplane:
    if not solids:
        raise ValueError("Cannot build an empty module")
    result = solids[0]
    for solid in solids[1:]:
        result = result.union(solid)
    return result


def shapes(workplane: cq.Workplane) -> list[cq.Solid]:
    solids = workplane.solids().vals()
    if not solids or any(not solid.isValid() or solid.Volume() <= 0 for solid in solids):
        raise ValueError("Empty, invalid or nonpositive CAD solid")
    return solids


def bounds(workplane: cq.Workplane) -> dict[str, float]:
    boxes = [solid.BoundingBox() for solid in shapes(workplane)]
    return {
        "xmin": min(b.xmin for b in boxes), "xmax": max(b.xmax for b in boxes),
        "ymin": min(b.ymin for b in boxes), "ymax": max(b.ymax for b in boxes),
        "zmin": min(b.zmin for b in boxes), "zmax": max(b.zmax for b in boxes),
    }


def volume(workplane: cq.Workplane) -> float:
    return sum(solid.Volume() for solid in shapes(workplane))


def intersection_volume(a: cq.Workplane, b: cq.Workplane) -> float:
    """Empty is valid; every nonempty Boolean result must itself be valid."""
    result = a.intersect(b)
    if not result.objects:
        return 0.0
    shape = result.val()
    if shape is None or not shape.isValid():
        raise ValueError("Invalid Boolean intersection")
    return float(shape.Volume())


def build_design(p: Parameters | None = None) -> Design:
    p = p or Parameters()
    p.validate()
    d = Design(p)
    s = p.stations
    ro, ri = p.od_mm / 2, p.bore_mm / 2
    er0, er1 = 175.0, s["electronics_end"]
    br0, br1 = s["battery_start"], s["battery_end"]
    r_carrier = ri - 0.20

    def add(name, label, module, kind, material, provenance, solid, color=STEEL, offset=(0, 0, 0)):
        shapes(solid)
        d.parts.append(Part(name, label, module, kind, material, provenance, solid, color, offset))

    nose = cq.Workplane(obj=cq.Solid.makeCone(6.0, ro, 22.0)).cut(cylinder(3.0, -1, 24))
    add("drained_nose", "Open-drain protective nose", "wet_head", "housing", "Inconel718 candidate",
        "Estimated concept; drain is permanently open, no valve", nose, DARK_STEEL, (0, 0, -95))
    guard = tube(ro, ro - 2.0, 22.0, 118.0)
    for angle in range(0, 360, 60):
        slot = (cq.Workplane("YZ").center(0, 32 + p.sensor_length_mm / 2)
                .slot2D(p.sensor_length_mm + 4, 10.0, angle=90).extrude(ro + 2)
                .rotate((0, 0, 0), (0, 0, 1), angle))
        guard = guard.cut(slot)
    add("open_sensor_guard", "Six-window acoustic guard", "wet_head", "housing", "Inconel718 candidate",
        "Estimated open cage; acoustic transfer uncalibrated", guard, STEEL, (75, 0, -45))
    add("hti_reference", "HTI-02-DHPC/D nominal envelope", "sensor", "sensor", "Supplier-controlled sensor",
        "Public HTI nominal envelope; purchased variant/interface unresolved",
        cylinder(p.sensor_diameter_mm / 2, 32, p.sensor_length_mm), SENSOR, (-60, 0, -10))
    add("sensor_mount_reservation", "Provisional sensor mount / thread reserve", "sensor", "mechanical",
        "Metal candidate", "Nominal 7/16-20 provenance only; detailed thread/seal not modeled",
        tube(11.1125 / 2, 3.0, 32 + p.sensor_length_mm, 153 - 32 - p.sensor_length_mm)
        .union(tube(9, 3, 138, 2)),
        STEEL, (-60, 0, -10))
    retainer = tube(ro - 2, 11.1125 / 2, 134, 4).cut(block(0.4, p.od_mm + 2, 133, 6))
    add("split_sensor_retainer", "Split wet sensor-retention support", "wet_head", "holder", "Metal candidate",
        "Estimated split support below mount flange, captured by removable guard; fastening to verify",
        retainer, DARK_STEEL, (-30, 0, -10))

    # A stepped pressure-boundary reserve; all details remain unqualified.
    lower = cylinder(ro, 140, 35).union(cylinder(ri - 0.225, 175, 12))
    lower = lower.cut(cylinder(5.0, 139, 49)).cut(cylinder(6.0, 139, 16)).cut(cylinder(6.0, 165, 23))
    lower_seals = []
    for z in (178.5, 184.0):
        lower = lower.cut(tube(ri + 0.1, ri - 0.925, z, 1.5))
        lower_seals.append(tube(ri, ri - 0.925, z, 1.5))
    add("sensor_bulkhead", "Stepped wet/dry bulkhead", "pressure_boundary", "housing", "Inconel718 candidate",
        "Estimated pressure boundary and retention land; no rating", lower)
    add("lower_seal_reservations", "Lower closure seal reservations", "pressure_boundary", "seal",
        "Elastomer TBD", "Rectangular seal-space visualization, not production O-ring glands",
        union_all(lower_seals), SEAL)
    feedthrough = cylinder(6.0, 153, 2).union(cylinder(5.0, 155, 10))
    pins = []
    for x in (-2.0, 0.0, 2.0):
        feedthrough = feedthrough.cut(cylinder(0.4, 152, 14).translate((x, 0, 0)))
        pins.append(cylinder(0.4, 32 + p.sensor_length_mm, 187 - 32 - p.sensor_length_mm).translate((x, 0, 0)))
    add("sealed_feedthrough_reserve", "Shouldered insulating feedthrough", "pressure_boundary", "insulator",
        "Hermetic insulator TBD", "Estimated three-pin sealed feedthrough, supplier verification required",
        feedthrough, (0.84, 0.88, 0.91), (50, 0, 20))
    add("feedthrough_conductors", "Three reference conductors", "pressure_boundary", "conductor",
        "Conductor TBD", "Three-wire visualization only, not a verified HTI pinout", union_all(pins), WIRE, (50, 0, 20))

    add("electronics_barrel", "Electronics pressure barrel", "electronics_housing", "housing", "Inconel718 candidate",
        "Inherited shell OD/wall; length selected for integration", tube(ro, ri, er0, p.electronics_barrel_mm),
        STEEL, (85, 0, 60))
    add("lower_cartridge_spacer", "Axial cartridge spacer", "electronics_cartridge", "carrier", "PA66-GF30 candidate",
        "Estimated support, not pressure bearing", tube(r_carrier, 8, 187, 11), POLYMER, (0, 0, 75))

    rows = [
        ("afe", "Analog front-end", AFE_ENVELOPE_MM, 32, BOARD),
        ("adc", "PCM1808 reference ADC", PCM1808_ENVELOPE_MM, 79, BOARD),
        ("mcu", "STM32F411 reference MCU", STM32F411_ENVELOPE_MM, 146, BOARD),
        ("regulator", "5 V / 3.3 V regulation", POWER_ENVELOPE_MM, 216, POWER),
        ("rtc", "RTC / timing module", RTC_ENVELOPE_MM, 268, BOARD),
        ("storage", "Nonvolatile storage module", SD_ENVELOPE_MM, 310, BOARD),
        ("protection", "Power protection reservation", (18, 18, 8), 352, POWER),
    ]
    rail_length = er1 - 12 - 198
    rail = union_all([block(ri, 16, 198, rail_length, x=sign * (16 + ri / 2)) for sign in (-1, 1)])
    rail = rail.intersect(cylinder(r_carrier, 198, rail_length))
    supports = [rail, tube(r_carrier, 10, 198, 4), tube(r_carrier, 10, er1 - 16, 4)]
    keepers = []
    harness = [wire_between((0, 13.5, 222), (0, 13.5, er1 - 18), 0.65),
               wire_between((0, 0, 187), (0, 0, 198), 0.55),
               wire_between((0, 0, 205), (0, 0, 207), 0.55)]
    connectors = [block(8, 8, 198, 7)]
    for index, (name, label, envelope, relative_z, color) in enumerate(rows):
        length, width, height = envelope
        z = er0 + relative_z
        add(name, label, "electronics", "electronics", "Functional module envelope",
            "Inherited nominal module envelope, not measured/custom-PCB dimensions" if name != "protection"
            else "Estimated protection/circuit-break reservation", block(width, height, z, length), color, (-35, 0, 90))
        d.components.append({"name": name, "label": label, "z_start_mm": z, "length_mm": length,
                             "width_mm": width, "height_mm": height,
                             "provenance": "Estimated" if name == "protection" else "Inherited nominal, unmeasured"})
        for end_z in (z, z + length - 3):
            supports.append(block(2 * ri, 2, end_z, 3, y=-height / 2 - 1))
            keepers.append(block(32, 1, end_z, 3, y=height / 2 + 0.5))
        # Reserved harness branches terminate at module faces, not through modules.
        harness.append(wire_between((0, height / 2, z + length / 2), (0, 13.5, z + length / 2), 0.55))
        if index < len(rows) - 1:
            next_z = er0 + rows[index + 1][3]
            gap = next_z - z - length
            c0, clen = z + length + 4, gap - 8
            connectors.append(block(8, 6, c0, clen))
            harness += [wire_between((0, 0, z + length), (0, 0, c0)),
                        wire_between((0, 0, c0 + clen), (0, 0, next_z))]
    carrier = union_all(supports).intersect(cylinder(r_carrier, 187, er1 - 12 - 187))
    add("carrier_and_card_saddles", "Discrete rails and module saddles", "electronics_cartridge", "carrier",
        "PA66-GF30 prototype / PEEK benchmark", "Estimated dry internal carrier; wet properties unqualified",
        carrier, POLYMER, (0, 0, 75))
    add("removable_card_keepers", "Removable card-retention bridges", "electronics_cartridge", "carrier",
        "PA66-GF30 prototype / PEEK benchmark", "Estimated separate keepers fitted after radial module loading; fasteners TBD",
        union_all(keepers), POLYMER, (40, 0, 90))
    add("internal_connector_reservations", "Connectors / internal service-header reserves", "electronics", "connector",
        "Connector TBD", "Estimated plug/service and bend-space allocations, no selected connector",
        union_all(connectors), (0.30, 0.35, 0.42), (-35, 0, 90))
    add("acquisition_harness", "Signal and power harness reserves", "electronics", "wire", "Harness TBD",
        "Simplified routes and bend space, no wiring/pinout design", union_all(harness), WIRE, (-35, 0, 90))

    coupler = tube(ro, 15, er1, 20)
    coupler = coupler.union(tube(ri - 0.225, 15, er1 - 12, 12)).union(tube(ri - 0.225, 15, br0, 12))
    cseals = []
    for z in (er1 - 9, er1 - 4, br0 + 3, br0 + 8):
        coupler = coupler.cut(tube(ri + 0.1, ri - 0.925, z, 1.5))
        cseals.append(tube(ri, ri - 0.925, z, 1.5))
    add("dry_service_coupler", "Dry service coupling / retention reserves", "service_joint", "housing",
        "Inconel718 candidate", "Estimated threaded-retention zone; threads not detailed", coupler, DARK_STEEL, (0, 0, 125))
    add("coupler_seal_reservations", "Coupler seal reservations", "service_joint", "seal", "Elastomer TBD",
        "Unqualified seal-space envelopes", union_all(cseals), SEAL, (0, 0, 125))
    add("battery_barrel", "Battery pressure barrel", "battery_housing", "housing", "Inconel718 candidate",
        "Same preliminary shell as electronics compartment", tube(ro, ri, br0, p.battery_barrel_mm),
        STEEL, (85, 0, 160))

    cell1 = br0 + 28
    cell2 = cell1 + p.cell_length_mm + 8
    cell_end = cell2 + p.cell_length_mm
    holder_bottom, holder_top = br0 + 16, cell_end + 17
    holder_ro, holder_ri = ri - 0.425, p.cell_diameter_mm / 2 + 0.4
    holder = tube(holder_ro, holder_ri, holder_bottom, holder_top - holder_bottom)
    # A dedicated lead groove outside the cell keepout.
    lead_y = p.cell_diameter_mm / 2 + 0.9
    holder = holder.cut(block(3, 1.4, holder_bottom - 1, holder_top - holder_bottom + 2, x=1.5, y=lead_y))
    add("battery_holder", "Two-cell holder and insulated end supports", "battery_pack", "holder", "PEEK benchmark / polymer TBD",
        "Estimated holder; terminal style, swelling and thermal behavior TBD", holder, POLYMER, (0, 0, 180))
    lower_stop = tube(holder_ri - 0.15, 4, holder_bottom, cell1 - 4 - holder_bottom)
    lower_stop = lower_stop.cut(wire_between((1.5, 0, br0 + 17), (1.5, lead_y + 1, br0 + 17), 0.65))
    upper_stop = tube(holder_ri - 0.15, 4, cell_end + 4, holder_top - cell_end - 4)
    add("battery_lower_end_support", "Removable lower battery support", "battery_pack", "holder", "Insulating polymer TBD",
        "Separate insertion stop with lead channel; not an integral closed sleeve end", lower_stop, POLYMER, (0, 0, 155))
    add("battery_upper_end_support", "Removable upper battery support", "battery_pack", "holder", "Insulating polymer TBD",
        "Separate insertion stop; retained by axial spacer in the concept", upper_stop, POLYMER, (0, 0, 220))
    for i, z in enumerate((cell1, cell2), 1):
        add(f"cell_{i}", f"LSH 20 candidate cell {i}", "battery_cells", "battery", "Primary Li-SOCl2 candidate",
            "33.4 x 61.6 mm conservative nominal reservation; pack not qualified",
            cylinder(p.cell_diameter_mm / 2, z, p.cell_length_mm), (0.64, 0.71, 0.78), (-60, 0, 180))
    contacts = [cylinder(7, cell1 - 4, 4), cylinder(7, cell1 + p.cell_length_mm, 8), cylinder(7, cell_end, 4),
                wire_between((1.5, lead_y, br0 + 17), (1.5, lead_y, cell_end + 2), 0.30),
                wire_between((1.5, 0, cell_end + 2), (1.5, lead_y, cell_end + 2), 0.30),
                wire_between((1.5, 0, br0 + 17), (1.5, lead_y, br0 + 17), 0.30),
                wire_between((1.5, 0, br0 + 4), (1.5, 0, br0 + 17), 0.30),
                wire_between((-1.5, 0, br0 + 4), (-1.5, 0, cell1 - 4), 0.30)]
    add("battery_contacts_and_leads", "Separate contacts and series-pack lead reserves", "battery_cells", "conductor",
        "Contacts/wires TBD", "Disconnected conductive solids are separate conductors, not a shorting bridge",
        union_all(contacts), WIRE, (-60, 0, 180))
    plug = block(10, 8, br0 + 4, 10)
    for x in (-1.5, 1.5):
        plug = plug.cut(cylinder(0.30, br0 + 3, 12).translate((x, 0, 0)))
    add("battery_disconnect", "Dry battery disconnect body", "battery_pack", "connector", "Connector TBD",
        "Estimated two-contact body; exact connector unresolved", plug, POWER, (0, 0, 180))
    # A removable lead between the battery plug and protection module, inside dry bores.
    link = [wire_between((0, 13.5, 546.5), (0, 0, 546.5), 0.55),
            wire_between((0, 0, 546.5), (0, 0, br0 + 4), 0.55)]
    # The trunk and its power lead are one harness; their junction is fused.
    acquisition = d.by_name("acquisition_harness")
    acquisition.solid = acquisition.solid.union(union_all(link))
    spacers = [tube(holder_ro, 10, br0 + 12, 4), tube(holder_ro, 4, holder_top, br1 - 12 - holder_top)]
    add("battery_axial_spacers", "Battery cartridge axial spacers", "battery_pack", "holder", "Polymer TBD",
        "Estimated retention stops; shock/drop loads not qualified", union_all(spacers), POLYMER, (0, 0, 180))

    topcap = cylinder(ro, br1, 30).union(cylinder(ri - 0.225, br1 - 12, 12))
    topcap = topcap.union(cq.Workplane(obj=cq.Solid.makeCone(ro, 14, 14, cq.Vector(0, 0, br1 + 30))))
    tseals = []
    for z in (br1 - 9, br1 - 4):
        topcap = topcap.cut(tube(ri + 0.1, ri - 0.925, z, 1.5))
        tseals.append(tube(ri, ri - 0.925, z, 1.5))
    add("blind_upper_closure", "Blind upper closure and neck", "upper_interface", "housing", "Inconel718 candidate",
        "Estimated blind closure; no electric-line or field cablehead standard selected", topcap, STEEL, (0, 0, 250))
    add("upper_seal_reservations", "Upper closure seal reservations", "upper_interface", "seal", "Elastomer TBD",
        "Unqualified seal-space envelopes", union_all(tseals), SEAL, (0, 0, 250))
    eye = block(30, 12, br1 + 44, 34).edges("|Y").fillet(5)
    eye = eye.cut(wire_between((0, -8, br1 + 61), (0, 8, br1 + 61), 6))
    add("lifting_eye_reservation", "Generic deployment / retrieval eye", "upper_interface", "mechanical", "Metal candidate",
        "Estimated lifting interface, no rated load or finalized wireline connection", eye, DARK_STEEL, (0, 0, 285))
    # Fan exploded modules across the viewing plane while preserving each source solid.
    for part in d.parts:
        lateral, _, axial = part.exploded_offset_mm
        part.exploded_offset_mm = (0, lateral, axial)
    return d


def representation(d: Design, view: str) -> list[tuple[Part, cq.Workplane]]:
    if view not in {"complete", "sectional", "exploded"}:
        raise ValueError("Unknown assembly representation")
    cutter = block(100, 160, -200, d.parameters.stations["total_length"] + 500, x=-50)
    result = []
    for part in d.parts:
        solid = part.solid
        if view == "exploded":
            solid = solid.translate(part.exploded_offset_mm)
        elif view == "sectional" and part.kind in {"housing", "carrier", "holder", "seal", "insulator"}:
            solid = solid.cut(cutter)
        shapes(solid)
        result.append((part, solid))
    return result


def verify_design(d: Design) -> dict[str, Any]:
    """Full-part verification. No whitelist permits positive-volume collisions."""
    p = d.parameters
    p.validate()
    bb = {part.name: bounds(part.solid) for part in d.parts}
    zmin = min(b["zmin"] for b in bb.values())
    zmax = max(b["zmax"] for b in bb.values())
    envelope = cylinder(p.od_mm / 2 + 1e-6, zmin - 1, zmax - zmin + 2)
    outside = {}
    for part in d.parts:
        remainder = part.solid.cut(envelope)
        if remainder.objects:
            val = remainder.val()
            if val is None or not val.isValid():
                raise ValueError("Envelope Boolean failed")
            outside[part.name] = float(val.Volume())
    if any(v > VOLUME_TOL_MM3 for v in outside.values()):
        raise ValueError(f"Part outside instrument diameter: {outside}")
    collisions = []
    tested = 0
    max_volume = 0.0
    for index, a in enumerate(d.parts):
        for b in d.parts[index + 1:]:
            ba, bbb = bb[a.name], bb[b.name]
            if any(ba[axis + "max"] <= bbb[axis + "min"] + 1e-7 or
                   bbb[axis + "max"] <= ba[axis + "min"] + 1e-7 for axis in ("x", "y", "z")):
                continue
            tested += 1
            overlap = intersection_volume(a.solid, b.solid)
            max_volume = max(max_volume, overlap)
            if overlap > VOLUME_TOL_MM3:
                collisions.append({"a": a.name, "b": b.name, "overlap_mm3": overlap})
    if collisions:
        raise ValueError(f"Prohibited part interference: {collisions}")
    if zmax - zmin > 2000 + 1e-6:
        raise ValueError("Tool length exceeds requirement")

    # Coverage at a nominal barrier plane only, never a sealing qualification.
    closure = union_all([d.by_name(name).solid for name in
                         ("sensor_bulkhead", "sealed_feedthrough_reserve", "feedthrough_conductors")])
    disk = cylinder(p.od_mm / 2, 160, 0.5)
    uncovered = disk.cut(closure)
    if uncovered.objects and (uncovered.val() is None or not uncovered.val().isValid()):
        raise ValueError("Nominal boundary closure check failed")
    gap_volume = float(uncovered.val().Volume()) if uncovered.objects else 0.0
    if gap_volume > VOLUME_TOL_MM3:
        raise ValueError(f"Nominal CAD barrier has an open path: {gap_volume}")
    open_rays = []
    for angle in range(0, 360, 60):
        theta = math.radians(angle)
        z = 32 + p.sensor_length_mm / 2
        ray = wire_between((p.sensor_diameter_mm / 2 * math.cos(theta), p.sensor_diameter_mm / 2 * math.sin(theta), z),
                           ((p.od_mm / 2 + 1) * math.cos(theta), (p.od_mm / 2 + 1) * math.sin(theta), z), 0.5)
        overlap = intersection_volume(ray, d.by_name("open_sensor_guard").solid)
        if overlap > VOLUME_TOL_MM3:
            raise ValueError("Guard blocks a designed acoustic exposure window")
        open_rays.append({"azimuth_deg": angle, "guard_intersection_mm3": overlap})
    count = len(d.parts)
    return {
        "status": "PASS — NOMINAL CONCEPT GEOMETRY ONLY",
        "part_count": count, "solid_count": sum(len(shapes(part.solid)) for part in d.parts),
        "maximum_od_mm": p.od_mm, "overall_length_mm": round(zmax - zmin, 6),
        "shell_wall_mm": p.wall_mm, "shell_bore_mm": p.bore_mm,
        "all_pair_count": count * (count - 1) // 2,
        "boolean_pairs_after_bbox_pruning": tested,
        "maximum_prohibited_interference_mm3": max_volume, "collision_exclusions": [],
        "volume_tolerance_mm3": VOLUME_TOL_MM3,
        "outside_envelope_volume_mm3": sum(outside.values()),
        "nominal_boundary_uncovered_volume_mm3": gap_volume,
        "boundary_check_limit": "Ideal CAD coverage at z=160 mm only; does not prove leak-tightness or pressure rating",
        "wet_to_dry_transition_z_mm": [153, 165], "open_guard_rays": open_rays,
        "clearances_mm": {
            "adc_enclosing_diameter_with_1mm_each_side": compute_required_circular_diameter(30, 12),
            "adc_reserved_diametral_margin": p.bore_mm - compute_required_circular_diameter(30, 12),
            "carrier_to_bore_radial": 0.20, "battery_holder_to_bore_radial": 0.425,
            "cell_to_holder_radial": 0.4,
            "sensor_to_guard_radial_at_strut": (p.od_mm - 4 - p.sensor_diameter_mm) / 2,
            "wiring_trunk_radius": 0.65, "connector_bend_gap_each_end": 4.0,
        },
        "parts": [{"name": part.name, "module": part.module, "kind": part.kind,
                   "material": part.material, "provenance": part.provenance,
                   "bounds_mm": bb[part.name], "volume_mm3": volume(part.solid),
                   "exploded_offset_mm": list(part.exploded_offset_mm)} for part in d.parts],
    }


def export_step(parts: list[tuple[Part, cq.Workplane]], path: Path) -> dict[str, Any]:
    if not parts:
        raise ValueError("STEP export cannot be empty")
    path.parent.mkdir(parents=True, exist_ok=True)
    assembly = cq.Assembly(name=path.stem)
    expected_volume = 0.0
    expected_solids = 0
    for part, solid in parts:
        assembly.add(solid, name=part.name, color=cq.Color(*part.color))
        expected_volume += volume(solid)
        expected_solids += len(shapes(solid))
    assembly.export(str(path))
    if "SI_UNIT(.MILLI.,.METRE.)" not in path.read_text():
        raise ValueError(f"STEP length units are not explicitly millimetres: {path}")
    imported = cq.importers.importStep(str(path))
    actual_volume = volume(imported)
    actual_solids = len(shapes(imported))
    if actual_solids != expected_solids or not math.isclose(actual_volume, expected_volume, rel_tol=1e-7, abs_tol=1e-3):
        raise ValueError(f"STEP round trip changed solid coverage or volume: {path}")
    expected_boxes = [bounds(solid) for _, solid in parts]
    actual_box = bounds(imported)
    for axis in ("x", "y", "z"):
        for endpoint, reducer in (("min", min), ("max", max)):
            key = axis + endpoint
            if abs(actual_box[key] - reducer(b[key] for b in expected_boxes)) > 1e-4:
                raise ValueError(f"STEP round trip changed {key}: {path}")
    return {"file": path.name, "status": "PASS", "part_names": [part.name for part, _ in parts],
            "solid_count": actual_solids, "units": "mm", "volume_mm3": actual_volume, "bounds_mm": actual_box,
            "volume_relative_error": abs(actual_volume - expected_volume) / expected_volume}


def export_all(d: Design, output: Path) -> list[dict[str, Any]]:
    records = []
    for view in ("complete", "sectional", "exploded"):
        records.append(export_step(representation(d, view), output / f"integrated_{view}.step"))
    groups = {
        "wet_head": {"wet_head", "sensor"}, "sensor_bulkhead": {"pressure_boundary"},
        "electronics_cartridge": {"electronics", "electronics_cartridge"},
        "battery_pack": {"battery_pack", "battery_cells"},
        "pressure_housing": {"electronics_housing", "service_joint", "battery_housing", "upper_interface"},
    }
    for name, modules in groups.items():
        records.append(export_step([(part, part.solid) for part in d.parts if part.module in modules], output / f"module_{name}.step"))
    return records


def mesh_faces(solid: cq.Workplane) -> np.ndarray:
    faces = []
    for shape in shapes(solid):
        vertices, triangles = shape.tessellate(0.40, 0.15)
        xyz = np.array([(v.z, v.x, v.y) for v in vertices])  # axial Z displayed horizontally
        faces.extend(xyz[np.array(triangles)])
    return np.asarray(faces)


def draw_projected(ax, parts, right, up, eye):
    """Depth-buffered CAD rendering placed on a physical-aspect engineering sheet."""
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(245 / 255, 247 / 255, 250 / 255)
    renderer.SetBackgroundAlpha(0)
    all_vertices = []
    for part, solid in parts:
        faces = mesh_faces(solid)
        vertices = np.ascontiguousarray(faces.reshape(-1, 3))
        all_vertices.append(vertices)
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(vertices, deep=True))
        cells = vtk.vtkCellArray()
        offsets = np.arange(0, len(vertices) + 1, 3, dtype=np.int64)
        indices = np.arange(len(vertices), dtype=np.int64)
        cells.SetData(numpy_to_vtkIdTypeArray(offsets, deep=True), numpy_to_vtkIdTypeArray(indices, deep=True))
        data = vtk.vtkPolyData()
        data.SetPoints(points)
        data.SetPolys(cells)
        clean = vtk.vtkCleanPolyData()
        clean.SetInputData(data)
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputConnection(clean.GetOutputPort())
        normals.SetFeatureAngle(45)
        normals.ConsistencyOn()
        normals.AutoOrientNormalsOn()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(normals.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*part.color)
        actor.GetProperty().SetAmbient(0.25)
        actor.GetProperty().SetDiffuse(0.75)
        actor.GetProperty().SetSpecular(0.28)
        actor.GetProperty().SetSpecularPower(35)
        renderer.AddActor(actor)
    vertices = np.concatenate(all_vertices)
    points = np.column_stack((vertices @ right, vertices @ up))
    low, high = points.min(axis=0), points.max(axis=0)
    span = high - low
    aspect = max(span[0] / max(span[1], 1), 1.0)
    width = 2800 if aspect > 5 else 1500
    height = max(int(width / aspect), 200)
    aspect = width / height
    half_height = max(span[1] / 2, span[0] / (2 * aspect)) * 1.06
    mid = (low + high) / 2
    depth = vertices @ eye
    center = right * mid[0] + up * mid[1] + eye * (depth.min() + depth.max()) / 2
    camera = renderer.GetActiveCamera()
    camera.SetFocalPoint(*center)
    camera.SetPosition(*(center + eye * 10000))
    camera.SetViewUp(*up)
    camera.ParallelProjectionOn()
    camera.SetParallelScale(half_height)
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetAlphaBitPlanes(1)
    window.SetMultiSamples(4)
    window.SetSize(width, height)
    window.AddRenderer(renderer)
    try:
        renderer.ResetCameraClippingRange()
        window.Render()
        capture = vtk.vtkWindowToImageFilter()
        capture.SetInput(window)
        capture.SetInputBufferTypeToRGBA()
        capture.ReadFrontBufferOff()
        capture.Update()
        rgba = vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(height, width, 4)
        image = np.flipud(rgba).copy()
    finally:
        window.Finalize()
    half_width = half_height * aspect
    ax.imshow(image, extent=(mid[0] - half_width, mid[0] + half_width, mid[1] - half_height, mid[1] + half_height), zorder=0)
    ax.set_xlim(mid[0] - half_width, mid[0] + half_width)
    ax.set_ylim(mid[1] - half_height, mid[1] + half_height)
    ax.set_aspect("equal")


def draw_3d(ax, parts, *, section=False):
    # True isometric camera, rolled so the long tool axis is horizontal.
    eye = np.array([1.0, -1.0, 1.0])
    eye /= np.linalg.norm(eye)
    right = np.array([2.0, 1.0, -1.0])
    right /= np.linalg.norm(right)
    up = np.cross(eye, right)
    draw_projected(ax, parts, right, up, eye)
    ax.set_axis_off()


def render_views(d: Design, output: Path) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    paths = []
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    subtitle = "PRELIMINARY CONCEPT • 70 °C / 2 h • pressure and sealing qualification unresolved"
    for view, title in (("complete", "INTEGRATED DOWNHOLE INSTRUMENT"),
                        ("sectional", "LONGITUDINAL CUTAWAY"), ("exploded", "EXPLODED ASSEMBLY")):
        fig = plt.figure(figsize=(18, 7), facecolor="#f5f7fa")
        fig.text(0.045, 0.93, "PERTACOUSTIC", fontsize=13, color="#17736e", weight="bold")
        fig.text(0.045, 0.87, title, fontsize=25, color="#182c3e", weight="bold")
        fig.text(0.045, 0.815, subtitle, fontsize=11, color="#5c6e7e")
        ax = fig.add_axes([0.025, 0.30, 0.95, 0.47], facecolor="#f5f7fa")
        draw_3d(ax, representation(d, view), section=(view == "sectional"))
        if view == "complete":
            caption = f"Isometric projection  |  {d.parameters.stations['total_length']:.1f} mm overall  |  Ø {d.parameters.od_mm:.2f} mm maximum  |  single hydrophone / onboard memory / battery power"
            notes = [("WET ACOUSTIC HEAD", "Open six-window guard and drained nose\nPressure-compensated HTI reference sensor"),
                     ("DRY ACQUISITION", "AFE → ADC → MCU / timing / storage\nRemovable carrier, plug and harness reserves"),
                     ("DRY POWER / DEPLOYMENT", "Two-cell candidate pack and protection\nBlind upper closure; generic retrieval eye")]
        elif view == "sectional":
            caption = "Front half removed from housing/supports only; functional component envelopes retained in full"
            notes = [("WET / DRY BOUNDARY", "Stepped bulkhead + insulating feedthrough\nConceptual seals; no leak-tightness claim"),
                     ("PACKAGING", f"{d.parameters.bore_mm:.2f} mm bore / {d.parameters.wall_mm:.2f} mm shell wall\n0.20 mm nominal carrier radial clearance"),
                     ("ELECTRONICS / CELLS", "Nominal and estimated envelopes, not custom PCBs\nBattery, connector and thermal validation pending")]
        else:
            caption = "All modules are translated copies of the complete assembly; source part identities and volumes preserved"
            notes = [("LOWER MODULES", "Nose / slotted guard / sensor / bulkhead\nFeedthrough and seal spaces separated"),
                     ("ELECTRONICS CARTRIDGE", "Barrel / support rails / module envelopes\nConnectors and harness shown separately"),
                     ("UPPER MODULES", "Coupler / battery barrel / holder / cells\nUpper closure and retrieval interface")]
        fig.text(0.045, 0.27, caption, fontsize=11, color="#243e53")
        for x, (heading, text) in zip((0.045, 0.36, 0.68), notes):
            fig.text(x, 0.19, heading, fontsize=10, weight="bold", color="#17736e")
            fig.text(x, 0.135, text, fontsize=10, linespacing=1.6, color="#536779", va="center")
        path = output / f"integrated_{view}.png"
        fig.savefig(path, dpi=180, facecolor=fig.get_facecolor())
        plt.close(fig)
        paths.append(path)

    # Exact CAD triangle projections provide two orthographic silhouettes.
    fig, axes = plt.subplots(2, 1, figsize=(18, 6), facecolor="#f5f7fa")
    for ax, horizontal, title in zip(axes, (1, 2), ("FRONT ORTHOGRAPHIC — X / Z", "SIDE ORTHOGRAPHIC — Y / Z")):
        right = np.array([1, 0, 0])
        up = np.eye(3)[horizontal]
        eye = np.cross(right, up)
        draw_projected(ax, representation(d, "complete"), right, up, eye)
        ax.set_xlim(-25, d.parameters.stations["total_length"] + 30)
        ax.set_ylim(-40, 40)
        ax.set_aspect("equal")
        ax.set_title(title, loc="left", fontsize=11, color="#243e53")
        ax.set_xlabel("Axial Z (mm)")
        ax.set_ylabel("mm")
        ax.set_facecolor("#f5f7fa")
        ax.grid(alpha=0.15)
    fig.suptitle(f"PERTACOUSTIC  |  {d.parameters.stations['total_length']:.1f} × Ø{d.parameters.od_mm:.2f} mm nominal", fontsize=19, color="#182c3e")
    fig.tight_layout()
    path = output / "integrated_orthographic.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    paths.append(path)
    paths.append(render_detail(d, output))
    paths.append(render_annotated_section(d, output))
    return paths


def render_detail(d: Design, output: Path) -> Path:
    p = d.parameters
    fig = plt.figure(figsize=(16, 8), facecolor="#f5f7fa")
    fig.suptitle("PERTACOUSTIC  |  INTEGRATION DETAILS", fontsize=21, color="#182c3e", y=0.96)
    ax = fig.add_axes([0.015, 0.45, 0.48, 0.43], facecolor="#f5f7fa")
    wet = [(part, solid) for part, solid in representation(d, "sectional") if part.module in {"wet_head", "sensor", "pressure_boundary"}]
    draw_3d(ax, wet, section=True)
    ax.set_title("Wet sensing head / conceptual pressure boundary", fontsize=11, color="#243e53")
    for i, (section_label, width, height) in enumerate((("ADC / card carrier", 30, 12), ("Battery / holder", p.cell_diameter_mm, p.cell_diameter_mm))):
        ax2 = fig.add_axes([0.53 + 0.235 * i, 0.45, 0.21, 0.42], facecolor="#f5f7fa")
        ax2.add_patch(Circle((0, 0), p.od_mm / 2, color=STEEL))
        ax2.add_patch(Circle((0, 0), p.bore_mm / 2, color="#f5f7fa"))
        if i == 0:
            carrier_slice = d.by_name("carrier_and_card_saddles").solid.intersect(block(80, 80, 280, 0.5))
            # Project the same CAD carrier slice, rather than inventing a replacement profile.
            faces = mesh_faces(carrier_slice)
            ax2.add_collection(PolyCollection(faces[:, :, [1, 2]], facecolors=[POLYMER], edgecolors="none"))
            ax2.add_patch(Rectangle((-width / 2, -height / 2), width, height, color=BOARD))
            ax2.add_patch(Rectangle((-16, -7), 32, 14, fill=False, ls="--", ec="#17736e", lw=1))
            ax2.add_patch(Circle((0, 13.5), 0.65, color=WIRE))
        else:
            slice_z = p.stations["battery_start"] + 28 + p.cell_length_mm / 2
            for name in ("battery_holder", "cell_1", "battery_contacts_and_leads"):
                part = d.by_name(name)
                sliced = part.solid.intersect(block(80, 80, slice_z, 0.5))
                faces = mesh_faces(sliced)
                ax2.add_collection(PolyCollection(faces[:, :, [1, 2]], facecolors=[part.color], edgecolors="none"))
        ax2.set(xlim=(-25, 25), ylim=(-25, 25), aspect="equal", title=section_label, xlabel="X (mm)", ylabel="Y (mm)")
        ax2.grid(alpha=0.15)
    notes = [
        (0.04, "PRESSURE BOUNDARY", "Fluid reaches the sensor through open guard windows.\nThe bulkhead and sealed feedthrough reserve isolate dry internals.\nExact supplier pinout, seals and retention remain unverified."),
        (0.53, "NOMINAL PACKAGING", f"{p.bore_mm:.2f} mm bore; 34.93 mm ADC clearance envelope.\nTwo Ø{p.cell_diameter_mm:.1f} × {p.cell_length_mm:.1f} mm candidate cells, arranged axially.\nDimensions show conceptual fit, not measured assembly clearance."),
    ]
    for x, title, text in notes:
        fig.text(x, 0.32, title, fontsize=11, color="#17736e", weight="bold")
        fig.text(x, 0.22, text, fontsize=10, color="#536779", linespacing=1.8, va="center")
    path = output / "integration_details.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def render_annotated_section(d: Design, output: Path) -> Path:
    p = d.parameters
    fig, ax = plt.subplots(figsize=(18, 6), facecolor="#f5f7fa")
    ax.set_facecolor("#f5f7fa")
    ax.axvspan(0, 153, color="#dfeef6", zorder=-2)
    ax.axvspan(165, p.stations["cap_end"], color="#e4eeea", zorder=-2)
    ax.axvspan(153, 165, color="#e9cd83", zorder=-2)
    draw_projected(ax, representation(d, "sectional"), np.array([1, 0, 0]), np.array([0, 0, 1]), np.array([0, -1, 0]))
    labels = [(76, 75, "WET\nHTI reference\nopen guard"), (159, -72, "Bulkhead +\nsealed feedthrough\nreserve"),
              (222, 65, "AFE"), (279, -58, "PCM1808\nADC"), (347, 83, "STM32F411\nMCU"),
              (408, -83, "5 V / 3.3 V\nregulation"), (455, 63, "RTC"), (497, -58, "Storage"),
              (536, 83, "Power\nprotection"), (p.stations["electronics_end"] + 10, -88, "Dry service\ncoupler"),
              (p.stations["battery_start"] + 59, 63, "Candidate\ncell 1"),
              (p.stations["battery_start"] + 128, -65, "Candidate\ncell 2"),
              (p.stations["battery_end"] + 15, 65, "Blind upper\nclosure"),
              (p.stations["eye_start"] + 17, -60, "Retrieval\neye")]
    for x, y, label in labels:
        ax.annotate(label, (x, 0), (x, y), ha="center", va="center", fontsize=8, color="#243e53",
                    arrowprops={"arrowstyle": "-", "color": "#778b98", "lw": 0.7})
    length = p.stations["total_length"]
    ax.annotate("", (0, -113), (length, -113), arrowprops={"arrowstyle": "<->", "color": "#17736e"})
    ax.text(length / 2, -123, f"{length:.1f} mm overall • Ø{p.od_mm:.2f} mm maximum • {p.wall_mm:.2f} mm wall / {p.bore_mm:.2f} mm bore", ha="center", fontsize=10, color="#17736e")
    ax.set(xlim=(-20, length + 25), ylim=(-135, 105), aspect="equal")
    ax.set_axis_off()
    fig.suptitle("PERTACOUSTIC  |  ANNOTATED LONGITUDINAL SECTION", fontsize=20, color="#182c3e", y=0.95)
    fig.text(0.06, 0.84, "Geometry-derived section • module envelopes are nominal / estimated • ideal CAD closure is not sealing qualification", color="#536779", fontsize=10)
    fig.text(0.06, 0.08, "Blue: wet sensing region     Gold: conceptual pressure boundary     Green: dry electronics / power", color="#536779", fontsize=10)
    path = output / "annotated_longitudinal_section.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def engineering_scenarios(p: Parameters) -> dict[str, Any]:
    return {
        "structural_screening": structural_screening(p.od_mm, p.wall_mm),
        "pressure_rating": "UNRESOLVED — barrel-only screens do not qualify joints, feedthrough, guard or eye",
        "power_scenarios": [{"load_w": load, "assumed_efficiency": 0.85, "series_cells": 2,
                             "nominal_pack_v": 7.2, "nominal_current_a": load / 0.85 / 7.2,
                             "two_hour_input_wh": load / 0.85 * 2,
                             "all_input_as_heat_w": load / 0.85,
                             "ideal_70c_shell_resistance_budget_to_85c_k_per_w": 15 / (load / 0.85)} for load in (1, 2)],
        "thermal_status": "CONDITIONAL — no credible complete-instrument 2-hour temperature simulation without thermal contacts, heat capacity, loss distribution and external convection",
        "storage_scenarios": [{"sample_rate_hz": fs, "channels_stored": 2, "bytes_per_sample": 4,
                               "duration_s": p.duration_s, "raw_bytes": int(fs * 2 * 4 * p.duration_s),
                               "with_10pct_allowance_bytes": int(fs * 2 * 4 * p.duration_s * 1.1)} for fs in (48000, 96000)],
        "battery_limits": {"candidate": "2 x Saft LSH 20 in series, selection provisional",
                           "upper_cell_temperature_c_from_public_datasheet": 85,
                           "exact_pack_qualification": "NOT VERIFIED", "runtime_at_70c": "NOT VERIFIED"},
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_revision() -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


def generate(output: Path, p: Parameters | None = None, *, figures=True) -> dict[str, Any]:
    output = output.resolve()
    for protected in (ROOT / "results" / "biweekly-5", ROOT / "results" / "compact-casing"):
        if output == protected or protected in output.parents:
            raise ValueError("Refusing to write into historical output directories")
    d = build_design(p)
    verified = verify_design(d)
    output.mkdir(parents=True, exist_ok=True)
    (output / "parameters.json").write_text(json.dumps(asdict(d.parameters), indent=2) + "\n")
    exports = export_all(d, output / "cad")
    image_paths = render_views(d, output / "figures") if figures else []
    scenarios = engineering_scenarios(d.parameters)
    try:
        vtk_version = version("vtk")
    except PackageNotFoundError:
        vtk_version = "Not installed; figures require VTK"
    evidence = {"parameters": asdict(d.parameters), "geometry": verified, "step_exports": exports,
                "figure_outputs": [path.name for path in image_paths],
                "engineering_scenarios": scenarios, "source_sha256": sha256(Path(__file__)),
                "source_files_sha256": {name: sha256(ROOT / name) for name in (
                    "cosmo/integrated_downhole.py", "cosmo/integrated_report.py",
                    "cosmo/compact_casing.py", "cosmo/material_library.json")},
                "implementation_baseline": BASELINE, "actual_execution_start": EXECUTION_START,
                "generation_head": git_revision(), "generation_state": "Local source and artifact generation; immutable result identified in Git handoff",
                "contract": {"type": "Human-approved prompt-defined execution contract under software-workflow 15.8",
                             "primary_request_sha256": "59ed10afde268b9865bca4e9fba620317b0e9eb4e2c624ffa4236516f8e3dab5",
                             "direct_execution_update_sha256": "7f44bd9aaf4d7dbe95cb949d62bf37dadbb66ea4fb6388725159d7b27f6cb4f2",
                             "latest_authorization": "Updated Execution Authorization — PertAcoustic TRL 5; human approval 'yes' of scoped governance amendment, 2026-11-11",
                             "preflight": "Scope, baseline, exclusions, acceptance/verification, preservation and Git permissions checked against complete supplied instructions; no unresolved material upstream decision for conceptual geometry"},
                "environment": {"python": platform.python_version(), "cadquery": cq.__version__, "numpy": np.__version__,
                                "matplotlib": matplotlib.__version__, "vtk": vtk_version}, "sources": SOURCES,
                "terminal_state": "Review Required; independent acceptance pending"}
    (output / "verification.json").write_text(json.dumps(evidence, indent=2) + "\n")
    (output / "design_report.md").write_text(design_report(evidence, d.components))
    manifest_paths = [output / "parameters.json", output / "verification.json", output / "design_report.md"]
    manifest_paths += sorted((output / "cad").glob("*.step")) + image_paths
    manifest = {"files": [{"path": path.relative_to(output).as_posix(), "bytes": path.stat().st_size,
                            "sha256": sha256(path)} for path in manifest_paths]}
    (output / "artifact_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": verified["status"], "length_mm": verified["overall_length_mm"],
                      "od_mm": verified["maximum_od_mm"], "parts": verified["part_count"],
                      "step_exports": len(exports), "figures": len(image_paths), "output": str(output)}, indent=2))
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--parameters", type=Path, help="JSON object containing Parameters fields")
    parser.add_argument("--no-figures", action="store_true")
    args = parser.parse_args()
    params = Parameters(**json.loads(args.parameters.read_text())) if args.parameters else Parameters()
    generate(args.output, params, figures=not args.no_figures)


if __name__ == "__main__":
    main()
