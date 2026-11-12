"""Render the Kenya food prices data story as an animated GIF.

Every number on screen is computed from Data/FactPrices.csv and the dimension
tables, using the same definitions as the dashboard's DAX measures.

Usage:  python animation/make_animation.py
Needs:  pandas, matplotlib, and ffmpeg on the PATH.
Output: animation/kenya_food_story.gif
"""
import glob
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "Data"
OUT = HERE / "kenya_food_story.gif"
FPS = 15
W, H, DPI = 9.6, 5.4, 100  # 960 x 540

# Brand theme (theme/kenya_food_prices_theme.json)
CRIMSON, NAVY, MUTED, NEUTRAL, BG = "#980016", "#04143D", "#5A6B85", "#DADADF", "#FFFFFF"
GRID = "#ECECEF"

for path in glob.glob("/usr/share/fonts/opentype/inter/Inter-*.otf"):
    font_manager.fontManager.addfont(path)
if any(f.name == "Inter" for f in font_manager.fontManager.ttflist):
    plt.rcParams["font.family"] = "Inter"

# ---------------------------------------------------------------- data
fact = pd.read_csv(DATA / "FactPrices.csv", parse_dates=["Date"])
market = pd.read_csv(DATA / "DimMarket.csv")
dates = pd.read_csv(DATA / "DimDate.csv", parse_dates=["Date"])
fact = fact.merge(market, on="MarketID")
fact["Year"] = fact.Date.dt.year

# Rolling 12-month average price per kg (row-weighted, like the DAX measure)
month_ends = pd.period_range(fact.Date.min(), fact.Date.max(), freq="M").to_timestamp("M")
priced = fact.dropna(subset=["PricePerKg"])
roll = np.array([
    priced.loc[(priced.Date > e - pd.DateOffset(months=12)) & (priced.Date <= e), "PricePerKg"].mean()
    for e in month_ends
])
roll_x = np.array([e.year + (e.month - 0.5) / 12 for e in month_ends])
START, END = roll[0], roll[-1]
V2021 = roll[list(month_ends.year).index(2021) + 11]  # Dec 2021
SHARE_AFTER_2021 = (END - V2021) / (END - START)

yearly = fact.groupby("Year").PricePerKg.mean()
yoy = yearly.pct_change() * 100
YOY_2008, YOY_2022 = yoy[2008], yoy[2022]

county = fact.groupby("County").PricePerKg.mean().sort_values(ascending=False)
TOP10 = county.head(10)
NAIROBI_RANK = list(county.index).index("Nairobi") + 1
NATIONAL = fact.PricePerKg.mean()

CAMP_AVG = fact.loc[fact.IsRefugeeCamp, "PricePerKg"].mean()
OTHER_AVG = fact.loc[~fact.IsRefugeeCamp, "PricePerKg"].mean()
N_CAMP = int(market.IsRefugeeCamp.sum())
mk = market.dropna(subset=["Latitude", "Longitude"]).merge(
    fact.groupby("MarketID").PricePerKg.mean().rename("avg"), on="MarketID", how="left")
mk["avg"] = mk["avg"].fillna(NATIONAL)
rng = np.random.default_rng(7)
mk["order"] = rng.random(len(mk))

shock = dates[dates.IsShockPeriod].groupby("ShockEvent").Date.agg(["min", "max"])
frac = lambda d: d.year + (d.dayofyear - 1) / 365.25
SHOCKS = [(frac(r["min"]), frac(r["max"])) for _, r in shock.sort_values("min").iterrows()]
SHOCK_LABELS = [  # (x-centre, row, text); the two 2022-23 bands share one label
    (2008.1, 0, "2008 post-election crisis"), (2011.75, 1, "2011 drought"),
    (2017.5, 0, "2017 maize crisis"), (2020.45, 1, "COVID-19"),
    (2022.7, 0, "2022–23 fuel shock + drought"),
]

outline = []
geo = json.load(open(HERE / "kenya_outline.geojson"))["features"][0]["geometry"]
polys = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
for poly in polys:
    outline.append(np.array(poly[0]))

print(f"rolling avg {START:.1f} -> {END:.1f} KES/kg (x{END / START:.2f}); "
      f"share of rise after 2021: {SHARE_AFTER_2021:.0%}")
print(f"YoY 2008 {YOY_2008:.1f}%  2022 {YOY_2022:.1f}%  ratio {YOY_2008 / YOY_2022:.2f}")
print(f"camps {CAMP_AVG:.1f} vs other {OTHER_AVG:.1f}; national {NATIONAL:.1f}; Nairobi rank {NAIROBI_RANK}")


