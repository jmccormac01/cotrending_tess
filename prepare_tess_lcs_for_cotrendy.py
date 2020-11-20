"""
Take a directory of TESS lcs, a catalog
for those objects and a with mask and
prepare input files for cotrendy
"""
import os
import argparse as ap
import numpy as np
from astropy.io import fits
from cotrendy.utils import picklify, load_config

# pylint: disable=invalid-name

def arg_parse():
    """
    Parse the command line arguments
    """
    p = ap.ArgumentParser()
    p.add_argument('config',
                   help='config file')
    return p.parse_args()

if __name__ == "__main__":
    args = arg_parse()

    # load the configuration file
    config = load_config(args.config)
    root = config['global']['root']
    mask_file = config['data']['cadence_mask_file']
    cat_file = config['catalog']['master_cat_file']

    # go into the root data directory
    os.chdir(root)

    # load the sector cadence mask
    with fits.open(mask_file) as m:
        mask = m[1].data['MASK']

    # load the catalog
    with fits.open(cat_file) as cata:
        cat = cata[1].data

    # store some stuff for later
    fluxes_to_cotrendy, ras, decs, mags, ids = [], [], [], [], []
    neg_fluxes = []
    dilutions = []
    cbv_objects_mask = []

    # loop over the catalog rows and pull out the ones we want to use for CBVs
    skipped = 0
    for row in cat:
        tic_id = row['TIC_ID']
        tic_file = f"TIC-{tic_id}.fits"

        try:
            with fits.open(tic_file) as ff:
                h = ff[1].data

            flux = h['AP2.5'][mask]
            sky = h['SKY_MEDIAN'][mask] * np.pi * (2.5**2)
            flux_corr = flux - sky
            neg = np.sum([flux_corr < 0])
        except FileNotFoundError:
            #print(f"Skipping {tic_file}, not found...")
            skipped += 1
            continue

        #if neg == 0:
        ras.append(row['RA'])
        decs.append(row['DEC'])
        mags.append(row['Tmag'])
        ids.append(tic_id)

        fluxes_to_cotrendy.append(flux_corr)
        times0 = int(h['BJD'][mask][0])
        times = h['BJD'][mask] - times0

        if 8.0 <= row['Tmag'] <= 12.0:# and neg == 0:
            cbv_objects_mask.append(True)
        else:
            cbv_objects_mask.append(False)

    fluxes_to_cotrendy = np.array(fluxes_to_cotrendy)
    cbv_objects_mask = np.array(cbv_objects_mask)

    # pickle the outputs
    picklify(config['data']['time_file'], times)
    picklify(config['data']['flux_file'], fluxes_to_cotrendy)
    picklify(config['data']['error_file'], np.sqrt(fluxes_to_cotrendy))
    picklify(config['data']['objects_mask_file'], cbv_objects_mask)
    picklify(config['catalog']['input_cat_file'], np.array([ras, decs, mags, ids]))

    print(f"Grabbed light curves for {len(fluxes_to_cotrendy)} objects.")
    print(f"Skipped {skipped} objects from catalog, files not found.")
