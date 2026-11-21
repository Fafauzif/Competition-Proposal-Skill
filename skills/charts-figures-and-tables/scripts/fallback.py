"""Matplotlib chart backend for the Essay Studio JSON contract."""

from __future__ import annotations

import math
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager
from matplotlib import pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

from charts import COLORS, atomic_bytes, valid_png


def wrap(value, width):
    return "\n".join(textwrap.fill(line, width=width) for line in str(value).split("\n"))


def make_figure(spec, height, diagram=False):
    figure, axes = plt.subplots(figsize=(spec.get("width_cm", 16) / 2.54, height / 2.54),
                               layout="constrained")
    if diagram:
        axes.set_axis_off()
        axes.set_xlim(0, 1)
        axes.set_ylim(0, 1)
    else:
        axes.spines[["right", "top"]].set_visible(False)
        axes.set_axisbelow(True)
    return figure, axes


def box(axes, x, y, width, height, label, colors, *, fill=None, bold=False):
    axes.add_patch(Rectangle((x - width / 2, y - height / 2), width, height,
                             facecolor=fill or colors["sage"],
                             edgecolor=colors["rule"], linewidth=0.55, zorder=2))
    axes.text(x, y, label, va="center", ha="center", color=colors["ink"],
              weight="bold" if bold else "normal", zorder=3)


def edge(axes, start, end, colors, *, head=True, turn=None):
    if turn:
        axes.plot([start[0], turn, turn, end[0]], [start[1], start[1], end[1], end[1]],
                  color=colors["forest"], linewidth=0.8, zorder=1)
        return
    arrow = FancyArrowPatch(start, end, arrowstyle="-|>" if head else "-",
                            color=colors["forest"], mutation_scale=9, linewidth=0.8,
                            shrinkA=0, shrinkB=0, zorder=1)
    axes.add_patch(arrow)


def gantt(spec, colors, main, _meta):
    labels = [wrap(task["label"], 37) for task in spec["tasks"]]
    rows = [label.count("\n") + 1 for label in labels]
    height = spec.get("height_cm", max(3.3 if main else 4, 1.15 + .51 * sum(rows)))
    figure, axes = make_figure(spec, height)
    count = len(spec["periods"])
    position = 0
    centers = []
    for label_rows, task in zip(rows, spec["tasks"]):
        center = position + label_rows / 2
        centers.append(center)
        start, end = task["start"], task["end"]
        shade = colors["clay"] if task.get("critical") else colors["forest"]
        axes.barh(center, end - start + 1 - .08, left=start - 1 + .04, height=.53, color=shade)
        position += label_rows
    axes.set_ylim(position + .13, -.13)
    axes.set_xlim(0, count)
    axes.set_xticks([x + .5 for x in range(count)], spec["periods"])
    axes.xaxis.tick_top()
    axes.set_yticks(centers, labels)
    axes.tick_params(axis="both", length=0, pad=3)
    axes.spines[["left", "bottom"]].set_visible(False)
    for x in range(count + 1):
        axes.axvline(x, color=colors["rule"], linewidth=.45)
    return figure


def bar_comparison(spec, colors, main, _meta):
    items = spec["categories"]
    series = spec["series"]
    figure, axes = make_figure(spec, spec.get("height_cm", max(3.1 if main else 4,
                                                               2 + len(items) * .65)))
    block = .72 / len(series)
    shades = [colors[k] for k in ("forest", "clay", "gray", "rule")]
    for index, item in enumerate(series):
        y = [row + (index - (len(series) - 1) / 2) * block for row in range(len(items))]
        bars = axes.barh(y, item["values"], height=block * .92, color=shades[index],
                         label=item.get("label", ""))
        axes.bar_label(bars, padding=3, fmt="%g", fontsize="small")
    values = [v for item in series for v in item["values"]]
    lo, hi = min(0, min(values)), max(0, max(values))
    span = hi - lo or 1
    axes.set_xlim(lo - (span * .17 if lo < 0 else 0), hi + span * .17)
    axes.set_yticks(range(len(items)), [wrap(item, 30) for item in items])
    axes.invert_yaxis()
    axes.set_xlabel(spec.get("x_label", ""))
    axes.grid(axis="x", color=colors["rule"], alpha=.45)
    if len(series) > 1:
        axes.legend(frameon=False, fontsize="small")
    return figure