# ---------------------------------------------------------------- helpers
def ease(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def ramp(t, start, dur):
    """0 -> 1 eased progress of a sub-animation starting at `start` seconds."""
    return ease((t - start) / dur)


def header(fig, chapter, title, subtitle, t):
    a = ramp(t, 0, 0.5)
    if chapter:
        fig.text(0.06, 0.925, chapter, size=10, weight="bold", color=CRIMSON, alpha=a)
    fig.text(0.06, 0.855, title, size=21, weight="bold", color=NAVY, alpha=a)
    fig.text(0.06, 0.80, subtitle, size=11, color=MUTED, alpha=a)


def footer(fig, progress):
    fig.text(0.06, 0.035, "Source: WFP Kenya food prices via HDX · Jan 2006 – Mar 2026",
             size=8, color=MUTED)
    fig.add_artist(plt.Rectangle((0, 0), 1, 0.008, color=GRID, transform=fig.transFigure))
    fig.add_artist(plt.Rectangle((0, 0), progress, 0.008, color=CRIMSON, transform=fig.transFigure))


def clean_axes(ax, left=False):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(NEUTRAL)
    ax.tick_params(length=0, labelsize=9, labelcolor=MUTED)
    ax.set_facecolor(BG)


# ---------------------------------------------------------------- scenes
def scene_title(fig, t):
    a = ramp(t, 0.1, 0.7)
    fig.add_artist(plt.Rectangle((0.06, 0.70), 0.07 * a, 0.012, color=CRIMSON,
                                 transform=fig.transFigure))
    fig.text(0.06, 0.56, "Twenty Years of Hunger", size=40, weight="bold", color=NAVY, alpha=a)
    fig.text(0.06, 0.47, "What Kenya's food price data reveals", size=18, color=MUTED,
             alpha=ramp(t, 0.5, 0.7))
    stats = [(f"{len(fact):,}", "price records"), (f"{len(market)}", "markets"),
             (f"{market.County.nunique()}", "counties"), ("2006–2026", "monthly data")]
    for i, (num, label) in enumerate(stats):
        a = ramp(t, 1.0 + 0.2 * i, 0.6)
        x = 0.06 + i * 0.21
        fig.text(x, 0.27 - 0.02 * (1 - a), num, size=24, weight="bold", color=CRIMSON, alpha=a)
        fig.text(x, 0.215 - 0.02 * (1 - a), label, size=11, color=MUTED, alpha=a)


def scene_trend(fig, t):
    header(fig, "1 OF 4", "Food prices have roughly quadrupled since 2006",
           "Average retail price per kg (KES), rolling 12-month average, all monitored foods", t)
    ax = fig.add_axes([0.07, 0.13, 0.87, 0.60])
    clean_axes(ax)
    ax.set_xlim(2005.6, 2027.6)
    ax.set_ylim(0, 150)
    ax.set_yticks([0, 25, 50, 75, 100, 125])
    ax.set_xticks(range(2006, 2027, 4))
    ax.grid(axis="y", color=GRID, lw=1)
    ax.set_axisbelow(True)

    # near-linear sweep reads better for a time axis than a hard ease
    p = min(max((t - 0.6) / 6.5, 0), 1)
    n = max(int(p * (len(roll) - 1)), 0)
    head_x, head_y = roll_x[n], roll[n]

    for x0, x1 in SHOCKS:
        if head_x >= x0:
            ax.axvspan(x0, x1, color=CRIMSON, alpha=0.16 * ease((head_x - x0) / 0.6), lw=0)
    for xc, row, text in SHOCK_LABELS:
        if head_x >= xc - 0.3:
            ax.text(xc, 143 - 11 * row, text, ha="center", va="center", size=8.5,
                    color=CRIMSON, weight="bold", alpha=ease((head_x - xc + 0.3) / 0.8))

    after = ramp(t, 9.2, 0.8)
    if after > 0:
        ax.axvspan(2022.0, roll_x[-1], ymax=0.80, color=NAVY, alpha=0.07 * after, lw=0)
        ax.text(2021.8, 12, f"{SHARE_AFTER_2021:.0%} of the 20-year rise\ncame after 2021",
                ha="right", va="bottom", size=12, weight="bold", color=NAVY, alpha=after,
                linespacing=1.4)

    ax.plot(roll_x[: n + 1], roll[: n + 1], color=CRIMSON, lw=2.4, solid_capstyle="round")
    ax.plot([head_x], [head_y], "o", ms=8, color=CRIMSON, mec=BG, mew=2, zorder=5)
    if p < 1:
        ax.text(head_x + 0.25, head_y + 7, f"KES {head_y:.0f}", size=12, weight="bold", color=NAVY)
        fig.text(0.94, 0.855, f"{int(head_x)}", size=30, weight="bold", color=NEUTRAL, ha="right")
    else:
        a = ramp(t, 7.2, 0.6)
        ax.plot([roll_x[0]], [roll[0]], "o", ms=8, color=CRIMSON, mec=BG, mew=2, zorder=5, alpha=a)
        ax.text(roll_x[0] + 0.1, roll[0] - 13, f"KES {START:.0f}\nin 2006", size=10.5, color=NAVY,
                weight="bold", alpha=a, va="center", linespacing=1.3)
        ax.text(roll_x[-1] + 0.25, roll[-1], f"KES {END:.0f}\nin 2026", size=10.5, color=NAVY,
                weight="bold", va="center", linespacing=1.3)
        fig.text(0.94, 0.855, f"×{END / START:.1f}", size=30, weight="bold", color=CRIMSON,
                 ha="right", alpha=a)


def scene_2008(fig, t):
    header(fig, "2 OF 4", f"In 2008, food prices jumped {YOY_2008:.0f}% in a single year",
           f"Nearly {YOY_2008 / YOY_2022:.0f}× the jump of the 2022 fuel and fertilizer shock"
           " · year-on-year change in average price per kg", t)
    ax = fig.add_axes([0.06, 0.16, 0.88, 0.56])
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 2)
    ax.axis("off")
    rows = [(1.45, YOY_2008, CRIMSON, "2008", "Post-election crisis", 0.5),
            (0.55, YOY_2022, NAVY, "2022", "Fuel and fertilizer shock", 1.6)]
    for y, val, color, year, name, start in rows:
        g = ramp(t, start, 1.6)
        a = ramp(t, start, 0.4)
        ax.text(0, y + 0.30, year, size=15, weight="bold", color=NAVY, alpha=a, va="center")
        ax.text(5.2, y + 0.30, name, size=11, color=MUTED, alpha=a, va="center")
        ax.barh(y, 55, height=0.34, color=GRID, alpha=a)
        ax.barh(y, val * g, height=0.34, color=color)
        ax.text(val * g + 1, y, f"+{val * g:.0f}%", size=26, weight="bold", color=NAVY,
                va="center", alpha=a)


