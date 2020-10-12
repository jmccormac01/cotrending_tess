"""
Write out a cotrendy config file
"""
import os
import glob as g
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
    p.add_argument('cbv_mode',
                   type=str,
                   help='CBV fitting mode, MAP | LS',
                   choices=['MAP', 'LS'])
    return p.parse_args()

args = arg_parse()
tmpdir = os.getenv('TMPDIR')
root = f"/tess/photometry/tessFFIextract/lightcurves/{args.sector_id}_{args.camera_id}-{args.chip_id}"

# copy all the fits files to the tmpdir
#comm = f"cp {root}/TIC-*.fits {tmpdir}/"
#print(comm)
#os.system(comm)

templist = g.glob(f"{root}/TIC-*.fits")
n_templist = len(templist)
for i, t in zip(range(n_templist), templist):
    comm = f"cp -fv {t} {tmpdir}/"
    #print(f"[{i+1}/{n_templist}] {comm}")
    os.system(comm)

# now make a config file and put it in the working directory
config_filename = f"{tmpdir}/config_{args.sector_id}_{args.camera_id}-{args.chip_id}.toml"
config_template = f"""# This is a TOML config file for TESS Sector {args.sector_id}
[owner]
name = "James McCormac"
version = "0.0.1"

[global]
# enable debugging mode?
debug = true
# working directory
root = "{tmpdir}"
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
# coords units, are they in degrees for ra/dec or pix for X/Y
coords_units = "deg"
input_cat_file = "tess_{args.sector_id}_{args.camera_id}-{args.chip_id}_cat.pkl"
# MAP weights for ra, dec and mag
dim_weights = [1, 1, 2]

[cotrend]
# number of workers in multiprocessing pool
pool_size = {args.pool_size}
# maximum number of CBVs to attempt extracting
max_n_cbvs = 12
# SNR limit for significant cbvs, those with lower SNR are excluded
cbv_snr_limit = 5
# set if we want LS or MAP fitting - NOTE: MAP still needs some work
cbv_mode = "{args.cbv_mode}"
# set the normalised variability limit
normalised_variability_limit = 1.3
# set the normalised variability limit below which priors are not used
prior_normalised_variability_limit = 0.85
# take a few test case stars to plot PDFs etc
test_stars = [10,100,1000]
"""

with open(config_filename, 'w') as of:
    of.write(config_template)
