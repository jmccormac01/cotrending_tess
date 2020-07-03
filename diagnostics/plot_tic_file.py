"""
Example layout of using Cotrendy
"""
import os
import argparse as ap
import matplotlib
matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
import cotrendy.utils as cuts
from cotrendy.catalog import Catalog
from cotrendy.cbvs import CBVs

def arg_parse():
    """
    Parse the command line arguments
    """
    p = ap.ArgumentParser()
    p.add_argument('tic_file',
                   help='path to TIC lc file')
    p.add_argument('--mask_file',
                   help='path to mask file')
    return p.parse_args()

if __name__ == "__main__":
    args = arg_parse()

    d = fits.open(args.tic_file)[1].data

    bjd = d['BJD'] - int(d['BJD'][0])
    data = d['AP2.5']
    sky = d['SKY_MEDIAN']
    cbv = d['CBV_AP2.5']
    corr = d['COR_AP2.5']

    data_no_sky = data - sky

    if args.mask_file:
        m = fits.open(args.mask_file)[1].data
        mask = m['MASK']
    else:
        mask = np.array([True]*len(data))

    fig, ax = plt.subplots(4, figsize=(10, 10), sharex=True)
    ax[0].plot(bjd[mask], data_no_sky[mask], 'r.', label="flux-sky")
    ax[0].legend()
    ax[1].plot(bjd[mask], sky[mask], 'b.', label="sky")
    ax[1].legend()
    ax[2].plot(bjd[mask], cbv[mask], 'g.', label="CBV total")
    ax[2].legend()
    ax[3].plot(bjd[mask], corr[mask], 'k.', label="flux corr")
    ax[3].legend()
    ax[3].set_xlabel('BJD - BJD0')
    fig.tight_layout()

    outfile = f"{args.tic_file.split('.')[0]}.png"
    fig.savefig(outfile)
