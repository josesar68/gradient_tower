# Gradient Tower Python Pipeline

Modular Python pipeline for processing OGHYO gradient tower observations, including quality-control auditing, calibrated meteorological data reconstruction, MOST and BRN-based turbulent energy flux estimation, NetCDF export, and publication-ready diagnostic figures.

The code was refactored from audited research notebooks into reusable modules, command-line scripts, and a main orchestration notebook. It is designed for micrometeorological gradient-tower datasets with multi-level wind speed, temperature, humidity, pressure, and quality-control flags.

## Main Capabilities

- Reconstruct cleaned tower DataFrames from calibrated tower datasets.
- Apply input quality control before flux calculations.
- Estimate turbulent energy fluxes using:
  - MOST: Monin-Obukhov Similarity Theory.
  - BRN_ANC: Bulk Richardson Number anchored method.
- Produce fluxes at:
  - 1-minute resolution.
  - 30-minute resolution.
- Export QC and flux products to NetCDF.
- Save audit tables as CSV and, where enabled, as NetCDF groups.
- Generate diagnostic and publication figures:
  - Time series of `QH`, `QE`, and `u_star`.
  - MOST vs BRN comparison scatter plots.
  - Mean diurnal cycles.
  - Seasonal dry/wet diurnal cycles.
  - QC flag distributions.
  - QC flag diurnal cycles by half-hour of the day.
  - Vertical thermodynamic and wind profiles.
  - QC audit figures for publication.

## Repository Structure

```text
gradient_tower_python_pipeline_modular/
+-- notebooks/
|   +-- MAIN_GRADIENT_TOWER_PIPELINE_AUDITED.ipynb
+-- scripts/
|   +-- run_qc_pipeline.py
|   +-- run_flux_pipeline.py
|   +-- run_flag_audit.py
|   +-- run_qc_audit_figures.py
+-- src/
|   +-- gradient_tower_pipeline/
|       +-- qc_pipeline.py
|       +-- flux_pipeline.py
|       +-- flag_audit.py
|       +-- profile_plots.py
|       +-- qc_audit_figures.py
+-- reports/
+-- graphics/
+-- output_df/
+-- requirements.txt
+-- README.md
```

## Core Modules

### `qc_pipeline.py`

Handles the main meteorological QC stage:

- Reads calibration matrices.
- Reads original tower and solar-position `.mat` files.
- Applies calibration and physical QC.
- Builds cleaned variables and QC flags.
- Exports the audited tower dataset to NetCDF.

Main entry point:

```python
run_full_qc_pipeline(...)
```

### `flux_pipeline.py`

Handles the turbulent flux workflow:

- Reconstructs DataFrames from saved QC NetCDF files.
- Computes 1-minute and 30-minute fluxes.
- Applies pre-QC and post-QC.
- Produces MOST and BRN_ANC flux estimates.
- Saves flux NetCDF files.
- Generates flux figures and audit tables.

Main entry points:

```python
read_saved_tower_dataframes_from_netcdf(...)
run_minute_flux_pipeline(...)
run_30min_flux_pipeline(...)
save_minute_energy_fluxes_to_netcdf(...)
save_30min_energy_fluxes_to_netcdf(...)
generate_flux_figures_and_statistics(...)
plot_seasonal_diurnal_fluxes(...)
plot_qc_flag_diurnal_cycles(...)
```

### `flag_audit.py`

Provides independent audit tools for QC flags and data availability:

- Availability summaries.
- Sensor-level flag audits.
- Diurnal atmospheric cycles.
- Seasonal vertical profiles.
- QC composition summaries.

Main entry points:

```python
run_full_qc_audit_workflow(...)
audit_data_availability(...)
save_reconstructed_dataframes_pickle(...)
```

### `profile_plots.py`

Wraps seasonal vertical profile plotting into a standalone workflow.

Main entry point:

```python
run_vertical_profile_figure_workflow(...)
```

### `qc_audit_figures.py`

Generates publication-ready QC audit figures, including:

- Ranked QC flag composition.
- 100% stacked data-quality outcome bars.
- Validated dry/wet atmospheric diurnal cycles.

Main entry point:

```python
generate_qc_audit_publication_figures(...)
```

## Installation

Create and activate a Python environment, then install dependencies:

```powershell
cd "D:\OneDrive\PAPER_GRADIENT_TOWER\gradient_tower_python_pipeline_modular"
pip install -r requirements.txt
```

