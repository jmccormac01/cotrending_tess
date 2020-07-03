"""
Take the cbvs file, find an object that went wrong
and plot all the steps of the correction
"""
import argparse as ap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.table import Table, Column
import cotrendy.utils as cuts
import cotrendy.lightcurves as clc
from cotrendy.catalog import Catalog
from cotrendy.cbvs import CBVs

def arg_parse():
    """
    Parse the command line arguments
    """
    p = ap.ArgumentParser()
    p.add_argument('tic_id',
                   type=int,
                   help='TIC ID of target')
    p.add_argument('cbv_file',
                   help='Path to CBV file')
    p.add_argument('catalog_file',
                   help='Path to catalog file')
    return p.parse_args()

if __name__ == "__main__":
    args = arg_parse()

    catalog = cuts.depicklify(args.catalog_file)
    cbvs = cuts.depicklify(args.cbv_file)
    n_cbvs = len(cbvs.vect_store)

    loc = np.where(catalog[-1] == args.tic_id)[0]

    fig, ax = plt.subplots(n_cbvs+3, figsize=(10, 10), sharex=True, sharey=True)

    # row 0 is the raw fluxes
    ax[0].plot(cbvs.norm_flux_array[loc], 'g.')
    ax[0].set_title(f"Ver: {cbvs.variability[loc]}")

    # cbvs
    for i, cbv_id in enumerate(sorted(cbvs.cbvs.keys())):
        ax[i+1].plot(cbvs.cbvs[cbv_id]*cbvs.fit_coeffs[cbv_id][loc], 'r.')

    # then the combined cbv
    ax[n_cbvs+2].plot(cbvs.cotrending_flux_array[loc], 'b.')

    # then the detrended lc
    ax[n_cbvs+3].plot(cbvs.cotrended_flux_array[loc], 'k.')

    fig.tight_layout()
    fig.savefig(f'TIC-{args.tic_id}.png')
