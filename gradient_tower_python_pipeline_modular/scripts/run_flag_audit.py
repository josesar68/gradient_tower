
from __future__ import annotations

import argparse
import sys
from pathlib import Path
#

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run audited QC flag workflow.")
    parser.add_argument("--nc-file", default=r"D:\OneDrive\PAPER_GRADIENT_TOWER\PYTHON\data_nc\OGHYO_GradientTower_Dataset_2018_2026.nc")
    parser.add_argument("--out-dir", default=r"D:\OneDrive\Documentos\New project\gradient_tower_python_pipeline_modular\output_df")
    parser.add_argument("--figures-dir", default=r"D:\OneDrive\PAPER_GRADIENT_TOWER\LATEX\graphics")
    parser.add_argument("--source", choices=["raw", "cleaned"], default="raw")
    parser.add_argument("--top-k-combos", type=int, default=15)
    parser.add_argument("--save-figures", action="store_true")
    parser.add_argument("--availability-threshold", type=float, default=0.80)
    parser.add_argument("--top-n-columns", type=int, default=None)
    parser.add_argument("--dpi", type=int, default=300)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    from gradient_tower_pipeline.flag_audit import (
        audit_data_availability,
        make_default_tower_config,
        print_qc_audit_report,
        print_workflow_summary,
        run_full_qc_audit_workflow,
        save_reconstructed_dataframes_pickle,
    )
    from gradient_tower_pipeline.qc_audit_figures import (
        QCAuditFigureConfig,
        audit_qc_audit_figure_outputs,
        generate_qc_audit_publication_figures,
    )

    cfg = make_default_tower_config()
    results = run_full_qc_audit_workflow(
        nc_file=args.nc_file,
        cfg=cfg,
        audit_data_source=args.source,
        top_k_combos=args.top_k_combos,
    )
    print_workflow_summary(results)
    print_qc_audit_report(
        results["per_col_cells"],
        results["per_flag_rows"],
        results["combos"],
        results["diagnostics"],
    )
    availability = audit_data_availability(results["cleaned_from_nc"], cfg, threshold=0.8)
    print(availability)
    outputs = save_reconstructed_dataframes_pickle(
        cleaned_from_nc=results["cleaned_from_nc"],
        flags_from_nc=results["flags_from_nc"],
        raw_from_nc=results["raw_from_nc"],
        out_dir=args.out_dir,
    )
    print(outputs)

    if args.save_figures:
        figure_cfg = QCAuditFigureConfig(
            out_dir=args.figures_dir,
            availability_threshold=args.availability_threshold,
            dpi=args.dpi,
            top_n_columns=args.top_n_columns,
        )
        figure_paths = generate_qc_audit_publication_figures(
            results,
            cfg=cfg,
            figure_cfg=figure_cfg,
        )
        print("\n=== QC AUDIT FIGURES SAVED ===")
        for name, path in figure_paths.items():
            print(f"{name}: {path}")
        print("\n=== QC AUDIT FIGURE OUTPUT CHECK ===")
        print(audit_qc_audit_figure_outputs(figure_cfg).to_string(index=False))


if __name__ == "__main__":
    main()
