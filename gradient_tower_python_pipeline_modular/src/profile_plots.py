from __future__ import annotations
#

"""Vertical profile figure orchestration for the gradient tower pipeline."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from .flag_audit import (
    TowerConfig,
    make_default_tower_config,
    plot_seasonal_vertical_profiles_publication,
    plot_seasonal_wind_profiles_publication,
)


@dataclass
class VerticalProfileFigureConfig:
    """Configuration for audited vertical profile figures."""

    out_dir: str | Path = "figures_vertical_profiles"
    min_availability: float = 0.80
    generate_thermodynamic_profiles: bool = True
    generate_wind_profiles: bool = True
    thermodynamic_prefix: str = "seasonal_profile"
    wind_prefix: str = "seasonal_wind"


def _profile_column_groups(cfg: TowerConfig) -> Dict[str, List[str]]:
    heights = cfg.heights_m
    suffixes = [str(int(h)) if float(h).is_integer() else str(h).replace(".", "p") for h in heights]
    return {
        "temperature": [cfg.temp_cols[h] for h in heights if h in cfg.temp_cols],
        "relative_humidity": [cfg.rh_cols[h] for h in heights if h in cfg.rh_cols],
        "wind_speed": [cfg.wind_cols[h] for h in heights if h in cfg.wind_cols],
        "wind_direction": [col for col in cfg.wdir_cols.values()],
        "virtual_potential_temperature": [f"theta_v_{suffix}" for suffix in suffixes],
        "specific_humidity": [f"q_{suffix}" for suffix in suffixes],
    }


def audit_vertical_profile_inputs(
    df: pd.DataFrame,
    cfg: Optional[TowerConfig] = None,
    min_availability: float = 0.80,
) -> pd.DataFrame:
    """
    Check whether a DataFrame can support the audited vertical profile figures.

    The thermodynamic figure can still run if derived ``theta_v_*`` or ``q_*``
    columns are incomplete, but the audit reports that limitation explicitly.
    """

    if cfg is None:
        cfg = make_default_tower_config()

    rows = []
    for group, cols in _profile_column_groups(cfg).items():
        present = [col for col in cols if col in df.columns]
        missing = [col for col in cols if col not in df.columns]
        if present and len(df) > 0:
            min_valid_fraction = float(df[present].notna().mean().min())
        else:
            min_valid_fraction = 0.0
        status = "PASS"
        if missing:
            status = "WARN"
        if present and min_valid_fraction < min_availability:
            status = "WARN"
        rows.append({
            "group": group,
            "required_columns": len(cols),
            "present_columns": len(present),
            "min_valid_fraction": min_valid_fraction,
            "min_availability_required": float(min_availability),
            "missing_columns": missing,
            "status": status,
        })

    if not isinstance(df.index, pd.DatetimeIndex):
        rows.append({
            "group": "datetime_index",
            "required_columns": 0,
            "present_columns": 0,
            "min_valid_fraction": 0.0,
            "min_availability_required": float(min_availability),
            "missing_columns": ["DatetimeIndex"],
            "status": "FAIL",
        })
    else:
        rows.append({
            "group": "datetime_index",
            "required_columns": 0,
            "present_columns": 1,
            "min_valid_fraction": 1.0,
            "min_availability_required": float(min_availability),
            "missing_columns": [],
            "status": "PASS",
        })

    return pd.DataFrame(rows)


def _expected_profile_paths(out_dir: Path, cfg: VerticalProfileFigureConfig) -> Dict[str, Path]:
    return {
        "thermodynamic_dry": out_dir / f"{cfg.thermodynamic_prefix}_dry_season.png",
        "thermodynamic_wet": out_dir / f"{cfg.thermodynamic_prefix}_wet_season.png",
        "wind_dry": out_dir / f"{cfg.wind_prefix}_dry_season.png",
        "wind_wet": out_dir / f"{cfg.wind_prefix}_wet_season.png",
    }


def run_vertical_profile_figure_workflow(
    df: pd.DataFrame,
    *,
    tower_cfg: Optional[TowerConfig] = None,
    figure_cfg: Optional[VerticalProfileFigureConfig] = None,
    strict: bool = False,
) -> Tuple[pd.DataFrame, Dict[str, Path]]:
    """
    Generate audited seasonal vertical profile figures from an existing DataFrame.

    Parameters
    ----------
    df
        Cleaned or original reconstructed tower DataFrame. It must use a
        DatetimeIndex and include the mapped tower columns.
    tower_cfg
        Tower column mapping. Defaults to the audited flag-audit configuration.
    figure_cfg
        Output and selection options for the figures.
    strict
        If True, raise an error when any input audit row is not PASS.
    """

    if tower_cfg is None:
        tower_cfg = make_default_tower_config()
    if figure_cfg is None:
        figure_cfg = VerticalProfileFigureConfig()

    out_dir = Path(figure_cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    audit = audit_vertical_profile_inputs(
        df,
        tower_cfg,
        min_availability=figure_cfg.min_availability,
    )
    failed = audit[audit["status"] == "FAIL"]
    warnings = audit[audit["status"] != "PASS"]
    if not failed.empty or (strict and not warnings.empty):
        raise ValueError(
            "The vertical profile input DataFrame did not pass validation:\n"
            + warnings.to_string(index=False)
        )

    paths = _expected_profile_paths(out_dir, figure_cfg)

    if figure_cfg.generate_thermodynamic_profiles:
        plot_seasonal_vertical_profiles_publication(
            df,
            tower_cfg,
            save_prefix=str(out_dir / figure_cfg.thermodynamic_prefix),
        )

    if figure_cfg.generate_wind_profiles:
        plot_seasonal_wind_profiles_publication(
            df,
            tower_cfg,
            save_prefix=str(out_dir / figure_cfg.wind_prefix),
        )

    return audit, paths