def scene_counties(fig, t):
    header(fig, "3 OF 4", "The counties that can least afford it pay the most",
           "Average price per kg (KES) by county, 2006–2026 · top 10 are all arid and semi-arid", t)
    ax = fig.add_axes([0.17, 0.10, 0.76, 0.66])
    clean_axes(ax)
    ax.spines["bottom"].set_visible(False)
    ax.set_xlim(0, 142)
    ax.set_ylim(-2.6, 10)
    ax.set_xticks([])
    ax.set_yticks([])
    for i, (name, val) in enumerate(TOP10.items()):
        y = 9.4 - i
        g = ramp(t, 0.5 + 0.22 * i, 0.9)
        a = ramp(t, 0.5 + 0.22 * i, 0.3)
        ax.text(-2, y, name, ha="right", va="center", size=10.5, color=NAVY, alpha=a)
        ax.barh(y, val * g, height=0.66, color=CRIMSON)
        ax.text(val * g + 1.5, y, f"{val * g:.0f}", va="center", size=10, weight="bold",
                color=NAVY, alpha=a)
    a = ramp(t, 4.0, 0.6)
    ax.plot([NATIONAL, NATIONAL], [-2.2, 9.9], color=NAVY, lw=1, ls=(0, (3, 3)), alpha=0.6 * a)
    ax.text(NATIONAL + 1, -2.2, f"All-market average {NATIONAL:.0f}", size=9, color=MUTED,
            alpha=a, va="center")
    g, a = ramp(t, 4.6, 0.9), ramp(t, 4.6, 0.3)
    val = county["Nairobi"]
    ax.text(-2, -0.9, "Nairobi", ha="right", va="center", size=10.5, weight="bold",
            color=NAVY, alpha=a)
    ax.barh(-0.9, val * g, height=0.66, color=NAVY)
    ax.text(val * g + 1.5, -0.9, f"{val * g:.0f}", va="center", size=10, weight="bold",
            color=NAVY, alpha=a)
    ax.text(NATIONAL + 4, -0.9, f"ranks {NAIROBI_RANK}th of {len(county)}", va="center", size=10,
            color=MUTED, alpha=ramp(t, 5.3, 0.5))


