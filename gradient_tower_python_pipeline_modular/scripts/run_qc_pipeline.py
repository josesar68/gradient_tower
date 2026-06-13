
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
    parser = argparse.ArgumentParser(description="Run audited Gradient Tower QC pipeline.")
    parser.add_argument("--base-dir", default=r"D:\OneDrive\PAPER_GRADIENT_TOWER\PYTHON")
    parser.add_argument("--temp-calib", default="calib_txt/matrix_temp_met.dat")
    parser.add_argument("--rh-calib", default="calib_txt/matrix_relhum_met.dat")
    parser.add_argument("--tower-mat", default="input_mat/var_torre_30m_20180515_20260331.mat")
    parser.add_argument("--sun-mat", default="input_mat/sun_position_20180515_20260331.mat")
    parser.add_argument("--output-netcdf", default="data_nc/OGHYO_GradientTower_Dataset_2018_2026.nc")
    parser.add_argument("--no-netcdf", action="store_true")
    parser.add_argument("--non-strict-columns", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    from gradient_tower_pipeline.qc_pipeline import TowerConfig, run_full_qc_pipeline

    base = Path(args.base_dir)
    cfg = TowerConfig(strict_columns=not args.non_strict_columns)
    raw_prepared, cleaned, flags, summary, missing_summary = run_full_qc_pipeline(
        temp_calib_file=base / args.temp_calib,
        rh_calib_file=base / args.rh_calib,
        tower_mat_file=base / args.tower_mat,
        sun_mat_file=base / args.sun_mat,
        output_netcdf=base / args.output_netcdf,
        cfg=cfg,
        export_netcdf=not args.no_netcdf,
    )
    print("QC completado")
    print(f"raw_prepared={raw_prepared.shape} cleaned={cleaned.shape} flags={flags.shape}")
    print(summary)
    print(missing_summary.head())


if __name__ == "__main__":
    main()