def cash_line(spec, colors, main, _meta):
    figure, axes = make_figure(spec, spec.get("height_cm", 4.8 if main else 6.2))
    for item, shade, pattern in zip(spec["series"], ("forest", "clay", "gray", "ink"),
                                    ("-", "--", "-.", ":")):
        axes.plot(spec["periods"], item["values"], label=item["label"],
                  color=colors[shade], linestyle=pattern, linewidth=1.35)
    axes.set_xlabel(spec.get("x_label", "Bulan"))
    axes.set_ylabel(spec.get("y_label", "Juta Rp"))
    axes.grid(color=colors["rule"], alpha=.45)
    if len(spec["series"]) > 1:
        axes.legend(frameon=False, fontsize="small")
    return figure


def distribution(spec, colors, main, meta):
    figure, axes = make_figure(spec, spec.get("height_cm", 4.8 if main else 6.2))
    values = spec["values"]
    lo, hi = min(values), max(values)
    if lo == hi:
        padding = max(1, abs(lo) * .1)
        lo, hi = lo - padding, hi + padding
    count = meta["bins"]
    step = (hi - lo) / count
    counts = meta["bin_counts"]
    axes.bar([lo + i * step for i in range(count)], counts, width=step, align="edge",
             color=colors["forest"], edgecolor="white", linewidth=.35)
    axes.set_xlabel(spec.get("x_label", "Nilai"))
    axes.set_ylabel(spec.get("y_label", "Frekuensi"))
    if spec.get("show_quantiles", True):
        groups = {}
        for label, value in meta["quantiles_linear"].items():
            groups.setdefault(value, []).append("P" + label)
        for i, (value, labels) in enumerate(groups.items()):
            axes.axvline(value, color=colors["ink"], linestyle="--", linewidth=.8)
            axes.annotate("/".join(labels), (value, .98 - .18 * i), xycoords=("data", "axes fraction"),
                          xytext=(3, -1), textcoords="offset points", va="top",
                          fontsize="small", color=colors["ink"],
                          bbox={"facecolor": "white", "edgecolor": "none", "alpha": .9, "pad": 1})
    return figure


def drivers(spec, colors, main, _meta):
    values = spec["values"]
    figure, axes = make_figure(spec, spec.get("height_cm", max(3.2 if main else 4,
                                                               1.8 + len(values) * .48)))
    axes.barh(range(len(values)), values, height=.61,
              color=[colors["forest" if value >= 0 else "clay"] for value in values])
    axes.set_xlim(-1, 1)
    axes.set_yticks(range(len(values)), [wrap(item, 29) for item in spec["labels"]])
    axes.invert_yaxis()
    axes.set_xlabel(spec.get("x_label", "Spearman ρ"))
    axes.axvline(0, color=colors["ink"], linewidth=.65)
    axes.grid(axis="x", color=colors["rule"], alpha=.45)
    return figure


def risk_heatmap(spec, colors, _main, _meta):
    from matplotlib.colors import to_rgb
    figure, axes = make_figure(spec, spec.get("height_cm", 7))
    cells = {}
    for item in spec["risks"]:
        cells.setdefault((item["impact"], item["probability"]), []).append(str(item["id"]))
    for impact in range(1, 6):
        for likelihood in range(1, 6):
            score = impact * likelihood
            rgb = to_rgb(colors["clay" if score >= 12 else "forest"])
            strength = .18 + score * .024
            blend = tuple(1 - (1 - v) * strength for v in rgb)
            axes.add_patch(Rectangle((impact - .5, likelihood - .5), 1, 1,
                                     facecolor=blend, edgecolor="white"))
            names = cells.get((impact, likelihood), [])
            if names:
                axes.text(impact, likelihood, wrap(", ".join(names), 15), ha="center", va="center")
    axes.set(xlim=(.5, 5.5), ylim=(.5, 5.5), xlabel=spec.get("x_label", "Dampak"),
             ylabel=spec.get("y_label", "Kemungkinan"))
    axes.set_xticks(range(1, 6))
    axes.set_yticks(range(1, 6))
    if spec.get("legend"):
        figure.supxlabel(wrap(spec["legend"], 75), fontsize="small")
    return figure


