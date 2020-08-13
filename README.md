# Cotrending TESS FFI light curves with Cotrendy

Removing systematics from TESS FFI by Sam Gill, using my Cotrendy toolkit

# Installing Cotrendy

   1. Cotrendy uses newer features in python like f-strings, so python>=3.6 is required
   1. Clone Cotrendy from the PLATO-Mission private repo using the standard process. Ask me for access.
   1. Then install Cotrendy using ```python setup.py install```

# Cotrending Example

To remove systematics from the FFI light curves for a given sector, camera and CCD we do the following:

   1. Prepare a Cotrendy config file, see below for example
   1. Run ```prepare_tess_lc_for_cotrendy.py path_to_config_file```
   1. Run ```cotrend_tess_lcs.py path_to_config_file```

The above will generate cotrending basis vectors (CBVs) using stars with 8 < T < 12 and then cotrend all light curves using those vectors.

The CBVs are fitted to the data using either a robust least squares (LS) or a Bayesian maximum a posteriori (MAP) method. The method is set using the ```cbv_mode``` option in the config file.

```wrapper.sh``` calls the three steps above in the correct order for each data set (per sector, camera and chip).

Below is an example config file with inline comments, things should be fairly self explanatory.

# Example Cotrendy configuration file

```toml
This is a TOML config file for TESS Sector S05
[owner]
name = "James McCormac"
version = "0.0.1"

[global]
# enable debugging mode?
debug = true
# working directory
root = "/tess/photometry/tessFFIextract/lightcurves/S05_1-1"
# time slot identifier, quarter, night etc
timeslot = "S05"
# camera_id
camera_id = "1-1"

[data]
# a file containing times, this should be the same length as each star row below
time_file = "tess_S05_1-1_times.pkl"
# a file containing fluxes (1 row per star)
flux_file = "tess_S05_1-1_fluxes.pkl"
# a file containing errors on flxues (1 row per star)
error_file = "tess_S05_1-1_errors.pkl"
# mask file to exclude cadences from CBV fitting
cadence_mask_file = "/tess/photometry/tessFFIextract/masks/S05_1-1_mask.fits"
# name of the cbv pickle file
cbv_file = "tess_S05_1-1_cbvs.pkl"
# file with ids of objects considered for CVBs
objects_mask_file = "tess_S05_1-1_objects_mask.pkl"
# reject outliers in the data, as per PLATO outlier rejection?
reject_outliers = false

[catalog]
# Master input catalog
master_cat_file = "/tess/photometry/tessFFIextract/sources/S05_1-1.fits"
# CBV input catalogs - these are the stars kept for making the CBVs
# ra, dec, mag, id
input_cat_file = "tess_S05_1_1_cat.pkl"
# MAP weights for ra, dec and mag
dim_weights = [1, 1, 2]

[cotrend]
# number of workers in multiprocessing pool
pool_size = 40
# maximum number of CBVs to attempt extracting
max_n_cbvs = 8
# SNR limit for significant cbvs, those with lower SNR are excluded
cbv_snr_limit = 5
# set if we want LS or MAP fitting - NOTE: MAP still needs some work
cbv_mode = "LS"
# set the normalised variability limit
normalised_variability_limit = 1.3
# set the normalised variability limit below which priors are not used
prior_normalised_variability_limit = 0.85
# take a few test case stars to plot PDFs etc
test_stars = [10,100,1000]
```

# Contributors

James McCormac