The project uses common scientific Python libraries such as:

- `numpy`
- `pandas`
- `xarray`
- `scipy`
- `matplotlib`
- `netCDF4`
- `tqdm`

## Recommended Execution Modes

You can run the workflow either from the main notebook or from command-line scripts.

### Option 1: Main Notebook

Open:

```text
notebooks/MAIN_GRADIENT_TOWER_PIPELINE_AUDITED.ipynb
```

The notebook is organized into independent blocks that can be run step by step:

0. Project routes.
1. Single import block for libraries and project functions.
2. Central execution configuration.
3. QC block: regenerate the main tower NetCDF.
4. Loading block: rebuild DataFrames from `QC_NETCDF`.
5. Calculation block: compute minute and 30-minute fluxes.
6. Save block: export minute and 30-minute flux NetCDF files.
7. Flux graphics block.
8. Vertical profile graphics block.
9. QC audit and QC publication figure block.
10. Final audit of expected products.
11. Optional integrated execution with `run_complete_pipeline()`.

The recommended workflow is to run blocks 0-10 interactively. Block 11 is an optional wrapper for users who want a single function call after the configuration is already set.

The graphics block can be executed without recalculating fluxes if the saved flux NetCDF files already exist. Run blocks 0, 1, and 2 first, then run block 7. If `pipeline_results` is not already present, the notebook rebuilds it from `MINUTE_FLUX_NETCDF` and `FLUX_NETCDF`.

Important notebook control flags are configured in block 2:

```python
RUN_REGENERATE_QC = True
RUN_LOAD_QC_NETCDF = True
RUN_MINUTE = True
RUN_30MIN = True

INCLUDE_30MIN_DISTRIBUTION_STATS = True
LOWER_30MIN_QUANTILE = 0.01
UPPER_30MIN_QUANTILE = 0.99

SAVE_MINUTE_NETCDF = True
SAVE_30MIN_NETCDF = True
DROP_MINUTE_TEXT_LABELS = True
DROP_30MIN_TEXT_LABELS = True
VERIFY_NETCDF = True

SAVE_MINUTE_FIGURES = True
SAVE_30MIN_FIGURES = True
SAVE_SEASONAL_DIURNAL_FLUX_FIGURES = True

RUN_VERTICAL_PROFILES = True
RUN_QC_AUDIT = True
RUN_QC_AUDIT_FIGURES = True
```

### Option 2: Command-Line Scripts

Run the QC pipeline:

```powershell
python scripts\run_qc_pipeline.py
```

Run 30-minute fluxes:

```powershell
python scripts\run_flux_pipeline.py --mode 30min --save-30min-netcdf --save-30min-figures
```

Run minute fluxes:

```powershell
python scripts\run_flux_pipeline.py --mode minute --save-minute-netcdf --save-minute-figures
```

Run both minute and 30-minute workflows:

```powershell
python scripts\run_flux_pipeline.py --mode all --save-minute-netcdf --save-30min-netcdf --save-minute-figures --save-30min-figures
```

Run the QC audit:

```powershell
python scripts\run_flag_audit.py --save-figures
```

Generate only QC audit figures:

```powershell
python scripts\run_qc_audit_figures.py
```

## Default Inputs

The default paths assume the following project layout:

```text
D:\OneDrive\PAPER_GRADIENT_TOWER\
+-- PYTHON\
|   +-- calib_txt\
|   |   +-- matrix_temp_met.dat
|   |   +-- matrix_relhum_met.dat
|   +-- input_mat\
|   |   +-- var_torre_30m_20180515_20260430.mat
|   |   +-- sun_position_20180515_20260430.mat
|   +-- data_nc\
|   |   +-- OGHYO_GradientTower_Dataset_2018_2026.nc
|   |   +-- OGHYO_Minute_Fluxes_2018_2026.nc
|   |   +-- OGHYO_30min_Fluxes_2018_2026.nc
+-- LATEX\
|   +-- graphics\
|       +-- figures_flux_minute\
|       +-- figures_flux_30min\
|       +-- figures_flux_seasonal_diurnal\
+-- gradient_tower_python_pipeline_modular\
```

## Output Products

### NetCDF Outputs

By default, the pipeline writes:

