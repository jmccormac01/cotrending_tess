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

    loc = np.where(catalog[-1] == args.tic_id)[0][0]

    fig, ax = plt.subplots(n_cbvs+3, figsize=(10, 10), sharex=True, sharey=True)

    # row 0 is the raw fluxes
    ax[0].plot(cbvs.norm_flux_array[loc], 'g.', label='raw data')
    ax[0].set_title(f"Ver: {cbvs.variability[loc]}")
    ax[0].legend()

    # cbvs
    ls_cbvs = []
    for i, cbv_id in enumerate(sorted(cbvs.cbvs.keys())):
        this_cbv_ls = cbvs.cbvs[cbv_id]*cbvs.fit_coeffs[cbv_id][loc]
        ls_cbvs.append(this_cbv_ls)
        ax[i+1].plot(this_cbv_ls, 'r.', label=f'CBV {cbv_id}')
        ax[i+1].legend()

    # combine the ls cbvs
    ls_cbvs = np.sum(np.array(ls_cbvs), axis=0)
    corrected_ls = cbvs.norm_flux_array[loc] - ls_cbvs

    # plot the commbined LS CBVs and
    # then the combined cbv that was applied
    ax[n_cbvs+1].plot(cbvs.cotrending_flux_array[loc], 'b.', label='MAP')
    ax[n_cbvs+1].plot(ls_cbvs, '.', color='orange', label='LS')
    ax[n_cbvs+1].legend()

    # then the detrended lc
    ax[n_cbvs+2].plot(cbvs.cotrended_flux_array[loc], 'b.', label='Cotrended MAP')
    ax[n_cbvs+2].plot(corrected_ls, '.', color='orange', label='Cotrended LS')
    ax[n_cbvs+2].legend()

    fig.tight_layout()
    fig.savefig(f'TIC-{args.tic_id}.png')
