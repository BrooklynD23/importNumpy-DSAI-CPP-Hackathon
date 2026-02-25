"""Shared utilities for analysis notebooks: DB connection, plot styling, figure export."""

import json
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import seaborn as sns

# ── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "health.duckdb"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
SYNTHETIC_SIGNATURES_PATH = PROJECT_ROOT / "reports" / "synthetic_signatures.json"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ── Color Constants ──────────────────────────────────────────────────────────
COLOR_RURAL = "#2ecc71"
COLOR_PERIURBAN = "#f39c12"
COLOR_URBAN = "#e74c3c"
COLOR_SEMI_URBAN = "#9b59b6"

TIER_COLORS = {
    "Rural": COLOR_RURAL,
    "Peri-urban": COLOR_PERIURBAN,
    "Urban": COLOR_URBAN,
    "Semi-urban": COLOR_SEMI_URBAN,
}

PALETTE = [COLOR_RURAL, COLOR_PERIURBAN, COLOR_URBAN, COLOR_SEMI_URBAN]


def get_connection() -> duckdb.DuckDBPyConnection:
    """Return a read-only DuckDB connection to the pipeline database."""
    return duckdb.connect(str(DB_PATH), read_only=True)


def load_synthetic_signatures() -> dict:
    """Load reports/synthetic_signatures.json if present (otherwise return {})."""
    if not SYNTHETIC_SIGNATURES_PATH.exists():
        return {}
    return json.loads(SYNTHETIC_SIGNATURES_PATH.read_text(encoding="utf-8"))


def get_robustness_delta(con: duckdb.DuckDBPyConnection, view_name: str):
    """Return the robustness_delta_summary row for a given base view name."""
    return con.execute(
        "SELECT * FROM robustness_delta_summary WHERE view_name = ?",
        [view_name],
    ).fetchdf()


def set_plot_style() -> None:
    """Apply consistent plot styling across all notebooks."""
    sns.set_theme(style="whitegrid", palette=PALETTE)
    plt.rcParams.update({
        "figure.figsize": (10, 6),
        "figure.dpi": 100,
        "savefig.dpi": 300,
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "legend.fontsize": 10,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.bbox": "tight",
    })


def save_fig(fig: plt.Figure, name: str) -> None:
    """Save figure to reports/figures/ as PNG (300dpi) and SVG."""
    fig.savefig(FIGURES_DIR / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIGURES_DIR / f"{name}.svg", bbox_inches="tight")
    print(f"  Saved: {name}.png + {name}.svg")


def effect_size_label(d: float) -> str:
    """Convert Cohen's d to descriptive label."""
    d_abs = abs(d)
    if d_abs < 0.2:
        return "negligible"
    if d_abs < 0.5:
        return "small"
    if d_abs < 0.8:
        return "medium"
    return "large"


def format_ci(mean: float, ci_half: float, as_pct: bool = True) -> str:
    """Format mean with 95% CI as 'X.XX% [lower, upper]'."""
    lo = mean - ci_half
    hi = mean + ci_half
    if as_pct:
        return f"{mean:.2f}% [{lo:.2f}, {hi:.2f}]"
    return f"{mean:.4f} [{lo:.4f}, {hi:.4f}]"
