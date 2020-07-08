"""
Use multiprocessing to plot all the cotrended diagnostic lcs
for a set of TESS FFIs
"""
import gc
import sys
import glob as g
import numpy as np
import argparse as ap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from multiprocessing import Pool
from functools import partial
from astropy.io import fits

# pylint: disable=invalid-name

def arg_parse():
    """
    Parse command line
    """
    p = ap.ArgumentParser()
    p.add_argument('pool_size',
                   type=int,
                   help='number of cores to run on')
    return p.parse_args()

def worker_fn(star_id, constants):
    """
    Read the files and do the plotting
    """
    lcs, mask = constants

    fits_file = lcs[star_id]
    base_name = fits_file.split('.fits')[0]
    plot_name = f"{base_name}.png"

    try:
        with fits.open(fits_file) as ff:
            data = ff[1].data

        bjd = data['BJD'][mask] - int(data['BJD'][mask][0])
        flux = data['AP2.5'][mask]
        sky = data['SKY_MEDIAN'][mask] * np.pi * (2.5**2)
        cbvs = data['CBV_AP2.5'][mask]
        flux_corr = data['COR_AP2.5'][mask]

        # generate some intermediate products
        flux_sky_corr = flux - sky
        med = np.median(flux_sky_corr)
        cbvs_in_flux = (cbvs * med) + med

        # now make a plot of the data, the correction and the corrected data
        fig, ax = plt.subplots(nrows=5, ncols=1, figsize=(10, 10), sharex=True)
        ax[0].plot(bjd, flux, 'k.', label='AP2.5')
        ax[0].legend()
        ax[0].set_ylabel('Flux')

        ax[1].plot(bjd, sky, 'b.', label='Sky median')
        ax[1].legend()
        ax[1].set_ylabel('Flux')

        ax[2].plot(bjd, flux_sky_corr, 'k.', label='AP2.5 - Sky median')
        ax[2].legend()
        ax[2].set_ylabel('Flux')

        ax[3].plot(bjd, cbvs_in_flux, 'r.', label='CBV total')
        ax[3].legend()
        ax[3].set_ylabel('Flux')

        ax[4].plot(bjd, flux_corr, 'r.', label='Flux CBV corr')
        ax[4].legend()
        ax[4].set_ylabel('Flux')
        ax[4].set_xlabel('BJD - BJD0')

        fig.tight_layout()
        fig.savefig(plot_name)
        fig.clf()
        plt.close()
        gc.collect()
    except Exception:
        pass

if __name__ == "__main__":
    args = arg_parse()
    lightcurves = sorted(g.glob('TIC*.fits'))
    n_lcs = len(lightcurves)
    target_ids = np.arange(0, n_lcs)

    # open the mask file
    mask_files = g.glob('*mask.fits')
    if len(mask_files) > 1:
        print('Multiple masks, quiting...')
        sys.exit(1)

    with fits.open(mask_files[0]) as ff:
        cadence_mask = ff[1].data['MASK']

    # set up constants tuple
    const = (lightcurves, cadence_mask)

    # make a partial function with the constants baked in
    fn = partial(worker_fn, constants=const)

    # run a pool of 6 workers and set them detrending
    with Pool(args.pool_size) as pool:
        pool.map(fn, target_ids)