def positioning(spec, colors, _main, _meta):
    figure, axes = make_figure(spec, spec.get("height_cm", 7), diagram=True)
    axes.set_xlim(-1.45, 1.45)
    axes.set_ylim(-1.32, 1.32)
    edge(axes, (-1.03, 0), (1.05, 0), colors)
    edge(axes, (0, -1.03), (0, 1.05), colors)
    for key, x, y, align in [("x_low", -1.04, 0, "right"), ("x_high", 1.06, 0, "left"),
                              ("y_low", 0, -1.15, "center"), ("y_high", 0, 1.15, "center")]:
        axes.text(x, y, wrap(spec[key], 13 if key.startswith("x") else 30), ha=align, va="center")
    for item in spec["points"]:
        x, y = item["x"], item["y"]
        axes.plot(x, y, "o", markersize=4, color=colors["forest"])
        axes.text(x + item.get("label_dx", 0), y + item.get("label_dy", .12),
                  wrap(item["label"], 21), ha="center", va="bottom")
    return figure


def issue_tree(spec, colors, _main, _meta):
    groups, issues, leaves = [], [], []
    for branch in spec["branches"]:
        begin = len(leaves)
        for issue in branch["issues"]:
            start = len(leaves)
            for cause in issue["causes"]:
                if isinstance(cause, str):
                    leaves.append(wrap(cause, 28))
                else:
                    caption = cause["text"]
                    if cause.get("citation"):
                        caption += "\n" + cause["citation"]
                    leaves.append(wrap(caption, 28))
            issues.append((start, len(leaves) - 1, issue["issue"]))
        groups.append((begin, len(leaves) - 1, branch["subproblem"]))
    weights = [max(2, label.count("\n") + 1) for label in leaves]
    height = spec.get("height_cm", max(5.8, 1.8 + .44 * sum(weights)))
    figure, axes = make_figure(spec, height, diagram=True)
    axes.set_ylim(0, sum(weights) + 2.4)
    positions = []
    leading = sum(weights) + .35
    for weight in weights:
        positions.append(leading - weight / 2)
        leading -= weight
    columns = [.08, .267, .49, .806]
    widths = [.15, .17, .22, .39]
    headings = [spec.get("goal_label", "Tujuan / masalah"), spec.get("subproblem_label", "Submasalah"),
                spec.get("issue_label", "Isu"), spec.get("cause_label", "Akar penyebab")]
    for x, width, text in zip(columns, widths, headings):
        box(axes, x, sum(weights) + 1.52, width, 1.35, wrap(text, 16), colors, bold=True)
    root_y = (positions[0] + positions[-1]) / 2
    root = wrap(spec["goal"], 12)
    box(axes, columns[0], root_y, widths[0], max(1.65, (root.count("\n") + 1) * .92),
        root, colors, fill="white")
    for start, end, label in groups:
        y = (positions[start] + positions[end]) / 2
        tile = wrap(label, 14)
        box(axes, columns[1], y, widths[1], max(1.65, (tile.count("\n") + 1) * .92),
            tile, colors, fill="white")
        edge(axes, (columns[0] + widths[0] / 2, root_y), (columns[1] - widths[1] / 2, y), colors,
             turn=.166)
        for a, b, issue in issues:
            if start <= a <= end:
                issue_y = (positions[a] + positions[b]) / 2
                tile = wrap(issue, 19)
                box(axes, columns[2], issue_y, widths[2], max(1.65, (tile.count("\n") + 1) * .92),
                    tile, colors, fill="white")
                edge(axes, (columns[1] + widths[1] / 2, y),
                     (columns[2] - widths[2] / 2, issue_y), colors, turn=.365)
                for leaf in range(a, b + 1):
                    edge(axes, (columns[2] + widths[2] / 2, issue_y),
                         (columns[3] - widths[3] / 2, positions[leaf]), colors, turn=.609)
    for y, weight, label in zip(positions, weights, leaves):
        box(axes, columns[3], y, widths[3], weight - .14, label, colors, fill="white")
    return figure