```text
PYTHON/data_nc/OGHYO_GradientTower_Dataset_2018_2026.nc
PYTHON/data_nc/OGHYO_Minute_Fluxes_2018_2026.nc
PYTHON/data_nc/OGHYO_30min_Fluxes_2018_2026.nc
```

Each flux NetCDF may also generate:

```text
*.audit.csv
*.column_name_map.csv
```

### Flux Figures

For 30-minute fluxes:

```text
LATEX/graphics/figures_flux_30min/
```

For minute fluxes:

```text
LATEX/graphics/figures_flux_minute/
```

For seasonal dry/wet flux cycles:

```text
LATEX/graphics/figures_flux_seasonal_diurnal/
```

The command-line scripts may still be configured to write figures under `PYTHON/figures_*` depending on the arguments used. The main notebook currently writes flux figures under `LATEX_GRAPHICS_DIR` by default.

### QC Audit And Publication Figures

By default:

```text
LATEX/graphics/
```

## Adapting The Pipeline To A Different Dataset

This is the most important section if you want to reuse the code with a different tower, time period, file structure, or sensor naming convention.

There are four levels where dataset-specific changes may be needed:

1. Paths and filenames.
2. Sensor column names and heights.
3. QC and flux thresholds.
4. Output names and folders.

### 1. Change Project And Data Paths

If using the notebook, edit the first code block in:

```text
notebooks/MAIN_GRADIENT_TOWER_PIPELINE_AUDITED.ipynb
```

Look for:

```python
PAPER_ROOT = Path(r"D:/OneDrive/PAPER_GRADIENT_TOWER")
PROJECT_ROOT = PAPER_ROOT / "gradient_tower_python_pipeline_modular"
DATA_ROOT = PAPER_ROOT / "PYTHON"
LATEX_GRAPHICS_DIR = PAPER_ROOT / "LATEX" / "graphics"

QC_NETCDF = DATA_ROOT / "data_nc/OGHYO_GradientTower_Dataset_2018_2026.nc"
MINUTE_FLUX_NETCDF = DATA_ROOT / "data_nc/OGHYO_Minute_Fluxes_2018_2026.nc"
FLUX_NETCDF = DATA_ROOT / "data_nc/OGHYO_30min_Fluxes_2018_2026.nc"
```

For a different dataset, change these paths, for example:

```python
PAPER_ROOT = Path(r"D:/my_project/my_tower")
DATA_ROOT = PAPER_ROOT / "data"
LATEX_GRAPHICS_DIR = PAPER_ROOT / "figures"

QC_NETCDF = DATA_ROOT / "netcdf/my_tower_qc.nc"
MINUTE_FLUX_NETCDF = DATA_ROOT / "netcdf/my_tower_fluxes_1min.nc"
FLUX_NETCDF = DATA_ROOT / "netcdf/my_tower_fluxes_30min.nc"
```

If using scripts, either edit the script defaults or pass paths from the command line:

```powershell
python scripts\run_flux_pipeline.py --nc-file "D:\my_project\data\netcdf\my_tower_qc.nc" --output-nc "D:\my_project\data\netcdf\my_tower_fluxes_30min.nc"
```

Relevant scripts:

```text
scripts/run_qc_pipeline.py
scripts/run_flux_pipeline.py
scripts/run_flag_audit.py
scripts/run_qc_audit_figures.py
```

### 2. Change Calibration And Original Raw Input Files

If regenerating the QC NetCDF from raw `.mat` files, update the QC regeneration block in the main notebook:

```python
run_full_qc_pipeline(
    temp_calib_file=DATA_ROOT / "calib_txt/matrix_temp_met.dat",
    rh_calib_file=DATA_ROOT / "calib_txt/matrix_relhum_met.dat",
    tower_mat_file=DATA_ROOT / "input_mat/var_torre_30m_20180515_20260430.mat",
    sun_mat_file=DATA_ROOT / "input_mat/sun_position_20180515_20260430.mat",
    output_netcdf=QC_NETCDF,
    cfg=qc_cfg,
    export_netcdf=True,
)
```

For another dataset, replace:

```text
matrix_temp_met.dat
matrix_relhum_met.dat
var_torre_30m_*.mat
sun_position_*.mat
```

with your calibration and input files.

The command-line equivalent is:

```powershell
python scripts\run_qc_pipeline.py --base-dir "D:\my_project\data" --temp-calib "calib/matrix_temp.dat" --rh-calib "calib/matrix_rh.dat"
```

