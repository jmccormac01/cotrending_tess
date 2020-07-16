"""
Write out a cotrendy config file
"""
import argparse as ap
import numpy as np

# pylint: disable=invalid-name

def arg_parse():
    """
    Parse the command line arguments
    """
    p = ap.ArgumentParser()
    p.add_argument('sector_id',
                   type=str,
                   help='TESS sector ID (e.g. S05)')
    p.add_argument('camera_id',
                   type=str,
                   help='Camera ID (e.g. 1)',
                   choices=["1", "2", "3", "4"])
    p.add_argument('chip_id',
                   type=str,
                   help='Chip ID (e.g. 1)',
                   choices=["1", "2", "3", "4"])
    p.add_argument('pool_size',
                   type=int,
                   help='number of cores available for worker pool',
                   choices=np.arange(1, 81))
    return p.parse_args()

args = arg_parse()
root = f"/tess/photometry/tessFFIextract/lightcurves/{args.sector_id}_{args.camera}-{args.chip}"
config_filename = f"{root}/config_{args.sector_id}_{args.camera_id}-{args.chip_id}.toml"
config_template = f"""# This is a TOML config file for TESS Sector {args.sector_id}
[owner]
name = "James McCormac"
version = "0.0.1"

[global]
# working directory
root = "{root}"
# time slot identifier, quarter, night etc
timeslot = "{args.sector_id}"
# camera_id
camera_id = "{args.camera_id}-{args.chip_id}"

[data]
# a file containing times, this should be the same length as each star row below
time_file = "tess_{args.sector_id}_{args.camera_id}-{args.chip_id}_times.pkl"
# a file containing fluxes (1 row per star)
flux_file = "tess_{args.sector_id}_{args.camera_id}-{args.chip_id}_fluxes.pkl"
# a file containing errors on flxues (1 row per star)
error_file = "tess_{args.sector_id}_{args.camera_id}-{args.chip_id}_errors.pkl"
# mask file to exclude cadences from CBV fitting
cadence_mask_file = "/tess/photometry/tessFFIextract/masks/{args.sector_id}_{args.camera_id}-{args.chip_id}_mask.fits"
# name of the cbv pickle file
cbv_file = "tess_{args.sector_id}_{args.camera_id}-{args.chip_id}_cbvs.pkl"
# file with ids of objects considered for CVBs
objects_mask_file = "tess_{args.sector_id}_{args.camera_id}-{args.chip_id}_objects_mask.pkl"
# reject outliers in the data, as per PLATO outlier rejection?
reject_outliers = false

[catalog]
# Master input catalog
master_cat_file = "/tess/photometry/tessFFIextract/sources/{args.sector_id}_{args.camera_id}-{args.chip_id}.fits"
# CBV input catalogs - these are the stars kept for making the CBVs
# ra, dec, mag, id
input_cat_file = "tess_{args.sector_id}_{args.camera_id}_{args.chip_id}_cat.pkl"
# MAP weights for ra, dec and mag
dim_weights = [1, 1, 2]

[cotrend]
# number of workers in multiprocessing pool
pool_size = {args.pool_size}
# maximum number of CBVs to attempt extracting
max_n_cbvs = 8
# SNR limit for significant cbvs, those with lower SNR are excluded
cbv_snr_limit = 5
# CBV fitting method, sequential or simultaneous
#cbv_fit_method = "simultaneous"
cbv_fit_method = "sequential"
# set if we want LS or MAP fitting - NOTE: MAP still needs some work
cbv_mode = "MAP"
# set the normalised variability limit
normalised_variability_limit = 1.3
# take a few test case stars to plot PDFs etc
test_stars = [10,100,1000]
"""

with open(config_filename, 'w') as of:
    of.write(config_template)
