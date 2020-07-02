"""
Take an input dir and plot a random sample of the light curves

We assume that the data is in AP2.5, COR_AP2.5 and CBV_AP2.5 columns
"""
import gc
import sys
import glob as g
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from astropy.io import fits

every = 50
lcs = sorted(g.glob('TIC*.fits'))
n_lcs = len(lcs)

# open the mask file
mask_files = g.glob('*mask.fits')
if len(mask_files) > 1:
    print('Multiple masks, quiting...')
    sys.exit(1)

with fits.open(mask_files[0]) as ff:
    mask = ff[1].data['MASK']

# plot a random sample of lcs
i = 0
while i < n_lcs:
    try:
        plot_name = "{}.png".format(lcs[i].split('.')[0])

        with fits.open(lcs[i]) as ff:
            data = ff[1].data

        bjd = data['BJD'][mask] - int(data['BJD'][mask][0])
        flux = data['AP2.5'][mask]
        cbvs = data['CBV_AP2.5'][mask]
        flux_corr = data['COR_AP2.5'][mask]
        sky = data['SKY_MEDIAN'][mask] * np.pi * (2.5**2)
        flux_sky_corr = flux - sky

        # now make a plot of the data, the correction and the corrected data
        fig, ax = plt.subplots(3, figsize=(10, 10), sharex=True)
        ax[0].plot(bjd, flux_sky_corr, 'g.', label='raw_norm')
        ax[0].legend()
        ax[0].set_ylabel('Flux')
        ax[1].plot(bjd, cbvs, 'k.', label='cbv_total')
        ax[1].legend()
        ax[1].set_ylabel('Flux norm')
        ax[2].plot(bjd, flux_corr, 'r.', label='cotrended')
        ax[2].legend()
        ax[2].set_ylabel('Flux')
        ax[2].set_xlabel('BJD - BJD0')
        fig.tight_layout()
        fig.savefig(plot_name)
        fig.clf()
        plt.close()
        gc.collect()

        print(i)

    except IndexError:
        print('Out of bounds')

    i += every