### 3. Change Sensor Heights And Column Names

This is required if your tower does not use the same variable names as OGHYO.

The flux pipeline expects columns such as:

```text
wind_n1, wind_n2, wind_n3, wind_n5
temp_n1, temp_n2, temp_n3, temp_n5
q_2, q_6, q_12, q_24
theta_v_2, theta_v_6, theta_v_12, theta_v_24
P_Pa
```

For a different tower, update the configuration objects in:

```text
src/gradient_tower_pipeline/qc_pipeline.py
src/gradient_tower_pipeline/flux_pipeline.py
```

Look for configuration classes such as:

```python
TowerConfig
FluxConfig
Flux30MinConfig
```

Typical fields to adapt include:

```python
heights_m
temp_cols
rh_cols
wind_cols
wdir_cols
```

For example:

```python
heights_m = [2.0, 6.0, 12.0, 24.0]
temp_cols = {
    2.0: "temp_n1",
    6.0: "temp_n2",
    12.0: "temp_n3",
    24.0: "temp_n5",
}
wind_cols = {
    2.0: "wind_n1",
    6.0: "wind_n2",
    12.0: "wind_n3",
    24.0: "wind_n5",
}
```

If your dataset uses different column names, change the dictionaries rather than renaming variables manually throughout the code.

### 4. Change Flux QC Parameters

The 30-minute flux configuration is created in the main notebook in the block that calls:

```python
cfg30 = Flux30MinConfig(...)
```

This is the best place to tune QC without editing the core module.

Important pre-QC thresholds:

```python
min_availability
min_top_wind_ms
min_abs_wind_shear_ms
min_abs_temp_diff_K
min_valid_levels_most
min_valid_levels_brn
```

Important BRN controls:

```python
min_du_ms
rib_critical
rib_min_unstable
rib_range
use_abs_shear_for_brn
```

Important MOST controls:

```python
max_most_iterations
most_tolerance_L_m
most_relative_tolerance
initial_L_unstable_m
initial_L_stable_m
max_abs_zeta
min_abs_L_m
max_abs_L_m
```

Post-QC plausible ranges:

```python
ustar_range_ms
QH_range_Wm2
QE_range_Wm2
L_range_m
rib_range
```

Example audited configuration:

```python
cfg30 = Flux30MinConfig(
    progress=PROGRESS_30MIN,
    min_availability=0.65,
    min_top_wind_ms=0.30,
    min_abs_wind_shear_ms=0.05,
    min_abs_temp_diff_K=0.075,
    min_valid_levels_most=3,
    min_valid_levels_brn=2,
    min_du_ms=0.10,
    rib_critical=0.30,
    rib_range=(-2.0, 0.30),
    ustar_range_ms=(0.04, 2.00),
    QH_range_Wm2=(-150.0, 700.0),
    QE_range_Wm2=(-100.0, 700.0),
    max_most_iterations=80,
    most_tolerance_L_m=0.10,
    most_relative_tolerance=5.0e-3,
    include_distribution_stats=INCLUDE_30MIN_DISTRIBUTION_STATS,
    lower_quantile=LOWER_30MIN_QUANTILE,
    upper_quantile=UPPER_30MIN_QUANTILE,
)
```

Do not change many QC parameters at once unless you are running a sensitivity experiment. A recommended approach is:

1. Change one or two thresholds.
2. Re-run the 30-minute flux pipeline.
3. Compare QC flag distributions.
4. Check sign consistency and extreme flux audits.
5. Compare MOST vs BRN_ANC.
6. Inspect diurnal and seasonal cycles.

### 5. Change Figure Output Directories

In the notebook central configuration block:

```python
MINUTE_FIGURES_DIR = LATEX_GRAPHICS_DIR / "figures_flux_minute"
FIGURES_30MIN_DIR = LATEX_GRAPHICS_DIR / "figures_flux_30min"
SEASONAL_DIURNAL_FLUX_DIR = LATEX_GRAPHICS_DIR / "figures_flux_seasonal_diurnal"
VERTICAL_PROFILE_FIGURES_DIR = LATEX_GRAPHICS_DIR
QC_AUDIT_FIGURES_DIR = LATEX_GRAPHICS_DIR
```

Change these if you want figures to be written elsewhere.

### 6. Change Time Period For Heavy Minute Figures

