#!/usr/bin/env python3
"""Generates the animated SVGs used by the profile README.

Run: python assets/build_assets.py
Every figure in the output is counted in the repository it names.
SMIL animation only (CSS keyframes are unreliable inside GitHub's <img> context).
"""

from __future__ import annotations

import math
import pathlib
import random
import xml.etree.ElementTree as ET

OUT = pathlib.Path(__file__).parent

BG = "#0b0e14"
PANEL = "#0e121a"
LINE = "#1b2230"
GRID = "#141a24"
TEXT = "#e6edf3"
MUTED = "#8b949e"
DIM = "#5c6570"
A = "#38bdf8"  # data / flow
B = "#a78bfa"  # AI / research

MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"


def head(w: int, h: int, title: str, desc: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="t d">
<title id="t">{title}</title><desc id="d">{desc}</desc>
<defs>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
  <path d="M40 0H0V40" fill="none" stroke="{GRID}" stroke-width="1"/>
</pattern>
<radialGradient id="vig" cx="50%" cy="45%" r="70%">
  <stop offset="0%" stop-color="#121826" stop-opacity="0.9"/>
  <stop offset="100%" stop-color="{BG}" stop-opacity="1"/>
</radialGradient>
<filter id="glow" x="-80%" y="-80%" width="260%" height="260%">
  <feGaussianBlur stdDeviation="6" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
</defs>
<rect width="{w}" height="{h}" fill="{BG}"/>
<rect width="{w}" height="{h}" fill="url(#grid)" opacity="0.55"/>
<rect width="{w}" height="{h}" fill="url(#vig)" opacity="0.75"/>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" fill="none" stroke="{LINE}"/>
"""


def label(x, y, s, size=11, fill=MUTED, anchor="start", family=MONO, weight="400", ls="0.12em", op=1.0):
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" font-weight="{weight}" letter-spacing="{ls}" opacity="{op}">{s}</text>\n'
    )


def kicker(x, y, s):
    return label(x, y, s, size=10, fill=DIM, ls="0.22em")


def edge(x1, y1, x2, y2, color=LINE, width=1.0, op=0.8, dash=None, dur=None, offset=0.0):
    """Thin edge; with dash+dur it becomes a slow travelling stroke."""
    s = f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}" opacity="{op}"'
    if dash:
        s += f' stroke-dasharray="{dash}">'
        s += (
            f'<animate attributeName="stroke-dashoffset" values="{dash.split()[0] * 1};0" '
            f'dur="{dur}s" begin="-{offset}s" repeatCount="indefinite"/></line>\n'
        )
        return s
    return s + "/>\n"


def particle(x1, y1, x2, y2, color=A, r=2.1, dur=5.0, offset=0.0, op=0.95):
    return (
        f'<circle r="{r}" fill="{color}" opacity="{op}">'
        f'<animateMotion path="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" dur="{dur}s" '
        f'begin="-{offset:.2f}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;{op};{op};0" dur="{dur}s" begin="-{offset:.2f}s" repeatCount="indefinite"/>'
        "</circle>\n"
    )


def node(x, y, r, color, dur=4.6, offset=0.0, halo=True, core=True):
    s = ""
    if halo:
        s += (
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" opacity="0.10">'
            f'<animate attributeName="r" values="{r};{r * 1.55:.1f};{r}" dur="{dur}s" begin="-{offset:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0.07;0.20;0.07" dur="{dur}s" begin="-{offset:.2f}s" repeatCount="indefinite"/>'
            "</circle>\n"
        )
    if core:
        s += f'<circle cx="{x}" cy="{y}" r="{r * 0.46:.1f}" fill="{PANEL}" stroke="{color}" stroke-width="1.4"/>\n'
        s += (
            f'<circle cx="{x}" cy="{y}" r="{max(1.8, r * 0.17):.1f}" fill="{color}">'
            f'<animate attributeName="opacity" values="0.45;1;0.45" dur="{dur}s" begin="-{offset:.2f}s" repeatCount="indefinite"/>'
            "</circle>\n"
        )
    return s


def panel(x, y, w, h, stroke=LINE, fill=PANEL, rx=3, op=1.0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1" opacity="{op}"/>\n'


def write(name: str, body: str) -> None:
    path = OUT / name
    path.write_text(body + "</svg>\n", encoding="utf-8")
    ET.parse(path)  # fails loudly on malformed output
    print(f"{name:26s} {path.stat().st_size / 1024:6.1f} KB")


# ---------------------------------------------------------------- hero graph

def hero() -> None:
    W, H = 1000, 440
    cx, cy = 500, 224
    s = head(W, H, "Arjun Patil system map",
             "Knowledge graph with ARJUN at the centre, connected to AI, LLM, RAG, automation, "
             "ML, data, systems, MLOps and research clusters.")
    s += kicker(28, 34, "SYSTEM MAP")
    s += label(W - 28, 34, "arjun05-tf", 10, DIM, anchor="end", ls="0.18em")

    nodes = [
        ("AI", 296, 108, B, 1.7),
        ("LLM", 164, 186, B, 1.5),
        ("RAG", 208, 310, B, 1.6),
        ("AUTOMATION", 392, 372, A, 1.6),
        ("ML", 618, 372, A, 1.3),
        ("DATA", 804, 308, A, 1.5),
        ("SYSTEMS", 842, 178, A, 1.2),
        ("MLOPS", 706, 96, A, 1.0),
        ("RESEARCH", 486, 70, B, 1.1),
    ]
    ring = [(i, (i + 1) % len(nodes)) for i in range(len(nodes))]

    # satellite density: unlabelled micro-nodes around the denser clusters
    sats = {0: 3, 2: 5, 3: 4, 5: 4, 6: 2, 8: 2}
    for i, count in sats.items():
        name, nx, ny, col, _ = nodes[i]
        for k in range(count):
            ang = math.radians(28 + k * (360 / (count + 1)) + i * 23)
            d = 30 + (k % 3) * 9
            sx, sy = nx + math.cos(ang) * d, ny + math.sin(ang) * d * 0.72
            s += edge(nx, ny, sx, sy, LINE, 0.7, 0.7)
            s += node(sx, sy, 5.0, col, dur=5.4 + k * 0.7, offset=i + k * 0.9, halo=False)

    # ring edges between neighbouring clusters
    for i, j in ring:
        _, x1, y1, c1, _ = nodes[i]
        _, x2, y2, _, _ = nodes[j]
        s += edge(x1, y1, x2, y2, LINE, 0.9, 0.85, dash="4 7", dur=9, offset=i * 1.4)

    # spokes to the centre, weighted by how much of the portfolio sits on them
    for i, (name, x, y, col, weight) in enumerate(nodes):
        s += edge(cx, cy, x, y, col, weight * 0.55, 0.26)
        s += particle(cx, cy, x, y, col, r=1.9 + weight * 0.35, dur=5.6 + i * 0.63, offset=i * 1.31)
        s += particle(x, y, cx, cy, col, r=1.6, dur=7.2 + i * 0.41, offset=3 + i * 0.97, op=0.6)

    for i, (name, x, y, col, weight) in enumerate(nodes):
        s += node(x, y, 16 + weight * 4, col, dur=4.2 + i * 0.37, offset=i * 0.8)
        dy = -30 if y < cy else 34
        s += label(x, y + dy, name, 12, TEXT, anchor="middle", weight="600", ls="0.16em")

    # centre anchor
    s += f'<circle cx="{cx}" cy="{cy}" r="58" fill="{B}" opacity="0.06"><animate attributeName="r" values="56;70;56" dur="7s" repeatCount="indefinite"/></circle>\n'
    s += f'<circle cx="{cx}" cy="{cy}" r="40" fill="none" stroke="{LINE}" stroke-width="1" stroke-dasharray="2 6"><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="64s" repeatCount="indefinite"/></circle>\n'
    s += f'<circle cx="{cx}" cy="{cy}" r="31" fill="{PANEL}" stroke="{A}" stroke-width="1.6" filter="url(#glow)" opacity="0.98"/>\n'
    s += label(cx, cy + 4, "ARJUN", 13, TEXT, anchor="middle", weight="700", ls="0.2em")
    write("hero-graph.svg", s)


# ----------------------------------------------------------- knowledge graph

CLUSTERS = [
    ("AI / LLM", 182, 132, B, ["Claude", "OpenAI", "structured output", "prompt versioning", "schema repair"]),
    ("RETRIEVAL", 168, 392, B, ["multilingual-e5", "Qdrant", "cross-encoder", "grounding", "abstention"]),
    ("AUTOMATION", 500, 118, A, ["n8n", "HMAC webhooks", "idempotency", "CRM sync", "retry policy"]),
    ("STREAMING", 836, 150, A, ["protobuf", "Redpanda", "Flink", "event time", "watermarks"]),
    ("ML", 500, 470, A, ["LightGBM", "XGBoost", "SHAP", "conformal", "PSI drift"]),
    ("SYSTEMS", 846, 420, A, ["FastAPI", "PostgreSQL", "Pydantic", "Docker", "Actions"]),
    ("RESEARCH", 352, 288, B, ["activations", "compression", "layer sweep", "baselines"]),
]
CLUSTER_LINKS = [(0, 1), (0, 2), (0, 6), (1, 6), (2, 5), (2, 3), (3, 5), (4, 5), (4, 1), (3, 4)]


def knowledge_graph() -> None:
    W, H = 1000, 600
    s = head(W, H, "Technical knowledge graph",
             "Seven clusters (AI/LLM, retrieval, automation, streaming, ML, systems and research), "
             "each expanded into the tools used in the repositories.")
    s += kicker(28, 34, "KNOWLEDGE GRAPH")
    s += label(W - 28, 34, "tools present in the repositories", 10, DIM, anchor="end", ls="0.12em")

    for n, (i, j) in enumerate(CLUSTER_LINKS):
        _, x1, y1, c1, _ = CLUSTERS[i]
        _, x2, y2, _, _ = CLUSTERS[j]
        s += edge(x1, y1, x2, y2, LINE, 1.0, 0.9)
        s += particle(x1, y1, x2, y2, c1, r=1.8, dur=8.5 + n * 0.7, offset=n * 1.7, op=0.75)

    # Leaves start on an ellipse around their hub, then a few relaxation passes
    # push overlapping labels apart. Hand-placing 32 labels is not worth it.
    fixed = [(cxx, cyy, len(name) * 9 + 46, 46) for name, cxx, cyy, _, _ in CLUSTERS]
    leaves = []
    for ci, (name, cxx, cyy, col, items) in enumerate(CLUSTERS):
        for k, leaf in enumerate(items):
            ang = math.radians(-100 + k * (360 / len(items)) + ci * 29)
            lx = cxx + math.cos(ang) * 124
            ly = cyy + math.sin(ang) * 92
            leaves.append([lx, ly, len(leaf) * 6.0 + 26, 30, ci, leaf, col, k])

    def overlap(ax, ay, aw, ah, bx, by, bw, bh):
        return (abs(ax - bx) < (aw + bw) / 2) and (abs(ay - by) < (ah + bh) / 2)

    for _ in range(260):
        for i, a in enumerate(leaves):
            for b in fixed + [l[:4] for j, l in enumerate(leaves) if j != i]:
                if not overlap(a[0], a[1], a[2], a[3], b[0], b[1], b[2], b[3]):
                    continue
                dx, dy = a[0] - b[0], a[1] - b[1]
                d = math.hypot(dx, dy) or 0.01
                a[0] += dx / d * 3.0
                a[1] += dy / d * 2.2
            hx, hy = CLUSTERS[a[4]][1], CLUSTERS[a[4]][2]
            dx, dy = a[0] - hx, a[1] - hy
            d = math.hypot(dx, dy) or 0.01
            if d > 165:  # keep the leaf visibly attached to its own hub
                a[0], a[1] = hx + dx / d * 165, hy + dy / d * 165
            a[0] = min(max(a[0], a[2] / 2 + 14), W - a[2] / 2 - 14)
            a[1] = min(max(a[1], 58), H - 30)

    for lx, ly, _, _, ci, leaf, col, k in leaves:
        cxx, cyy = CLUSTERS[ci][1], CLUSTERS[ci][2]
        s += edge(cxx, cyy, lx, ly, col, 0.8, 0.22)
        s += particle(cxx, cyy, lx, ly, col, r=1.4, dur=6 + k * 0.9 + ci * 0.3, offset=ci * 1.1 + k * 1.3, op=0.5)
        s += node(lx, ly, 6.4, col, dur=5 + k * 0.6, offset=ci + k * 0.7, halo=False)
        s += label(lx, ly + 18, leaf, 9.5, MUTED, anchor="middle", ls="0.06em")

    for ci, (name, cxx, cyy, col, _) in enumerate(CLUSTERS):
        s += node(cxx, cyy, 22, col, dur=5.2 + ci * 0.4, offset=ci * 0.9)
        s += f'<rect x="{cxx - (len(name) * 7 + 18) / 2:.1f}" y="{cyy - 9}" width="{len(name) * 7 + 18}" height="18" rx="2" fill="{BG}" opacity="0.82"/>\n'
        s += label(cxx, cyy + 4, name, 10.5, TEXT, anchor="middle", weight="700", ls="0.14em")

    write("knowledge-graph.svg", s)


# ---------------------------------------------------------- project ecosystem

def ecosystem() -> None:
    W, H = 1000, 520
    s = head(W, H, "Project ecosystem",
             "Domains above, three flagship projects in the middle, shared engineering substrate below, "
             "with two supporting projects on the research side.")
    s += kicker(28, 34, "PROJECT ECOSYSTEM")

    domains = [("AI / AUTOMATION", 210), ("RETRIEVAL", 500), ("STREAMING DATA", 790)]
    flags = [
        ("SIGNALOPS AI", "42 endpoints · 7 workflows · 228 tests", 170, A),
        ("GERMAN LAW RAG", "113 eval questions · rerank + abstention", 500, B),
        ("BVG DELAY STREAM", "protobuf · Flink event time · Timescale", 830, A),
    ]
    sub = ["FastAPI", "PostgreSQL", "Docker Compose", "evaluation harness", "GitHub Actions"]

    for i, (name, x) in enumerate(domains):
        s += panel(x - 118, 66, 236, 34, LINE, "#101521")
        s += label(x, 88, name, 10.5, TEXT, anchor="middle", weight="600", ls="0.18em")

    for i, (name, meta, x, col) in enumerate(flags):
        s += panel(x - 146, 186, 292, 86, col, PANEL)
        s += f'<rect x="{x - 146}" y="186" width="292" height="2" fill="{col}" opacity="0.5"><animate attributeName="opacity" values="0.25;0.8;0.25" dur="{5 + i}s" repeatCount="indefinite"/></rect>\n'
        s += label(x - 128, 222, name, 13, TEXT, weight="700", ls="0.14em")
        s += label(x - 128, 246, meta, 9.5, MUTED, ls="0.04em")
        s += node(x + 128, 206, 7, col, dur=4 + i * 0.6, offset=i, halo=False)
        # domain -> project
        dx = domains[i][1]
        s += edge(dx, 100, x, 186, col, 1.0, 0.3)
        s += particle(dx, 100, x, 186, col, dur=4.4 + i * 0.5, offset=i * 1.3)
        # project -> substrate
        s += edge(x, 272, 500, 384, col, 1.0, 0.25)
        s += particle(x, 272, 500, 384, col, r=1.8, dur=5.2 + i * 0.6, offset=1 + i * 1.7, op=0.7)

    # cross links between flagships: shared patterns, not shared code
    s += edge(316, 229, 354, 229, DIM, 1.2, 0.8, dash="3 5", dur=6)
    s += edge(646, 229, 684, 229, DIM, 1.2, 0.8, dash="3 5", dur=6, offset=2)

    s += panel(240, 384, 520, 40, LINE, "#101521")
    s += label(500, 409, "  ·  ".join(sub), 10, MUTED, anchor="middle", ls="0.1em")

    secondary = [("BERLINRENTML", "LightGBM · conformal · live demo", 196, 470, A),
                 ("CROSS-MODEL LATENT MEMORY", "research prototype · phase 1", 720, 470, B)]
    for i, (name, meta, x, y, col) in enumerate(secondary):
        s += node(x - 150, y - 4, 8, col, dur=5.5, offset=i * 2, halo=False)
        s += label(x - 136, y, name, 10.5, TEXT, weight="600", ls="0.12em")
        s += label(x - 136, y + 16, meta, 9, DIM, ls="0.04em")
        s += edge(x - 150, y - 12, 500, 424, col, 0.9, 0.18)
        s += particle(x - 150, y - 12, 500, 424, col, r=1.5, dur=7 + i, offset=i * 2.4, op=0.55)
    write("project-ecosystem.svg", s)


# ------------------------------------------- SignalOps: lead intelligence graph
# Radial evidence graph on a 12 s cycle: evidence flows inward, the ICP arc
# fills, then the outreach / grounding / approval / CRM states light in order.

CYCLE = 12.0


def keyed(attr: str, values: str, keytimes: str, dur: float = CYCLE) -> str:
    return (f'<animate attributeName="{attr}" values="{values}" keyTimes="{keytimes}" '
            f'dur="{dur}s" repeatCount="indefinite"/>')


def signalops() -> None:
    W, H = 1000, 540
    cx, cy = 300, 288
    s = head(W, H, "SignalOps AI lead intelligence graph",
             "A company node at the centre of four evidence sources (security posture, compliance, "
             "procurement, maturity). Evidence flows inward, an ICP fit arc fills, and the outreach, "
             "grounding, human approval and CRM states activate in sequence.")
    s += kicker(28, 34, "SIGNALOPS AI · LEAD INTELLIGENCE")
    s += label(W - 28, 34, "evidence in, qualification out", 9.5, DIM, anchor="end", ls="0.1em")

    rng = random.Random(11)
    # background: other leads in the book, dim and out of focus
    for i in range(26):
        ang = rng.uniform(0, math.tau)
        d = rng.uniform(190, 330)
        bx, by = cx + math.cos(ang) * d * 1.25, cy + math.sin(ang) * d * 0.62
        if not (40 < bx < 540 and 70 < by < H - 40):
            continue
        r = rng.uniform(1.6, 3.4)
        s += f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{r:.1f}" fill="{MUTED}" opacity="{rng.uniform(0.10, 0.3):.2f}"/>\n'

    for i, r in enumerate((76, 122, 172, 226)):
        s += (f'<ellipse cx="{cx}" cy="{cy}" rx="{r * 1.22:.0f}" ry="{r * 0.78:.0f}" fill="none" '
              f'stroke="#27324a" stroke-width="1" stroke-dasharray="2 8" opacity="{1.0 - i * 0.16:.2f}">'
              f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" '
              f'to="{360 if i % 2 else -360} {cx} {cy}" dur="{90 + i * 40}s" repeatCount="indefinite"/></ellipse>\n')

    # provenance rails, same encoding the app uses: solid observed, dashed inferred, dotted gap
    prov = [("none", "observed"), ("4 3", "inferred"), ("1 4", "recorded gap")]
    sources = [
        ("COMPLIANCE", 164, 226, "end", 0, -26),
        ("PROCUREMENT", 268, 138, "middle", 0, -26),
        ("SECURITY POSTURE", 428, 186, "middle", 0, -26),
        ("MATURITY", 168, 368, "end", -24, 4),
    ]
    for i, (name, sx, sy, anchor, lx, ly) in enumerate(sources):
        for k in range(3):
            ang = math.atan2(sy - cy, sx - cx) + (k - 1) * 0.42
            ex, ey = sx + math.cos(ang) * 58, sy + math.sin(ang) * 40
            dash, _ = prov[k]
            da = "" if dash == "none" else f' stroke-dasharray="{dash}"'
            s += (f'<line x1="{sx}" y1="{sy}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{A}" '
                  f'stroke-width="0.8" opacity="0.3"{da}/>\n')
            s += f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="2.6" fill="{PANEL}" stroke="{A}" stroke-width="1" opacity="0.65"/>\n'
            s += particle(ex, ey, sx, sy, A, r=1.5, dur=4.5 + k * 1.3 + i * 0.4, offset=i * 1.1 + k * 1.7, op=0.5)

        s += edge(sx, sy, cx, cy, A, 1.2, 0.3)
        for k in range(2):
            s += particle(sx, sy, cx, cy, A, r=2.2, dur=5 + i * 0.9 + k * 2.1, offset=i * 1.6 + k * 2.4)
        s += node(sx, sy, 15, A, dur=4.6 + i * 0.5, offset=i * 1.2)
        s += label(sx + lx, sy + ly, name, 10, TEXT, anchor=anchor, weight="600", ls="0.12em")

    # pain hypotheses: rule-derived, so they sit on their own branch under the company
    s += edge(cx, cy, cx - 10, 432, B, 1.1, 0.3)
    for k in range(3):
        px = cx - 74 + k * 68
        s += edge(cx - 10, 432, px, 466, B, 0.8, 0.25)
        s += (f'<circle cx="{px}" cy="466" r="5" fill="{PANEL}" stroke="{B}" stroke-width="1.2">'
              + keyed("opacity", "0.35;0.35;1;1;0.35", f"0;{0.3 + k * 0.04};{0.4 + k * 0.04};0.86;1") + "</circle>\n")
    s += label(cx - 10, 494, "PAIN HYPOTHESES", 9.5, MUTED, anchor="middle", ls="0.14em")

    # the lead under evaluation
    s += f'<circle cx="{cx}" cy="{cy}" r="46" fill="{B}" opacity="0.05"><animate attributeName="r" values="42;56;42" dur="8s" repeatCount="indefinite"/></circle>\n'
    s += f'<circle cx="{cx}" cy="{cy}" r="27" fill="{PANEL}" stroke="{A}" stroke-width="1.8" filter="url(#glow)"/>\n'
    s += label(cx, cy + 4, "COMPANY", 10, TEXT, anchor="middle", weight="700", ls="0.12em")

    # ICP fit arc: sweeps as evidence lands, bands labelled the way the app bands them
    ax, ay, ar = 660, 258, 54
    circ = 2 * math.pi * ar
    s += edge(cx + 28, cy - 6, ax - ar - 6, ay + 10, A, 1.2, 0.3)
    s += particle(cx + 28, cy - 6, ax - ar - 6, ay + 10, A, r=2.2, dur=4.4, offset=0.4)
    s += f'<circle cx="{ax}" cy="{ay}" r="{ar}" fill="none" stroke="{LINE}" stroke-width="6"/>\n'
    s += (f'<circle cx="{ax}" cy="{ay}" r="{ar}" fill="none" stroke="{A}" stroke-width="6" '
          f'stroke-linecap="round" stroke-dasharray="{circ:.1f}" transform="rotate(-90 {ax} {ay})" opacity="0.9">'
          + keyed("stroke-dashoffset",
                  f"{circ:.1f};{circ * 0.26:.1f};{circ * 0.26:.1f};{circ:.1f}", "0;0.34;0.9;1") + "</circle>\n")
    for k, band in enumerate(("disqualified", "nurture", "qualified", "high priority")):
        a0 = math.radians(-90 + k * 90)
        s += (f'<line x1="{ax + math.cos(a0) * (ar - 9):.1f}" y1="{ay + math.sin(a0) * (ar - 9):.1f}" '
              f'x2="{ax + math.cos(a0) * (ar + 9):.1f}" y2="{ay + math.sin(a0) * (ar + 9):.1f}" '
              f'stroke="{BG}" stroke-width="3"/>\n')
    s += label(ax, ay - 2, "ICP FIT", 10, TEXT, anchor="middle", weight="700", ls="0.14em")
    s += label(ax, ay + 14, "rules + model", 8.5, DIM, anchor="middle", ls="0.06em")
    s += label(ax, ay + ar + 26, "four bands, model never sets the total", 8.5, DIM, anchor="middle", ls="0.06em")

    # state column: each state lights only after the one above it
    rows = [("OUTREACH DRAFT", "German first touch", 0.40),
            ("GROUNDING CHECK", "claim resolved to evidence id", 0.54),
            ("HUMAN APPROVAL", "nothing sent without a click", 0.68),
            ("CRM SYNC", "follow-up scheduled", 0.82)]
    rx, ry = 790, 132
    s += f'<line x1="{rx - 18}" y1="{ry}" x2="{rx - 18}" y2="{ry + 3 * 72}" stroke="{LINE}" stroke-width="1"/>\n'
    s += edge(ax + ar + 6, ay - 20, rx - 18, ry + 6, A, 1.1, 0.3)
    for i, (name, meta, t) in enumerate(rows):
        y = ry + i * 72
        s += (f'<circle cx="{rx - 18}" cy="{y}" r="5.5" fill="{PANEL}" stroke="{A}" stroke-width="1.4">'
              + keyed("opacity", f"0.3;0.3;1;1;0.3", f"0;{t - 0.03};{t};0.93;1") + "</circle>\n")
        s += (f'<circle cx="{rx - 18}" cy="{y}" r="5.5" fill="none" stroke="{A}" stroke-width="1.2">'
              + keyed("r", f"5.5;5.5;20;20", f"0;{t};{t + 0.06};1")
              + keyed("opacity", f"0;0.8;0;0", f"0;{t};{t + 0.06};1") + "</circle>\n")
        s += label(rx, y + 4, name, 10.5, TEXT, weight="700", ls="0.12em")
        s += label(rx, y + 20, meta, 8.5, MUTED, ls="0.04em")
        if name == "GROUNDING CHECK":  # per-claim verification ticks
            for k in range(3):
                tx = rx + 2 + k * 16
                s += (f'<path d="M{tx} {y + 32} l3 4 l6 -8" fill="none" stroke="{A}" stroke-width="1.4" opacity="0.2">'
                      + keyed("opacity", f"0.15;0.15;1;1;0.15",
                              f"0;{t + 0.01 + k * 0.012};{t + 0.03 + k * 0.012};0.93;1") + "</path>\n")

    # run strip: the dashboard's last executions, failures marked, newest on the right
    sx0, sy0 = 772, 448
    rng2 = random.Random(4)
    s += label(sx0, sy0 - 16, "RUN STRIP", 9.5, TEXT, weight="700", ls="0.16em")
    s += label(sx0, sy0 + 44, "last executions, failures marked", 8.5, DIM, ls="0.06em")
    for k in range(34):
        h = rng2.uniform(6, 26)
        fail = k in (9, 25)
        s += (f'<rect x="{sx0 + k * 5.6:.1f}" y="{sy0 + 26 - h:.1f}" width="3.4" height="{h:.1f}" '
              f'fill="{"#f0a500" if fail else A}" opacity="{0.8 if fail else 0.35}"/>\n')
    s += (f'<rect x="{sx0 + 34 * 5.6:.1f}" y="{sy0 + 8}" width="3.4" height="18" fill="{A}">'
          + keyed("opacity", "0;0;1;1;0.2", "0;0.8;0.84;0.96;1") + "</rect>\n")

    s += label(28, H - 26, "rails: solid observed  ·  dashed inferred  ·  dotted recorded gap", 8.5, DIM, ls="0.08em")
    write("signalops-intelligence.svg", s)


# ------------------------------------------ German law RAG: semantic field map
# 10 s retrieval cycle: query wave crosses the corpus, candidates light by
# distance, the rerank column physically reorders, one paragraph locks in.

RAG_CYCLE = 10.0


def legal_field() -> None:
    W, H = 1000, 520
    s = head(W, H, "German law RAG retrieval map",
             "A field of 80 Absatz-level law chunks. A query wave crosses the corpus, candidate "
             "paragraphs light up, a cross-encoder column reorders them, and § 4 ArbZG locks to the "
             "cited answer.")
    s += kicker(28, 34, "GERMAN LAW RAG · SEMANTIC FIELD")
    s += label(W - 28, 34, "corpus: 80 Absatz chunks, ArbZG", 9.5, DIM, anchor="end", ls="0.1em")

    qx, qy = 300, 268
    rng = random.Random(5)
    pts = []
    while len(pts) < 80:  # one node per chunk in the real corpus
        x, y = rng.uniform(62, 548), rng.uniform(86, 464)
        if all((x - px) ** 2 + (y - py) ** 2 > 820 for px, py, *_ in pts):
            pts.append((x, y, math.hypot(x - qx, y - qy)))

    pts.sort(key=lambda p: p[2])
    # candidates are spread through the field, not the six nodes nearest the query:
    # dense retrieval pulls from the whole corpus, which is the point of the figure
    cand = [1, 6, 13, 22, 34, 47]
    marks = ["§ 4", "§ 3", "§ 5", "§ 7", "§ 9", "§ 11"]

    s += panel(50, 76, 512, 400, LINE, "#0c1018")
    s += f'<clipPath id="field"><rect x="50" y="76" width="512" height="400"/></clipPath>\n'
    s += label(60, 466, "semantic space", 8.5, DIM, ls="0.18em")

    # the query itself, and the search wave it emits
    s += panel(60, 48, 232, 22, LINE, PANEL)
    s += label(70, 63, "QUERY  Ruhepausen? (DE / EN)", 9, TEXT, ls="0.04em")
    s += edge(176, 70, qx, qy, B, 1.0, 0.3)
    s += '<g clip-path="url(#field)">\n'
    for k in range(2):
        s += (f'<circle cx="{qx}" cy="{qy}" r="0" fill="none" stroke="{B}" stroke-width="1.2">'
              + keyed("r", "0;330;330", f"0;0.4;1", RAG_CYCLE)
              + keyed("opacity", "0.55;0;0", "0;0.4;1", RAG_CYCLE) + "</circle>\n")
    s += node(qx, qy, 9, B, dur=3.2, halo=True)

    for i, (x, y, d) in enumerate(pts):
        t = min(0.38, d / 330 * 0.4)
        if i in cand:
            m = cand.index(i)
            r = 3.8
            s += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{B}" opacity="0.25">'
                  + keyed("opacity", f"0.55;0.55;1;1;0.55", f"0;{t};{t + 0.04};0.9;1", RAG_CYCLE)
                  + keyed("r", f"{r};{r};{r + 2.6};{r + 2.6};{r}", f"0;{t};{t + 0.04};0.9;1", RAG_CYCLE) + "</circle>\n")
            s += (f'<text x="{x:.1f}" y="{y - 11:.1f}" font-family="{MONO}" font-size="9" fill="{TEXT}" '
                  f'text-anchor="middle" opacity="0.6">{marks[m]}'
                  + keyed("opacity", "0.6;0.6;1;1;0.6", f"0;{t};{t + 0.04};0.9;1", RAG_CYCLE) + "</text>\n")
            s += (f'<line x1="{x:.1f}" y1="{y:.1f}" x2="600" y2="{150 + m * 42}" stroke="{B}" '
                  f'stroke-width="0.9" opacity="0.14">'
                  + keyed("opacity", f"0.14;0.14;0.4;0.4;0.14", f"0;{t + 0.04};{t + 0.1};0.9;1", RAG_CYCLE) + "</line>\n")
        else:
            # non-candidates recede while the wave is live: relevance filtering
            r = rng.uniform(2.0, 3.4)
            s += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{MUTED}" opacity="0.45">'
                  + keyed("opacity", "0.45;0.45;0.16;0.16;0.45", f"0;{t};{t + 0.08};0.9;1", RAG_CYCLE) + "</circle>\n")
    s += "</g>\n"

    # rerank column: rows physically swap into their reranked order
    s += label(612, 108, "CROSS-ENCODER RERANK", 9.5, TEXT, weight="700", ls="0.14em")
    s += label(612, 124, "top-20 candidates reordered", 8.5, DIM, ls="0.04em")
    order = [2, 0, 3, 1, 4, 5]  # dense rank -> reranked slot
    for i in range(6):
        y = 150 + i * 42
        dy = (order.index(i) - i) * 42
        s += (f'<g opacity="0.9">'
              f'<animateTransform attributeName="transform" type="translate" '
              f'values="0 0;0 0;0 {dy};0 {dy};0 0" keyTimes="0;0.5;0.62;0.92;1" '
              f'dur="{RAG_CYCLE}s" repeatCount="indefinite"/>\n')
        s += panel(600, y - 14, 196, 30, LINE, PANEL)
        if i == 0:  # the paragraph that ends up on top after reranking
            s += (f'<rect x="600" y="{y - 14}" width="196" height="30" rx="3" fill="none" stroke="{B}" '
                  f'stroke-width="1.4" opacity="0">'
                  + keyed("opacity", "0;0;0.95;0.95;0", "0;0.62;0.68;0.95;1", RAG_CYCLE) + "</rect>\n")
        s += label(612, y + 5, marks[i] + "  ArbZG", 10, TEXT, weight="600", ls="0.08em")
        bar = 28 + (5 - i) * 12
        s += f'<rect x="700" y="{y - 4}" width="{bar}" height="8" fill="{B}" opacity="0.35" rx="1"/>\n'
        s += "</g>\n"

    # the winning paragraph stays attached to the answer as a citation
    s += panel(826, 198, 146, 108, LINE, PANEL)
    s += label(840, 224, "ANSWER", 10.5, TEXT, weight="700", ls="0.16em")
    s += label(840, 244, "grounded in the", 8.5, MUTED, ls="0.04em")
    s += label(840, 258, "retrieved text, or", 8.5, MUTED, ls="0.04em")
    s += label(840, 272, "refusal", 8.5, MUTED, ls="0.04em")
    s += f'<rect x="840" y="282" width="78" height="18" rx="2" fill="{B}" opacity="0.14"/>\n'
    s += label(848, 295, "§ 4 ArbZG", 9, TEXT, weight="600", ls="0.04em")
    s += (f'<line x1="796" y1="192" x2="826" y2="252" stroke="{B}" stroke-width="1.2" opacity="0">'
          + keyed("opacity", "0;0;0.9;0.9;0", "0;0.64;0.72;0.95;1", RAG_CYCLE) + "</line>\n")
    s += (f'<circle r="2.4" fill="{B}" opacity="0">'
          f'<animateMotion path="M796 192 L826 252" dur="{RAG_CYCLE}s" repeatCount="indefinite" '
          f'keyTimes="0;0.66;0.74;1" keyPoints="0;0;1;1" calcMode="linear"/>'
          + keyed("opacity", "0;0;1;1;0", "0;0.66;0.74;0.95;1", RAG_CYCLE) + "</circle>\n")
    s += label(28, H - 22, "wave: retrieval  ·  column: ranking  ·  chip: citation that stays attached",
               8.5, DIM, ls="0.08em")
    write("legal-retrieval.svg", s)


# -------------------------------------------- BVG: live transit telemetry view

def poly_path(pts: list[tuple[float, float]]) -> str:
    return "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)


def bvg_telemetry() -> None:
    W, H = 1000, 560
    s = head(W, H, "BVG delay stream telemetry",
             "Four abstract transit lines with trains in motion, stop events dropping onto an "
             "event-time axis, one event diverted into the late side output, and a rolling window "
             "sweeping a schematic punctuality series.")
    s += kicker(28, 34, "BVG DELAY STREAM · LIVE TELEMETRY")
    s += label(W - 28, 34, "event time, not arrival time", 9.5, DIM, anchor="end", ls="0.1em")

    lines = [
        ("U5", [(96, 118), (330, 110), (600, 124), (940, 112)], A),
        ("S7", [(96, 166), (288, 180), (620, 160), (940, 174)], A),
        ("U2", [(96, 214), (360, 228), (700, 210), (940, 222)], B),
        ("M10", [(96, 262), (420, 250), (780, 266), (940, 254)], A),
    ]
    axis_y, late_y = 348, 392

    for li, (name, pts, col) in enumerate(lines):
        path = poly_path(pts)
        s += f'<path d="{path}" fill="none" stroke="{col}" stroke-width="2" opacity="0.22"/>\n'
        s += label(78, pts[0][1] + 4, name, 10, TEXT, anchor="end", weight="700", ls="0.1em")

        stations = [(pts[0][0] + (pts[-1][0] - pts[0][0]) * f,
                     pts[0][1] + (pts[-1][1] - pts[0][1]) * f + math.sin(f * 6 + li) * 5)
                    for f in (0.12, 0.3, 0.48, 0.66, 0.84)]
        for k, (sx, sy) in enumerate(stations):
            s += (f'<circle cx="{sx:.0f}" cy="{sy:.0f}" r="3.2" fill="{PANEL}" stroke="{col}" stroke-width="1.2"/>\n')
            s += (f'<circle cx="{sx:.0f}" cy="{sy:.0f}" r="3.2" fill="none" stroke="{col}" stroke-width="1">'
                  f'<animate attributeName="r" values="3.2;11;11" dur="{6 + k}s" begin="-{li * 1.7 + k * 1.1:.1f}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="opacity" values="0.7;0;0" dur="{6 + k}s" begin="-{li * 1.7 + k * 1.1:.1f}s" repeatCount="indefinite"/></circle>\n')

            # a stop event leaves the station and lands on the event-time axis
            late = (li == 2 and k == 3)
            tgt_y = late_y if late else axis_y
            drift = 40 if late else 0
            s += (f'<circle r="2" fill="{"#f0a500" if late else col}" opacity="0">'
                  f'<animateMotion path="M{sx:.0f} {sy:.0f} L{sx + drift:.0f} {tgt_y}" dur="{7 + k * 0.8 + li:.1f}s" '
                  f'begin="-{k * 1.9 + li * 0.9:.1f}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="opacity" values="0;0.9;0.9;0" dur="{7 + k * 0.8 + li:.1f}s" '
                  f'begin="-{k * 1.9 + li * 0.9:.1f}s" repeatCount="indefinite"/></circle>\n')

        for t in range(2):  # trains, different speeds and directions per line
            dur = 26 + li * 7 + t * 11
            rev = ' keyPoints="1;0" keyTimes="0;1" calcMode="linear"' if li % 2 else ""
            s += (f'<g opacity="0.95"><rect x="-9" y="-3.5" width="18" height="7" rx="2.5" fill="{PANEL}" '
                  f'stroke="{col}" stroke-width="1.2"/>'
                  f'<rect x="-9" y="-3.5" width="5" height="7" rx="2.5" fill="{col}" opacity="0.55"/>'
                  f'<animateMotion path="{path}" dur="{dur}s" begin="-{t * dur / 2 + li * 3:.1f}s" '
                  f'rotate="auto" repeatCount="indefinite"{rev}/></g>\n')


    # event-time axis and the late side output underneath it
    s += f'<line x1="96" y1="{axis_y}" x2="940" y2="{axis_y}" stroke="{LINE}" stroke-width="1"/>\n'
    for k in range(8):
        x = 96 + k * 120
        s += f'<line x1="{x}" y1="{axis_y - 4}" x2="{x}" y2="{axis_y + 4}" stroke="{DIM}" stroke-width="1"/>\n'
    s += label(96, axis_y - 12, "EVENT TIME", 9, TEXT, weight="700", ls="0.18em")
    s += label(940, axis_y - 12, "watermark + allowed lateness", 8.5, DIM, anchor="end", ls="0.06em")
    s += (f'<line x1="760" y1="{axis_y - 16}" x2="760" y2="{axis_y + 16}" stroke="{A}" stroke-width="1.4" opacity="0.8">'
          f'<animate attributeName="x1" values="620;860;620" dur="40s" repeatCount="indefinite"/>'
          f'<animate attributeName="x2" values="620;860;620" dur="40s" repeatCount="indefinite"/></line>\n')

    s += (f'<line x1="96" y1="{late_y}" x2="940" y2="{late_y}" stroke="#f0a500" stroke-width="1" '
          f'opacity="0.35" stroke-dasharray="4 6"/>\n')
    s += label(96, late_y - 8, "late_events  ·  side output, kept not dropped", 8.5, "#f0a500", ls="0.06em", op=0.8)
    s += (f'<circle cx="540" cy="{late_y}" r="3" fill="#f0a500">'
          f'<animate attributeName="opacity" values="0.2;1;0.2" dur="7s" repeatCount="indefinite"/></circle>\n')
    s += (f'<circle cx="540" cy="{late_y}" r="3" fill="none" stroke="#f0a500" stroke-width="1">'
          f'<animate attributeName="r" values="3;14;14" dur="7s" repeatCount="indefinite"/>'
          f'<animate attributeName="opacity" values="0.8;0;0" dur="7s" repeatCount="indefinite"/></circle>\n')

    # schematic punctuality series with the tumbling window sweeping across it
    rng = random.Random(3)
    base, top = 516, 444
    for k in range(32):
        x = 96 + k * 26.5
        h = rng.uniform(14, 72)
        s += f'<rect x="{x:.0f}" y="{base - h:.0f}" width="17" height="{h:.0f}" fill="{A}" opacity="0.18" rx="1"/>\n'
    s += f'<line x1="96" y1="{base}" x2="940" y2="{base}" stroke="{LINE}" stroke-width="1"/>\n'
    s += (f'<g><rect x="0" y="{top - 8}" width="196" height="{base - top + 14}" fill="{A}" opacity="0.07"/>'
          f'<rect x="0" y="{top - 8}" width="196" height="{base - top + 14}" fill="none" stroke="{A}" '
          f'stroke-width="1" opacity="0.4" stroke-dasharray="3 4"/>'
          f'<text x="8" y="{top + 6}" font-family="{MONO}" font-size="8.5" fill="{A}" letter-spacing="0.1em" '
          f'opacity="0.85">tumbling 1 h</text>'
          f'<animateTransform attributeName="transform" type="translate" values="96 0;748 0;96 0" '
          f'dur="34s" repeatCount="indefinite"/></g>\n')
    s += label(96, base + 20, "sliding 1 h / 5 min runs alongside the tumbling window", 8.5, DIM, ls="0.06em")
    s += label(940, base + 20, "schematic: throughput and punctuality not yet measured", 8.5, DIM,
               anchor="end", ls="0.06em")
    write("bvg-telemetry.svg", s)


# ------------------------------------------------------------------ metrics

METRICS = [
    ("42", "REST ENDPOINTS", "signalops-ai"),
    ("7", "n8n WORKFLOWS", "signalops-ai"),
    ("228", "TESTS", "signalops-ai"),
    ("134", "LABELLED EVAL ITEMS", "signalops-ai · 3 suites"),
    ("113", "RETRIEVAL EVAL QUESTIONS", "german-law-rag · 91 + 22 negatives"),
    ("80", "CITABLE LAW CHUNKS", "german-law-rag · Absatz level"),
    ("10,388", "LISTINGS MODELLED", "berlin-rent-predictor"),
    ("82,892", "STOP-TIME UPDATES / SNAPSHOT", "bvg-delay-stream · live feed"),
]


def metrics() -> None:
    W, H = 1000, 300
    s = head(W, H, "Engineering metrics",
             "Eight verified counts drawn from the repositories: endpoints, workflows, tests, "
             "evaluation items, retrieval questions, law chunks, listings and feed records.")
    s += kicker(28, 34, "ENGINEERING METRICS")
    s += label(W - 28, 34, "counted in the repositories", 9.5, DIM, anchor="end", ls="0.1em")

    cols, pad, gap = 4, 30, 12
    tw = (W - 2 * pad - gap * (cols - 1)) / cols
    th = 92
    for i, (num, name, src) in enumerate(METRICS):
        x = pad + (i % cols) * (tw + gap)
        y = 62 + (i // cols) * (th + gap)
        col = A if i % 2 == 0 else B
        s += panel(x, y, tw, th, LINE, PANEL)
        s += f'<rect x="{x}" y="{y}" width="2" height="{th}" fill="{col}" opacity="0.4"><animate attributeName="opacity" values="0.15;0.75;0.15" dur="{5 + i * 0.5}s" repeatCount="indefinite"/></rect>\n'
        s += label(x + 16, y + 42, num, 27, TEXT, weight="700", ls="0.01em", family=SANS)
        s += label(x + 16, y + 62, name, 8.6, MUTED, ls="0.14em")
        s += label(x + 16, y + 78, src, 8, DIM, ls="0.04em")

    # scan line: slow sweep across the panel, the only purely ambient motion here
    s += (
        f'<rect x="0" y="52" width="2" height="{H - 70}" fill="{A}" opacity="0.10">'
        f'<animate attributeName="x" values="20;{W - 20};20" dur="34s" repeatCount="indefinite"/></rect>\n'
    )
    write("metrics.svg", s)


# ------------------------------------------------------------ activity strip

PUSHES = [
    ("signalops-ai", 0, A),
    ("berlin-rent-predictor", 1, A),
    ("bvg-delay-stream", 2, A),
    ("cross-model-latent-memory", 4, B),
    ("german-law-rag", 15, B),
]


def activity() -> None:
    W, H = 1000, 230
    s = head(W, H, "Recent push activity",
             "Five repositories ordered by last push, measured in days before 5 October 2026.")
    s += kicker(28, 34, "RECENT BUILD ACTIVITY")
    s += label(W - 28, 34, "last push · as of 2026-10-05", 9.5, DIM, anchor="end", ls="0.1em")

    x0, bar_max = 250, 620
    for i, (repo, days, col) in enumerate(PUSHES):
        y = 70 + i * 26
        w = bar_max * (1 - min(days, 30) / 34)
        s += label(x0 - 14, y + 4, repo, 10, TEXT, anchor="end", ls="0.06em")
        s += f'<rect x="{x0}" y="{y - 4}" width="{w:.0f}" height="8" fill="{col}" opacity="0.18"/>\n'
        s += f'<rect x="{x0}" y="{y - 4}" width="2" height="8" fill="{col}" opacity="0.9"/>\n'
        s += (
            f'<circle r="2" cy="{y}" fill="{col}" opacity="0.85">'
            f'<animateMotion path="M{x0} {y} L{x0 + w:.0f} {y}" dur="{6 + i * 1.3}s" begin="-{i * 1.6}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0.9;0" dur="{6 + i * 1.3}s" begin="-{i * 1.6}s" repeatCount="indefinite"/></circle>\n'
        )
        d = "today" if days == 0 else f"{days}d ago"
        s += label(x0 + w + 10, y + 4, d, 9, MUTED, ls="0.04em")

    s += node(40, 204, 7, A, dur=2.6, halo=True)
    s += label(58, 208, "ACTIVE", 9.5, A, weight="700", ls="0.2em")
    s += label(124, 208, "five repositories pushed within the last month", 9, DIM, ls="0.06em")
    write("activity-strip.svg", s)


if __name__ == "__main__":
    hero()
    knowledge_graph()
    ecosystem()
    signalops()
    legal_field()
    bvg_telemetry()
    metrics()
    activity()
