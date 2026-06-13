from __future__ import annotations

"""Autonomous QC-audit figure generation for the gradient tower pipeline."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import PercentFormatter

from .flag_audit import (
    FLAG_ORDER,
    TowerConfig,
    make_default_tower_config,
    plot_diurnal_science_ready_with_wdir,
    run_full_qc_audit_workflow,
)


@dataclass
class QCAuditFigureConfig:
    """Output and style settings for QC-audit publication figures."""

    out_dir: str | Path = "figures_qc"
    availability_threshold: float = 0.80
    composition_filename: str = "qc_flags_composition_ranked.png"
    outcome_filename: str = "bars_qc_outcome_stacked_100pct.png"
    diurnal_filename: str = "diurnal_cycle_validated_with_wdir.png"
    dpi: int = 300
    top_n_columns: Optional[int] = None


FLAG_COLORS: Dict[str, str] = {
    "CALM": "#56B4E9",
    "PERSIST": "#0072B2",
    "SPIKE": "#E69F00",
    "STEP": "#D55E00",
    "RANGE": "#CC79A7",
    "MISSING": "#7F858C",
    "INCONSIST": "#F0E442",
    "RESAMPLE": "#BDBDBD",
}


def _prepare_ranked_columns(per_col_cells: pd.DataFrame, top_n: Optional[int]) -> pd.DataFrame:
    if "ANY_pct" not in per_col_cells.columns:
        raise ValueError("per_col_cells must include ANY_pct.")

    ranked = per_col_cells.copy().sort_values("ANY_pct", ascending=False)
    if top_n is not None:
        ranked = ranked.head(int(top_n))
    return ranked


def _scaled_flag_percentages(ranked: pd.DataFrame, flag_names: list[str]) -> pd.DataFrame:
    """
    Scale overlapping flag percentages so each stacked bar sums to ANY_pct.

    QC bits are not mutually exclusive. Directly stacking bit percentages can
    exceed the total contaminated fraction, so this keeps the composition shape
    while preserving the correct total height.
    """

    raw = pd.DataFrame(
        {name: ranked[f"{name}_pct"].fillna(0.0).clip(lower=0.0) for name in flag_names},
        index=ranked.index,
    )
    totals = raw.sum(axis=1).replace(0.0, np.nan)
    any_pct = ranked["ANY_pct"].fillna(0.0).clip(lower=0.0)
    scaled = raw.div(totals, axis=0).mul(any_pct, axis=0).fillna(0.0)
    return scaled


def plot_qc_flags_composition_ranked(
    per_col_cells: pd.DataFrame,
    *,
    save_path: str | Path,
    top_n: Optional[int] = None,
    dpi: int = 300,
) -> Path:
    """Plot ranked QC flag composition by sensor column."""

    ranked = _prepare_ranked_columns(per_col_cells, top_n)
    flag_names = [name for name, _ in FLAG_ORDER if f"{name}_pct" in ranked.columns]
    x = np.arange(len(ranked))

    fig, ax = plt.subplots(figsize=(14, 7))
    bottom = np.zeros(len(ranked), dtype=float)

    preferred_order = ["CALM", "PERSIST", "SPIKE", "STEP", "RANGE", "MISSING", "INCONSIST", "RESAMPLE"]
    flag_names = [name for name in preferred_order if name in flag_names]
    scaled_flags = _scaled_flag_percentages(ranked, flag_names)
    for name in flag_names:
        values = scaled_flags[name].to_numpy(dtype=float)
        ax.bar(
            x,
            values,
            bottom=bottom,
            color=FLAG_COLORS.get(name, "#999999"),
            edgecolor="white",
            linewidth=0.6,
            label=name,
        )
        bottom += values

    any_pct = ranked["ANY_pct"].fillna(0.0).to_numpy(dtype=float)
    ax.plot(x, any_pct, color="black", marker="o", linewidth=2.2, label="ANY (Total Contamination %)")
    for xi, yi in zip(x, any_pct):
        ax.text(xi, yi + 1.2, f"{yi:.1f}%", ha="center", va="bottom", fontsize=14, fontweight="bold")

    ax.set_ylabel("% of Data (Scaled Composition)", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(ranked.index.astype(str), rotation=45, ha="right")
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))
    ax.grid(True, axis="y", linestyle="--", alpha=0.35)
    ax.set_ylim(0, max(45.0, float(np.nanmax(bottom)) * 1.12 if len(bottom) else 45.0))
    ax.tick_params(axis='both', which='major', labelsize=15, length=5, width=1.0)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=5, frameon=False,fontsize=16)
    fig.tight_layout()

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return save_path


def plot_qc_outcome_stacked_100pct(
    per_col_cells: pd.DataFrame,
    *,
    save_path: str | Path,
    top_n: Optional[int] = None,
    dpi: int = 300,
) -> Path:
    """Plot clean/contaminated/hard-fail QC outcome as 100% stacked bars."""

    ranked = _prepare_ranked_columns(per_col_cells, top_n)
    x = np.arange(len(ranked))
    any_pct = ranked["ANY_pct"].fillna(0.0).clip(lower=0.0, upper=100.0)
    hard_pct = ranked.get("HARD_FAIL_pct", pd.Series(0.0, index=ranked.index)).fillna(0.0).clip(lower=0.0, upper=100.0)
    contaminated_pct = (any_pct - hard_pct).clip(lower=0.0, upper=100.0)
    clean_pct = (100.0 - any_pct).clip(lower=0.0, upper=100.0)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.bar(x, hard_pct, color="#D55E00", edgecolor="white", linewidth=0.6, label="HARD FAIL (Removed)")
    ax.bar(x, contaminated_pct, bottom=hard_pct, color="#EAC625", edgecolor="white", linewidth=0.6, label="CONTAMINATED (Soft/Contextual Flag, Retained)")
    ax.bar(x, clean_pct, bottom=hard_pct + contaminated_pct, color="#009E73", edgecolor="white", linewidth=0.6, label="CLEAN (Unflagged, Retained)")

    for xi, hard, cont, clean, any_value in zip(x, hard_pct, contaminated_pct, clean_pct, any_pct):
        if any_value >= 1.0:
            ax.text(xi, max(hard + cont / 2, 1.5), f"{any_value:.1f}%", ha="center", va="center", fontsize=14,
                    bbox=dict(facecolor="white", alpha=0.75, edgecolor="none", pad=1.5))
        if clean >= 5.0:
            ax.text(xi, hard + cont + clean / 2, f"{clean:.1f}%", ha="center", va="center", fontsize=14,
                    bbox=dict(facecolor="white", alpha=0.55, edgecolor="none", pad=1.5))

    ax.set_title(
        "Data Quality Outcome by Sensor Column (% 100 Stacked Bar)\n"
        "Sorted by contamination (ANY_pct descending)",
        fontweight="bold",
    )
    ax.set_ylabel("% of Data Considered", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(ranked.index.astype(str), rotation=45, ha="right")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))
    ax.grid(True, axis="y", linestyle="--", alpha=0.35)
    ax.tick_params(axis='both', which='major', labelsize=15, length=5, width=1.0)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3, frameon=False,fontsize=16)
    fig.tight_layout()

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return save_path


def expected_qc_audit_figure_paths(
    figure_cfg: Optional[QCAuditFigureConfig] = None,
) -> Dict[str, Path]:
    """Return expected output paths for the standard QC-audit figures."""

    if figure_cfg is None:
        figure_cfg = QCAuditFigureConfig()
    out_dir = Path(figure_cfg.out_dir)
    return {
        "qc_flags_composition_ranked": out_dir / figure_cfg.composition_filename,
        "bars_qc_outcome_stacked_100pct": out_dir / figure_cfg.outcome_filename,
        "diurnal_cycle_validated_with_wdir": out_dir / figure_cfg.diurnal_filename,
    }


def audit_qc_audit_figure_outputs(
    figure_cfg: Optional[QCAuditFigureConfig] = None,
) -> pd.DataFrame:
    """Audit whether the expected QC-audit figure files exist on disk."""

    rows = []
    for name, path in expected_qc_audit_figure_paths(figure_cfg).items():
        rows.append({
            "figure": name,
            "path": str(path),
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0,
            "status": "PASS" if path.exists() and path.stat().st_size > 0 else "FAIL",
        })
    return pd.DataFrame(rows)


def generate_qc_audit_publication_figures(
    results: Dict[str, Any],
    *,
    cfg: Optional[TowerConfig] = None,
    figure_cfg: Optional[QCAuditFigureConfig] = None,
) -> Dict[str, Path]:
    """Generate the standard QC audit figures from workflow results."""

    if cfg is None:
        cfg = results.get("cfg") or make_default_tower_config()
    if figure_cfg is None:
        figure_cfg = QCAuditFigureConfig()

    out_dir = Path(figure_cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    per_col_cells = results["per_col_cells"]
    cleaned_from_nc = results["cleaned_from_nc"]

    paths = {
        "qc_flags_composition_ranked": plot_qc_flags_composition_ranked(
            per_col_cells,
            save_path=out_dir / figure_cfg.composition_filename,
            top_n=figure_cfg.top_n_columns,
            dpi=figure_cfg.dpi,
        ),
        "bars_qc_outcome_stacked_100pct": plot_qc_outcome_stacked_100pct(
            per_col_cells,
            save_path=out_dir / figure_cfg.outcome_filename,
            top_n=figure_cfg.top_n_columns,
            dpi=figure_cfg.dpi,
        ),
    }

    diurnal_path = out_dir / figure_cfg.diurnal_filename
    plot_diurnal_science_ready_with_wdir(
        cleaned_from_nc,
        cfg,
        threshold=figure_cfg.availability_threshold,
        save_path=str(diurnal_path),
    )
    paths["diurnal_cycle_validated_with_wdir"] = diurnal_path

    audit = audit_qc_audit_figure_outputs(figure_cfg)
    failed = audit[audit["status"] != "PASS"]
    if not failed.empty:
        raise IOError(
            "Some QC audit figures were not created correctly:\n"
            + failed.to_string(index=False)
        )

    return paths


def run_qc_audit_figure_workflow(
    nc_file: str | Path,
    *,
    cfg: Optional[TowerConfig] = None,
    figure_cfg: Optional[QCAuditFigureConfig] = None,
    audit_data_source: str = "raw",
    include_wdir: bool = False,
    top_k_combos: int = 15,
) -> Dict[str, Any]:
    """Run QC audit from NetCDF and save the standard QC-audit figures."""

    if cfg is None:
        cfg = make_default_tower_config()
    if figure_cfg is None:
        figure_cfg = QCAuditFigureConfig()

    results = run_full_qc_audit_workflow(
        nc_file=str(nc_file),
        cfg=cfg,
        include_wdir=include_wdir,
        audit_data_source=audit_data_source,  # type: ignore[arg-type]
        top_k_combos=top_k_combos,
    )
    figure_paths = generate_qc_audit_publication_figures(
        results,
        cfg=cfg,
        figure_cfg=figure_cfg,
    )
    results["qc_audit_figure_paths"] = figure_paths
    return results