Minute figures can be large. Limit the plotted period using:

```python
FIGURES_START = None
FIGURES_END = None
```

For example:

```python
FIGURES_START = "2019-01-01"
FIGURES_END = "2019-01-31"
```

These limits affect only figure generation, not the underlying NetCDF flux products.

## QC Flags

The pipeline separates input QC from post-calculation flux QC.

### Input QC Flags

`Input_QC_Flag` determines whether an interval is eligible for flux calculation.

Typical meanings:

```text
0 = accepted for calculation
1 = low wind
2 = weak wind shear
3 = insufficient valid levels
4 = missing critical input
5 = weak temperature gradient
6 = physically invalid input
7 = weak humidity gradient
8 = low 30-minute availability
```

### Post-QC Flux Flags

`QC_Flag_MOST` and `QC_Flag_BRN_ANC` evaluate the quality of the calculated flux output.

Typical meanings:

```text
0 = accepted flux
1 = u_star outside plausible range
2 = QH outside plausible range
3 = QE outside plausible range
4 = stability outside plausible range
5 = method status not successful
6 = missing or non-finite output
9 = not eligible from pre-QC
```

### Method Status Variables

Status variables describe whether the numerical method succeeded:

```text
Status_MOST
Status_BRN_ANC
```

Use cross-tabs to diagnose QC results:

```python
pd.crosstab(flux_30m["Status_MOST"], flux_30m["QC_Flag_MOST"])
pd.crosstab(flux_30m["Status_BRN_ANC"], flux_30m["QC_Flag_BRN_ANC"])
```

## QC Diagnostic Figures

The flux figure workflow now includes diurnal QC flag diagnostics.

For each of:

```text
Input_QC_Flag
QC_Flag_MOST
QC_Flag_BRN_ANC
```

the pipeline saves:

```text
qc_diurnal_counts_<flag_column>.png
qc_diurnal_counts_<flag_column>.pdf
qc_diurnal_counts_<flag_column>.csv
qc_diurnal_stacked_<flag_column>.png
qc_diurnal_stacked_<flag_column>.pdf
```

These figures show the number and composition of flags by half-hour of the day. They are useful for identifying whether rejections occur mostly at night, around sunrise, during stable conditions, or during daytime convective periods.

## Main Outputs To Check After A Run

After running the pipeline, check:

```text
PYTHON/data_nc/*.nc
PYTHON/data_nc/*.audit.csv
PYTHON/data_nc/*.column_name_map.csv
LATEX/graphics/figures_flux_30min/
LATEX/graphics/figures_flux_minute/
LATEX/graphics/figures_flux_seasonal_diurnal/
LATEX/graphics/
```

The notebook final manifest audits whether expected products exist and are non-empty.

## Recommended Scientific Validation

Before using fluxes in a publication, inspect:

- `QC_Flag_MOST` and `QC_Flag_BRN_ANC` distributions.
- `Input_QC_Flag` causes.
- `Status_MOST` vs `QC_Flag_MOST`.
- `Status_BRN_ANC` vs `QC_Flag_BRN_ANC`.
- Extreme flux audit.
- Flux sign consistency audit.
- MOST vs BRN paired comparison.
- Seasonal dry/wet diurnal cycles.
- Nocturnal flux behavior.
- Sensitivity to `min_availability`, `ustar_range_ms`, `rib_critical`, `rib_range`, and MOST convergence tolerances.

## Notes For New Datasets

When inserting a different dataset, the safest adaptation path is:

1. Update paths in the notebook first block.
2. Update calibration and raw input filenames if regenerating QC NetCDF.
3. Update tower heights and variable-name dictionaries in `TowerConfig` / `FluxConfig`.
4. Run only QC reconstruction.
5. Inspect the cleaned DataFrame columns.
6. Run 30-minute fluxes before minute fluxes.
7. Generate QC figures and inspect flag causes.
8. Tune QC parameters gradually.
9. Only then generate publication figures and final NetCDF files.

Avoid editing internal computational functions unless the physical method itself must change. Most dataset adaptation should be possible through configuration objects, input paths, and column mappings.

## Citation / Acknowledgment

This repository supports processing and auditing of gradient tower observations from the OGHYO / Mantaro Valley micrometeorological dataset. If used in scientific work, cite the associated dataset, observing facility, and the flux-processing methodology used for MOST and BRN_ANC estimates.
