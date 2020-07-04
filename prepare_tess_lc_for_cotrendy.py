"""
Take a directory of TESS lcs, a catalog
for those objects and a with fits.open(mask_files[0]) as ff:
mask = ff[1].datamask file and
prepare input files for cotrendy
"""
import os
import argparse as ap
import glob as g
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
    m = fits.open(mask_file)
    mask = m[1].data['MASK']

    # load the catalog
    cat = fits.open(cat_file)[1].data

    # store some stuff for later
    fluxes_to_trendy, ras, decs, mags, ids = [], [], [], [], []
    neg_fluxes = []
    dilutions = []
    cbv_objects_mask = []

    # get a list of TIC lc files in current directory
    tic_files = sorted(g.glob('TIC-*.fits'))

    # loop over the files and pull out the ones we want to use for CBVs
    ignore = []
    for tic_file in tic_files:
        tic_id = int(tic_file.split('.fits')[0].split('-')[1])

        h = fits.open(tic_file)[1].data
        flux = h['AP2.5'][mask]
        sky = h['SKY_MEDIAN'][mask] * np.pi * (2.5**2)
        flux_corr = flux - sky
        neg = np.sum([flux_corr < 0])

        if neg == 0:
            # get the catalog info for pickle file
            row_in_cat = np.where(cat['TIC_ID'] == tic_id)[0]

            ra = cat['RA'][row_in_cat][0]
            dec = cat['DEC'][row_in_cat][0]
            mag = cat['Tmag'][row_in_cat][0]

            ras.append(ra)
            decs.append(dec)
            mags.append(mag)
            ids.append(tic_id)

            fluxes_to_trendy.append(flux_corr)
            times0 = int(h['BJD'][mask][0])
            times = h['BJD'][mask] - times0

            if 8.0 <= mag <= 12.0 and neg == 0:
                cbv_objects_mask.append(True)
            else:
                cbv_objects_mask.append(False)
        else:
            # store these files for ignoring
            ignore.append(tic_file)

    # get rid of files with negative counts
    if not os.path.exists('ignore'):
        os.mkdir('ignore')
    for ig in ignore:
        os.system(f"mv {ig} ignore/")

    fluxes_to_trendy = np.array(fluxes_to_trendy)
    cbv_objects_mask = np.array(cbv_objects_mask)

    # pickle the outputs
    picklify(config['data']['time_file'], times)
    picklify(config['data']['flux_file'], fluxes_to_trendy)
    picklify(config['data']['error_file'], np.sqrt(fluxes_to_trendy))
    picklify(config['data']['objects_mask_file'], cbv_objects_mask)
    picklify(config['catalog']['input_cat_file'], np.array([ras, decs, mags, ids]))
