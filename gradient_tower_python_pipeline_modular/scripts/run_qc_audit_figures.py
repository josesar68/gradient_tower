from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate autonomous QC audit publication figures.")
    parser.add_argument(
        "--nc-file",
        default=r"D:\OneDrive\PAPER_GRADIENT_TOWER\PYTHON\data_nc\OGHYO_GradientTower_Dataset_2018_2026.nc",
    )
    parser.add_argument(
        "--out-dir",
        default=r"D:\OneDrive\PAPER_GRADIENT_TOWER\LATEX\graphics",
    )
    parser.add_argument("--source", choices=["raw", "cleaned"], default="raw")
    parser.add_argument("--top-k-combos", type=int, default=15)
    parser.add_argument("--top-n-columns", type=int, default=None)
    parser.add_argument("--availability-threshold", type=float, default=0.80)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--include-wdir", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    from gradient_tower_pipeline.flag_audit import make_default_tower_config
    from gradient_tower_pipeline.qc_audit_figures import (
        QCAuditFigureConfig,
        audit_qc_audit_figure_outputs,
        run_qc_audit_figure_workflow,
    )

    cfg = make_default_tower_config()
    figure_cfg = QCAuditFigureConfig(
        out_dir=args.out_dir,
        availability_threshold=args.availability_threshold,
        dpi=args.dpi,
        top_n_columns=args.top_n_columns,
    )
    results = run_qc_audit_figure_workflow(
        args.nc_file,
        cfg=cfg,
        figure_cfg=figure_cfg,
        audit_data_source=args.source,
        include_wdir=args.include_wdir,
        top_k_combos=args.top_k_combos,
    )

    print("\n=== QC AUDIT FIGURES SAVED ===")
    for name, path in results["qc_audit_figure_paths"].items():
        print(f"{name}: {path}")

    print("\n=== QC AUDIT FIGURE OUTPUT CHECK ===")
    print(audit_qc_audit_figure_outputs(figure_cfg).to_string(index=False))


if __name__ == "__main__":
    main()
