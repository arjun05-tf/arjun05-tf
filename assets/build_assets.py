#!/usr/bin/env python3
"""Generates the animated SVGs used by the profile README.

Run: python assets/build_assets.py
Every figure in the output is counted in the repository it names.
SMIL animation only (CSS keyframes are unreliable inside GitHub's <img> context).
"""

from __future__ import annotations

import math
import pathlib
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


def slab(cx, y, hw, hh, stroke, accent, depth=16):
    """Isometric plate with an extruded side, so the stack reads as depth."""
    top = f"{cx - hw},{y} {cx},{y - hh} {cx + hw},{y} {cx},{y + hh}"
    left = f"{cx - hw},{y} {cx},{y + hh} {cx},{y + hh + depth} {cx - hw},{y + depth}"
    right = f"{cx + hw},{y} {cx},{y + hh} {cx},{y + hh + depth} {cx + hw},{y + depth}"
    s = f'<polygon points="{left}" fill="#080b11" stroke="{stroke}" stroke-width="1"/>\n'
    s += f'<polygon points="{right}" fill="#0a0e16" stroke="{stroke}" stroke-width="1"/>\n'
    s += f'<polygon points="{top}" fill="#10151f" stroke="{stroke}" stroke-width="1"/>\n'
    s += f'<polygon points="{top}" fill="{accent}" opacity="0.05"/>\n'
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
    s = head(W, H, "Arjun Patil — system map",
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
             "Seven clusters — AI/LLM, retrieval, automation, streaming, ML, systems and research — "
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


# ------------------------------------------------------------------ pipelines

def pipeline(name: str, title: str, desc: str, kick: str, stages: list[tuple[str, str]],
             col: str, note: str) -> None:
    W, H = 1000, 250
    n = len(stages)
    pad, gap = 30, 12
    bw = (W - 2 * pad - gap * (n - 1)) / n
    y, bh = 92, 74
    s = head(W, H, title, desc)
    s += kicker(28, 34, kick)
    s += label(W - 28, 34, note, 9.5, DIM, anchor="end", ls="0.1em")

    for i, (main, meta) in enumerate(stages):
        x = pad + i * (bw + gap)
        s += panel(x, y, bw, bh, LINE, PANEL)
        s += f'<rect x="{x}" y="{y}" width="{bw:.1f}" height="1.6" fill="{col}" opacity="0.35"><animate attributeName="opacity" values="0.15;0.7;0.15" dur="{4.5 + i * 0.4}s" repeatCount="indefinite"/></rect>\n'
        lines = main.split("\n")
        for li, line in enumerate(lines):
            s += label(x + bw / 2, y + 30 + li * 16 - (len(lines) - 1) * 8, line, 11.5, TEXT,
                       anchor="middle", weight="700", ls="0.1em")
        s += label(x + bw / 2, y + bh - 12, meta, 9, MUTED, anchor="middle", ls="0.02em")
        if i < n - 1:
            ax, bx = x + bw, x + bw + gap
            s += edge(ax, y + bh / 2, bx, y + bh / 2, col, 1.0, 0.45)
            s += f'<path d="M{bx - 4} {y + bh / 2 - 3} L{bx} {y + bh / 2} L{bx - 4} {y + bh / 2 + 3}" fill="none" stroke="{col}" stroke-width="1" opacity="0.6"/>\n'

    # records travel on a rail under the stages: one dot = one record in flight
    track = y + bh + 32
    s += f'<line x1="{pad}" y1="{track}" x2="{W - pad}" y2="{track}" stroke="{LINE}" stroke-width="1"/>\n'
    for i in range(n):
        x = pad + i * (bw + gap) + bw / 2
        s += edge(x, y + bh, x, track, LINE, 0.8, 0.7)
        s += f'<circle cx="{x:.1f}" cy="{track}" r="2.2" fill="{PANEL}" stroke="{col}" stroke-width="1" opacity="0.7"/>\n'
    path = f"M{pad} {track} L{W - pad} {track}"
    for k in range(4):
        s += (
            f'<circle r="{3.0 - k * 0.35:.1f}" fill="{col}" opacity="0.9">'
            f'<animateMotion path="{path}" dur="{9 + k * 1.7}s" begin="-{k * 2.6}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0.95;0.95;0" dur="{9 + k * 1.7}s" begin="-{k * 2.6}s" repeatCount="indefinite"/>'
            "</circle>\n"
        )
    s += label(pad, track + 24, "record in flight", 8.5, DIM, ls="0.14em")
    write(name, s)


# ------------------------------------------------------------------- stack

STACK = [
    ("AI / LLM", "Claude · OpenAI · structured output · prompt versions", B),
    ("RETRIEVAL", "multilingual-e5 · Qdrant · cross-encoder rerank", B),
    ("APPLICATION", "FastAPI · Pydantic · Next.js console", A),
    ("AUTOMATION", "n8n · HMAC webhooks · retries · CRM sync", A),
    ("STREAMING", "protobuf · Redpanda · Flink · event time", A),
    ("STORAGE", "PostgreSQL · TimescaleDB · Qdrant", A),
    ("OPERATIONS", "Docker · GitHub Actions · MLflow · Grafana", A),
]


def stack() -> None:
    W, H = 1000, 560
    s = head(W, H, "Stack as layers",
             "Seven isometric layers from AI and retrieval down through application, automation, "
             "streaming, storage and operations, with a request descending through them.")
    s += kicker(28, 34, "STACK")
    s += label(W - 28, 34, "one request, top to bottom", 9.5, DIM, anchor="end", ls="0.1em")

    cx, hw, hh, step, top = 500, 400, 44, 66, 80
    for i, (name, techs, col) in enumerate(STACK):
        y = top + i * step
        s += slab(cx, y, hw, hh, LINE, col)
        s += label(cx - 196, y - 1, name, 11, TEXT, weight="700", ls="0.16em")
        s += label(cx - 196, y + 16, techs, 9.5, MUTED, ls="0.03em")
        s += node(cx + 212, y + 6, 8, col, dur=4.4 + i * 0.5, offset=i * 0.9, halo=False)
        if i < len(STACK) - 1:
            s += edge(cx + 212, y + 15, cx + 212, y + step - 3, col, 0.9, 0.25)

    rail = f"M{cx + 212} {top + 6} L{cx + 212} {top + 6 + (len(STACK) - 1) * step}"
    for k in range(3):
        s += (
            f'<circle r="{2.4 - k * 0.4:.1f}" fill="{A}" opacity="0.9">'
            f'<animateMotion path="{rail}" dur="{7 + k * 2.5}s" begin="-{k * 2.4}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0.9;0.9;0" dur="{7 + k * 2.5}s" begin="-{k * 2.4}s" repeatCount="indefinite"/>'
            "</circle>\n"
        )
    write("stack-layers.svg", s)


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
    pipeline(
        "signalops-flow.svg", "SignalOps AI pipeline",
        "Lead intake, research, security signals, qualification, model draft, grounding validation, "
        "human approval and CRM sync.",
        "SIGNALOPS AI · LEAD TO CRM",
        [("LEAD", "webhook, HMAC"), ("RESEARCH", "enrichment"), ("SECURITY\nSIGNALS", "23 signal keys"),
         ("QUALIFY", "rules + model"), ("LLM\nDRAFT", "German outreach"), ("GROUNDING", "claim ↔ evidence"),
         ("HUMAN\nAPPROVAL", "nothing auto-sent"), ("CRM", "sync + follow-up")],
        A, "deterministic code owns every write",
    )
    pipeline(
        "bvg-stream.svg", "BVG delay stream pipeline",
        "GTFS-Realtime producer into Redpanda, Flink event-time windows, TimescaleDB aggregates, Grafana.",
        "BVG DELAY STREAM · EVENT TIME",
        [("PRODUCER", "protobuf, 30 s poll"), ("REDPANDA", "6 partitions + DLQ"),
         ("FLINK", "tumbling 1 h · sliding 5 min"), ("TIMESCALEDB", "idempotent upsert"),
         ("GRAFANA", "punctuality by line")],
        A, "watermarks · late records kept, not dropped",
    )
    pipeline(
        "rag-pipeline.svg", "German law RAG pipeline",
        "Query, multilingual embedding, Qdrant vector search, cross-encoder rerank, evidence selection, "
        "grounded answer or refusal.",
        "GERMAN LAW RAG · QUERY TO CITATION",
        [("QUERY", "DE or EN"), ("EMBEDDING", "multilingual-e5, 768d"), ("VECTOR\nSEARCH", "Qdrant, top-20"),
         ("RERANK", "cross-encoder"), ("EVIDENCE", "Absatz-level § chunks"), ("ANSWER", "cited, or refusal")],
        B, "recall@1 0.44 → 0.60 after rerank",
    )
    stack()
    metrics()
    activity()