def scene_camps(fig, t):
    header(fig, "4 OF 4", f"{N_CAMP} monitored markets sit inside refugee camps",
           "Kakuma, Kalobeyei and Dadaab · each dot is a monitored market, sized by average price", t)
    ax = fig.add_axes([0.04, 0.07, 0.50, 0.70])
    ax.axis("off")
    ax.set_aspect("equal")
    for ring in outline:
        ax.fill(ring[:, 0], ring[:, 1], color="#F4F4F6", ec=NEUTRAL, lw=1.2)
    ax.set_xlim(33.5, 42.3)
    ax.set_ylim(-4.9, 5.3)
    other, camp = mk[~mk.IsRefugeeCamp], mk[mk.IsRefugeeCamp]
    vis = other[other.order < ramp(t, 0.4, 2.2)]
    ax.scatter(vis.Longitude, vis.Latitude, s=vis.avg * 0.32, color=MUTED, alpha=0.55,
               ec=BG, lw=0.5, zorder=3)
    c = ramp(t, 2.8, 0.7)
    if c > 0:
        pulse = 0.5 + 0.5 * np.sin((t - 2.8) * 2 * np.pi / 1.5)
        ax.scatter(camp.Longitude, camp.Latitude, s=camp.avg * (1.6 + 1.6 * pulse), color=CRIMSON,
                   alpha=0.16 * c, lw=0, zorder=4)
        ax.scatter(camp.Longitude, camp.Latitude, s=camp.avg * 0.5 * c, color=CRIMSON,
                   ec=BG, lw=0.8, zorder=5)
        for name, grp in camp.groupby("RefugeeComplex"):
            if name == "Kalobeyei":
                continue
            label = "Kakuma + Kalobeyei" if name == "Kakuma" else name
            x, y = grp.Longitude.mean(), grp.Latitude.mean()
            dx, ha = (0.45, "left") if name == "Kakuma" else (0.5, "left")
            ax.text(x + dx, y + (0.45 if name == "Kakuma" else -0.15), label, size=10.5, weight="bold", color=CRIMSON,
                    alpha=c, ha=ha, zorder=6)
    for i, (val, label, color) in enumerate([
            (CAMP_AVG, "average price per kg\nin refugee camp markets", CRIMSON),
            (OTHER_AVG, "average price per kg\nin all other markets", NAVY)]):
        a = ramp(t, 3.6 + 0.8 * i, 0.9)
        y = 0.58 - i * 0.27
        fig.text(0.60, y, f"KES {val * a:.0f}", size=34, weight="bold", color=color, alpha=a)
        fig.text(0.60, y - 0.10, label, size=11, color=MUTED, alpha=a, linespacing=1.4)
    fig.text(0.60, 0.10, "All foods and all years pooled; camp monitoring\nis recent, so this is "
             "not a like-for-like premium.", size=8.5, color=MUTED, alpha=ramp(t, 5.4, 0.6),
             linespacing=1.4)


def scene_close(fig, t):
    a = ramp(t, 0.1, 0.8)
    fig.add_artist(plt.Rectangle((0.06, 0.80), 0.07 * a, 0.012, color=CRIMSON,
                                 transform=fig.transFigure))
    fig.text(0.06, 0.50, "National averages hide\nwho pays the most.", size=34, weight="bold",
             color=NAVY, alpha=a, linespacing=1.25)
    fig.text(0.06, 0.32, "Kenya Food Prices Dashboard · 20 years, 226 markets, 25 counties",
             size=13, color=MUTED, alpha=ramp(t, 0.8, 0.7))
    fig.text(0.06, 0.25, "Analysis by Jacinta Kamemba · Power BI capstone project", size=11,
             color=MUTED, alpha=ramp(t, 1.2, 0.7))


SCENES = [(scene_title, 3.2), (scene_trend, 11.5), (scene_2008, 5.5),
          (scene_counties, 7.5), (scene_camps, 8.0), (scene_close, 4.0)]


def main():
    total = sum(d for _, d in SCENES)
    tmp = Path(tempfile.mkdtemp(prefix="kfp_frames_"))
    fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor=BG)
    k, elapsed = 0, 0.0
    for scene, dur in SCENES:
        for i in range(int(round(dur * FPS))):
            fig.clf()
            t = i / FPS
            scene(fig, t)
            footer(fig, (elapsed + t) / total)
            fig.savefig(tmp / f"f{k:04d}.png", dpi=DPI, facecolor=BG)
            k += 1
        elapsed += dur
    plt.close(fig)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(tmp / "f%04d.png"),
         "-filter_complex",
         "split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];"
         "[b][p]paletteuse=dither=none:diff_mode=rectangle",
         "-loop", "0", str(OUT)], check=True)
    shutil.rmtree(tmp)
    print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.1f} MB, {k} frames, {total:.0f}s)")


if __name__ == "__main__":
    main()
