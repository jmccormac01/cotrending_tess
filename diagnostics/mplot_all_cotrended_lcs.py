"""
Use multiprocessing to plot all the cotrended diagnostic lcs
for a set of TESS FFIs
"""
import gc
import numpy as np
import argparse as ap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from multiprocessing import Pool
from functools import partial
from astropy.io import fits
from cotrendy.utils import depicklify

# pylint: disable=invalid-name

def arg_parse():
    """
    Parse command line
    """
    p = ap.ArgumentParser()
    p.add_argument('catalog',
                   help='catalog pickled filename')
    p.add_argument('cbvs',
                   help='cbvs pickled filename')
    p.add_argument('mask',
                   help='cadence mask fits filename')
    p.add_argument('pool_size',
                   type=int,
                   help='number of cores to run on')
    p.add_argument('--object_mask',
                   help='use the object mask if limited set')
    return p.parse_args()

def worker_fn(star_id, constants):
    """
    Read the files and do the plotting
    """
    catalog, variability, mask = constants

    # ra, dec, Tmag, ID
    current_cat_row = catalog[:, star_id]
    tic_id = int(current_cat_row[-1])
    t_mag = round(current_cat_row[-2], 2)

    # variability
    var_n = round(variability[star_id], 4)

    # names
    fits_file = f"TIC-{tic_id}.fits"
    plot_name = f"TIC-{tic_id}.png"

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
        ax[0].set_title(f"TIC-{tic_id} T={t_mag} Var_n={var_n}")
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

    # load this info for adding to plots
    catalog = depicklify(args.catalog)
    cbvs = depicklify(args.cbvs)

    if args.object_mask:
        obj_mask = depicklify(args.object_mask)
        catalog = catalog[obj_mask]

    if catalog is not None and cbvs is not None:

        # check the shapes match
        assert len(catalog[0]) == len(cbvs.variability), "Mismatched catalog/variability arrays"

        n_targets = len(catalog[0])
        target_ids = np.arange(0, n_targets)

        with fits.open(args.mask) as ff:
            cadence_mask = ff[1].data['MASK']

        # set up constants tuple
        const = (catalog, cbvs.variability, cadence_mask)

        # make a partial function with the constants baked in
        fn = partial(worker_fn, constants=const)

        # run a pool of 6 workers and set them detrending
        with Pool(args.pool_size) as pool:
            pool.map(fn, target_ids)