def service_flow(spec, colors, _main, _meta):
    exception = spec.get("exception_label")
    figure, axes = make_figure(spec, spec.get("height_cm", 8.9 if exception else 5.8), diagram=True)
    top, bottom = .82, .50 if exception else .31
    xs = [.19, .50, .81]
    coords = [(x, top) for x in xs] + [(x, bottom) for x in reversed(xs)]
    width, height = .267, .23 if exception else .33
    for (x, y), label in zip(coords, spec["stages"]):
        box(axes, x, y, width, height, wrap(label, 22), colors)
    for (x, y), (next_x, next_y) in zip(coords, coords[1:]):
        if y == next_y:
            dx = width / 2 if next_x > x else -width / 2
            edge(axes, (x + dx, y), (next_x - dx, y), colors)
        else:
            edge(axes, (x, y - height / 2), (next_x, next_y + height / 2), colors)
    if exception:
        location = int(spec.get("exception_from", 4)) - 1
        x, y = coords[location]
        ex_y, ex_height = .14, .20
        # Run alongside a row when the exception originates above another stage.
        bypass = x + width / 2 + .02
        if location < 3:
            axes.plot([x + width / 2, bypass, bypass], [y, y, ex_y + ex_height / 2],
                      color=colors["clay"], linewidth=.9, zorder=1)
            edge(axes, (bypass, ex_y + ex_height / 2), (min(.83, bypass), ex_y + ex_height / 2 - .015),
                 colors | {"forest": colors["clay"]})
        else:
            edge(axes, (x, y - height / 2), (x, ex_y + ex_height / 2),
                 colors | {"forest": colors["clay"]})
        detail = exception
        if spec.get("resume_label"):
            detail += "\n" + spec["resume_label"]
        box(axes, .5, ex_y, .82, ex_height, wrap(detail, 68), colors, fill="white")
    return figure


def tam_sam_som(spec, colors, _main, _meta):
    height = spec.get("height_cm", 7.1)
    figure, axes = make_figure(spec, height, diagram=True)
    # All three tiers display the same semantic level and values as the JSON.
    axes.set_aspect("equal", adjustable="box")
    axes.set_xlim(0, spec.get("width_cm", 16) / height)
    centers = [.55, .44, .33]
    radius = [.43, .32, .21]
    for y, r, shade in zip(centers, radius, ("forest", "clay", "sage")):
        axes.add_patch(Circle((.47, y), r, edgecolor="white", facecolor=colors[shade], linewidth=.6))
    positions = [.875, .665, .32]
    for index, (level, y) in enumerate(zip(spec["levels"], positions)):
        axes.text(.47, y, str(level["label"]) + "\n" + wrap(level["value"], 20),
                  color="white" if index != 2 else colors["ink"], ha="center", va="center",
                  weight="bold", fontsize="small")
        x = .47 + math.sqrt(max(0, radius[index] ** 2 - (y - centers[index]) ** 2))
        edge(axes, (x + .025, y), (1.00, y), colors, head=False)
        axes.text(1.05, y + .027, wrap(level["description"], 36), ha="left", va="bottom", weight="bold")
        axes.text(1.05, y - .016, wrap(level.get("basis", ""), 40), ha="left", va="top", fontsize="small")
    return figure


