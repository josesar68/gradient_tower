
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
    #

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run calibrated audited BRN/MOST flux pipeline.")
    parser.add_argument("--nc-file", default=r"D:\OneDrive\PAPER_GRADIENT_TOWER\PYTHON\data_nc\OGHYO_GradientTower_Dataset_2018_2026.nc")
    parser.add_argument("--output-nc", default=r"D:\OneDrive\PAPER_GRADIENT_TOWER\PYTHON\data_nc\OGHYO_30min_Fluxes_2018_2026.nc")
    parser.add_argument("--minute-output-nc", default=r"D:\OneDrive\PAPER_GRADIENT_TOWER\PYTHON\data_nc\OGHYO_Minute_Fluxes_2018_2026.nc")
    parser.add_argument("--mode", choices=["minute", "30min", "all"], default="30min")
    parser.add_argument("--no-progress", action="store_true")
    parser.add_argument("--save-minute-netcdf", action="store_true")
    parser.add_argument("--save-30min-netcdf", action="store_true")
    parser.add_argument("--save-minute-figures", action="store_true")
    parser.add_argument("--save-30min-figures", action="store_true")
    parser.add_argument("--minute-figures-dir", default=r"D:\OneDrive\PAPER_GRADIENT_TOWER\PYTHON\figures_flux_minute")
    parser.add_argument("--figures-30min-dir", default=r"D:\OneDrive\PAPER_GRADIENT_TOWER\PYTHON\figures_flux_30min")
    parser.add_argument("--figures-start", default=None)
    parser.add_argument("--figures-end", default=None)
    parser.add_argument("--no-30min-distribution-stats", action="store_true")
    parser.add_argument("--lower-quantile", type=float, default=0.01)
    parser.add_argument("--upper-quantile", type=float, default=0.99)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    from gradient_tower_pipeline.flux_pipeline import (
        Flux30MinConfig,
        FluxConfig,
        generate_flux_figures_and_statistics,
        generate_minute_flux_figures_and_statistics,
        read_saved_tower_dataframes_from_netcdf,
        run_30min_flux_pipeline,
        run_minute_flux_pipeline,
        save_30min_energy_fluxes_to_netcdf,
        save_minute_energy_fluxes_to_netcdf,
    )

    cleaned, flags, raw, ds, ds_raw = read_saved_tower_dataframes_from_netcdf(args.nc_file)
    print(f"Datos reconstruidos: cleaned={cleaned.shape}, flags={flags.shape}, raw={None if raw is None else raw.shape}")

    if args.mode in {"minute", "all"}:
        cfg_min = FluxConfig(progress=not args.no_progress)
        flux_minute, summary_minute = run_minute_flux_pipeline(cleaned, cfg_min, verbose=True)
        print(f"Flujos minuto: {flux_minute.shape}")
        print(summary_minute)
        if args.save_minute_netcdf:
            output_nc_minute, ds_flux_minute, audit_flux_minute, name_map_minute = save_minute_energy_fluxes_to_netcdf(
                flux_minute,
                output_nc=args.minute_output_nc,
                cfg=cfg_min,
                report={"summary": summary_minute} if summary_minute is not None else None,
                overwrite=True,
            )
            print(f"NetCDF minuto guardado: {output_nc_minute}")
        if args.save_minute_figures:
            summary_stats_minute, comparison_stats_minute = generate_minute_flux_figures_and_statistics(
                flux_minute,
                out_dir=args.minute_figures_dir,
                start=args.figures_start,
                end=args.figures_end,
                title_prefix="Minute ",
            )
            print(f"Figuras minuto guardadas en: {args.minute_figures_dir}")
            print(summary_stats_minute)
            print(comparison_stats_minute)

    if args.mode in {"30min", "all"}:
        cfg30 = Flux30MinConfig(
            progress=not args.no_progress,
            include_distribution_stats=not args.no_30min_distribution_stats,
            lower_quantile=args.lower_quantile,
            upper_quantile=args.upper_quantile,
        )
        flux30, report30 = run_30min_flux_pipeline(cleaned, cfg30, verbose=True)
        print(f"Flujos 30 min: {flux30.shape}")
        for key in ["summary", "paired_comparison", "coherence_audit"]:
            if key in report30:
                print(f"\n=== {key} ===")
                print(report30[key])
        if args.save_30min_netcdf:
            output_nc, ds_flux, audit_flux, name_map = save_30min_energy_fluxes_to_netcdf(
                flux30,
                output_nc=args.output_nc,
                cfg=cfg30,
                report=report30,
                overwrite=True,
                )
            print(f"NetCDF guardado: {output_nc}")
        if args.save_30min_figures:
            summary_stats_30m, comparison_stats_30m = generate_flux_figures_and_statistics(
                flux30,
                out_dir=args.figures_30min_dir,
                start=args.figures_start,
                end=args.figures_end,
                title_prefix="30-min ",
            )
            print(f"Figuras 30 min guardadas en: {args.figures_30min_dir}")
            print(summary_stats_30m)
            print(comparison_stats_30m)


if __name__ == "__main__":
    main()