def structure_tree(spec, colors, _main, _meta):
    nodes = {str(node["id"]): node for node in spec["nodes"]}
    children = {name: [] for name in nodes}
    for name, node in nodes.items():
        if node.get("parent") is None:
            root = name
        else:
            children[str(node["parent"])].append(name)
    positions = {}
    leaf = 0

    def position(key, depth):
        nonlocal leaf
        if children[key]:
            values = [position(k, depth + 1) for k in children[key]]
            x = sum(values) / len(values)
        else:
            x = leaf
            leaf += 1
        positions[key] = (x, depth)
        return x

    position(root, 0)
    levels = max(depth for _, depth in positions.values()) + 1
    figure, axes = make_figure(spec, spec.get("height_cm", 2.1 * levels), diagram=True)
    axes.set_xlim(-.56, leaf - .44)
    axes.set_ylim(levels - .5, -.5)
    width, height = .89, .66
    for key, (x, y) in positions.items():
        for child in children[key]:
            child_x, child_y = positions[child]
            mid = (y + child_y) / 2
            axes.plot([x, x, child_x, child_x], [y + height / 2, mid, mid, child_y - height / 2],
                      color=colors["forest"], linewidth=.8, zorder=1)
        box(axes, x, y, width, height, wrap(nodes[key]["label"], max(11, 76 // leaf)), colors,
            bold=(key == root))
    return figure


def value_proposition(spec, colors, _main, _meta):
    left, offer, right = (spec[key] for key in ("left", "offer", "right"))
    columns = [
        (left["name"], [(left.get("jobs_heading", "Pekerjaan"), left["jobs"])]),
        (left.get("needs_heading", "Kebutuhan"), [(left.get("gains_heading", "Manfaat"), left["gains"]),
                                                  (left.get("pains_heading", "Hambatan"), left["pains"])]),
        (offer["name"], [(offer.get("gain_heading", "Pencipta manfaat"), offer["gain_creators"]),
                         (offer.get("pain_heading", "Pengurai hambatan"), offer["pain_relievers"])]),
        (right.get("needs_heading", "Kebutuhan"), [(right.get("gains_heading", "Manfaat"), right["gains"]),
                                                   (right.get("pains_heading", "Hambatan"), right["pains"])]),
        (right["name"], [(right.get("jobs_heading", "Pekerjaan"), right["jobs"])]),
    ]
    width = .18
    labels = [[title + "\n\n" + "\n".join(wrap(line, 15) for line in lines)
               for title, lines in tiles] for _, tiles in columns]
    max_lines = max(label.count("\n") + 1 for column in labels for label in column)
    figure, axes = make_figure(spec, spec.get("height_cm", max(7.7, .83 * max_lines + 1.6)), diagram=True)
    xs = [.097, .298, .5, .702, .903]
    for i, ((title, _), group) in enumerate(zip(columns, labels)):
        x = xs[i]
        axes.text(x, .952, wrap(title, 16), ha="center", va="center", weight="bold")
        ys = [.445] if len(group) == 1 else [.66, .23]
        for y, label in zip(ys, group):
            box(axes, x, y, width, .833 if len(group) == 1 else .40, label, colors,
                fill=colors["sage"] if i == 2 else "white")
    for y in (.66, .23):
        for x in (xs[1], xs[3]):
            shift = width / 2 if x < .5 else -width / 2
            edge(axes, (.5 - shift, y), (x + shift, y), colors)
    return figure


RENDERERS = {name: globals()[name] for name in (
    "issue_tree", "service_flow", "tam_sam_som", "gantt", "risk_heatmap", "bar_comparison",
    "cash_line", "distribution", "drivers", "structure_tree", "positioning", "value_proposition",
)}


def render(spec, name, output, dpi, profile, meta, *, require_font=False):
    wanted_font = spec.get("font", "Liberation Serif")
    installed_fonts = {item.name for item in font_manager.fontManager.ttflist}
    if require_font and wanted_font not in installed_fonts:
        raise RuntimeError(f"Required font unavailable to Matplotlib: {wanted_font}")
    font = wanted_font if wanted_font in installed_fonts else "DejaVu Serif"
    colors = {key: "#" + value for key, value in (COLORS | spec.get("colors", {})).items()}
    pt = spec.get("font_pt", 10)
    settings = {"font.family": font, "font.size": pt, "axes.labelsize": pt,
                "xtick.labelsize": pt * .9, "ytick.labelsize": pt * .9,
                "text.color": colors["ink"], "axes.labelcolor": colors["ink"],
                "axes.edgecolor": colors["rule"], "pdf.fonttype": 42, "svg.fonttype": "none",
                "axes.formatter.use_locale": False, "text.parse_math": False}
    from io import BytesIO
    with plt.rc_context(settings):
        figure = RENDERERS[spec["type"]](spec, colors, profile == "main", meta)
        try:
            content = {}
            for extension in ("png", "pdf", "svg"):
                with BytesIO() as buffer:
                    figure.savefig(buffer, format=extension, dpi=dpi, bbox_inches="tight",
                                   pad_inches=.04, facecolor="white")
                    content[extension] = buffer.getvalue()
            valid_png(content["png"])
            for extension, data in content.items():
                atomic_bytes(output / f"{name}.{extension}", data)
        finally:
            plt.close(figure)
    return {"backend": "matplotlib", "font_used": font,
            "font_requested": wanted_font, "font_substituted": font != wanted_font,
            "pdf": str(output / f"{name}.pdf"), "png": str(output / f"{name}.png"),
            "svg": str(output / f"{name}.svg"), "render_status": "rendered"}
