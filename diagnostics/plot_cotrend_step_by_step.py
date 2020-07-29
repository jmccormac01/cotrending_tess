"""
Take the cbvs file, find an object that went wrong
and plot all the steps of the correction
"""
import gc
from multiprocessing import Pool
import argparse as ap
from functools import partial
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import cotrendy.utils as cuts


def arg_parse():
    """
    Parse the command line arguments
    """
    p = ap.ArgumentParser()
    p.add_argument('cbv_file',
                   help='Path to CBV file')
    p.add_argument('catalog_file',
                   help='Path to catalog file')
    p.add_argument('pool_size',
                   type=int,
                   help='number of cores to run on')
    p.add_argument('--object_mask',
                   help='use the object mask if limited set')
    return p.parse_args()


def worker_fn(star_id, constants):
    """
    """
    tic_ids, t_mags, cbvs = constants

    tic_id = tic_ids[star_id]
    t_mag = t_mags[star_id]
    var = cbvs.variability[star_id]
    flux = cbvs.norm_flux_array[star_id]
    n_cbvs = cbvs.n_cbvs

    print(f"Plotting for TIC-{tic_id}...")

    # map file
    map_filename = f"TIC-{tic_id}_map.pkl"
    mapp = cuts.depicklify(map_filename)

    # shrink some names
    pr_w8 = mapp.prior_weight
    pr_w8_var = mapp.prior_weight_pt_var
    pr_w8_gd = mapp.prior_weight_pt_gen_good
    pr_gen_gd = mapp.prior_general_goodness
    pr_noi_gd = mapp.prior_noise_goodness
    mode = mapp.mode

    # PLOT THE COND, PRIOR AND POSTERIOR STEP BY STEP #
    fig, ax = plt.subplots(ncols=3, nrows=n_cbvs+3, figsize=(20, 20), sharex=True, sharey=True)

    # row 0 is the raw fluxes, duplicate them to guide the eye
    title = f'Mag: {t_mag} Var: {var:.3f} Prior Wt: {pr_w8:.3f} [{pr_w8_var:.3f}:{pr_w8_gd:.3f}] Prior Gdness: {pr_gen_gd:.3f} [{pr_noi_gd:.3f}] -  Mode: {mode}'
    fig.suptitle(title)
    ax[0, 0].plot(flux, 'k.', label='raw data')
    ax[0, 0].legend()
    ax[0, 1].plot(flux, 'k.', label='raw data')
    ax[0, 1].legend()
    ax[0, 2].plot(flux, 'k.', label='raw data')
    ax[0, 2].legend()

    # cbvs
    cond_cbvs = []
    prior_cbvs = []
    if mode == "MAP":
        post_cbvs = []

    for i, cbv_id in enumerate(sorted(cbvs.cbvs.keys())):
        # LS
        this_cbv_cond = cbvs.cbvs[cbv_id]*cbvs.fit_coeffs[cbv_id][star_id]
        cond_cbvs.append(this_cbv_cond)
        ax[i+1, 0].plot(this_cbv_cond, 'r.',
                        label=f'CBV {cbv_id} [{cbvs.fit_coeffs[cbv_id][star_id]:.5f}]')
        ax[i+1, 0].legend()
        # prior
        this_cbv_prior = cbvs.cbvs[cbv_id]*mapp.prior_peak_theta[cbv_id]
        prior_cbvs.append(this_cbv_prior)
        ax[i+1, 1].plot(this_cbv_prior, 'r.',
                        label=f'CBV {cbv_id} [{mapp.prior_peak_theta[cbv_id]:.5f}]')
        ax[i+1, 1].legend()
        # posterior or LS again
        if mode == "MAP":
            this_cbv_post = cbvs.cbvs[cbv_id]*mapp.posterior_peak_theta[cbv_id]
            post_cbvs.append(this_cbv_post)
            ax[i+1, 2].plot(this_cbv_post, 'r.',
                            label=f'CBV {cbv_id} [{mapp.posterior_peak_theta[cbv_id]:.5f}]')
            ax[i+1, 2].legend()
        # otherwise just plot the LS one again in 3rd column
        else:
            ax[i+1, 2].plot(this_cbv_cond, 'r.',
                            label=f'CBV {cbv_id} [{cbvs.fit_coeffs[cbv_id][star_id]:.5f}]')
            ax[i+1, 2].legend()


    # combine the cbvs using the conditional
    cond_cbvs = np.sum(np.array(cond_cbvs), axis=0)
    corrected_cond = flux - cond_cbvs
    # combine the cbvs using the prior
    prior_cbvs = np.sum(np.array(prior_cbvs), axis=0)
    corrected_prior = flux - prior_cbvs
    # combine the cbvs using the posterior
    if mode == "MAP":
        post_cbvs = np.sum(np.array(post_cbvs), axis=0)
        corrected_post = flux - post_cbvs

    # plot the commbined cond CBVs
    ax[n_cbvs+1, 0].plot(cond_cbvs, '.', color='orange', label='LS')
    ax[n_cbvs+1, 0].legend()
    # plot the commbined prior CBVs
    ax[n_cbvs+1, 1].plot(prior_cbvs, '.', color='orange', label='Prior')
    ax[n_cbvs+1, 1].legend()
    # plot the commbined posterior CBVs
    if mode == "MAP":
        ax[n_cbvs+1, 2].plot(post_cbvs, '.', color='orange', label='Posterior')
        ax[n_cbvs+1, 2].legend()
    # otherwise repeat the LS
    else:
        ax[n_cbvs+1, 2].plot(cond_cbvs, '.', color='orange', label='LS')
        ax[n_cbvs+1, 2].legend()

    # then the detrended lc cond
    ax[n_cbvs+2, 0].plot(corrected_cond, 'g.', label='Cotrended LS')
    ax[n_cbvs+2, 0].legend()
    # then the detrended lc prior
    ax[n_cbvs+2, 1].plot(corrected_prior, 'g.', label='Cotrended Prior')
    ax[n_cbvs+2, 1].legend()
    # then the detrended lc posterior
    if mode == "MAP":
        ax[n_cbvs+2, 2].plot(corrected_post, 'g.', label='Cotrended Posterior')
        ax[n_cbvs+2, 2].legend()
    # otherwise repeat the LS
    else:
        ax[n_cbvs+2, 2].plot(corrected_cond, 'g.', label='Cotrended LS')
        ax[n_cbvs+2, 2].legend()

    fig.tight_layout()
    fig.subplots_adjust(top=0.95)
    fig.savefig(f'TIC-{tic_id}_step_by_step.png')
    fig.clf()
    plt.close()
    gc.collect()

    # PLOT THE CONDITIONAL PDFS #
    fig_c, axar_c = plt.subplots(len(cbvs.cbvs.keys()), figsize=(10, 10))
    if len(cbvs.cbvs.keys()) == 1:
        axar_c = [axar_c]

    try:
        _ = fig_c.suptitle(f'Mag: {t_mag} Var: {var:.3f} Prior Wt: {pr_w8:.3f} [{pr_w8_var:.3f}:{pr_w8_gd:.3f}] Prior Gdness: {pr_gen_gd:.3f} [{pr_noi_gd:.3f}]  -  Mode: {mode}')
        for i, ax_c in zip(sorted(cbvs.cbvs.keys()), axar_c):
            # draw a vertical line for the max of each PDF
            _ = ax_c.axvline(mapp.prior_peak_theta[i], color='blue', ls='--', label="prior")
            _ = ax_c.axvline(mapp.cond_peak_theta[i], color='red', ls='--', label="cond")
            _ = ax_c.axvline(mapp.posterior_peak_theta[i], color='green', ls='--', label="post")
            label = f"Cond ({mapp.cond_peak_theta[i]:.4f})"
            _ = ax_c.plot(cbvs.theta[i], mapp.cond_pdf[i], 'k-',
                          label=label)
            _ = ax_c.legend()

        fig_c.tight_layout()
        fig_c.subplots_adjust(top=0.95)
    except Exception:
        print("Prior plotting failed for star {star_id}")

    fig_c.savefig(f"TIC-{tic_id}_conditional_pdfs.png")
    fig_c.clf()
    plt.close()
    gc.collect()

    # PLOT THE PRIOR PDFS #
    fig_p, axar_p = plt.subplots(len(cbvs.cbvs.keys()), figsize=(10, 10))

    # make the axis a list if there is only one
    if len(cbvs.cbvs.keys()) == 1:
        axar_p = [axar_p]

    try:
        _ = fig_p.suptitle(f'Mag: {t_mag} Var: {var:.3f} Prior Wt: {pr_w8:.3f} [{pr_w8_var:.3f}:{pr_w8_gd:.3f}] Prior Gdness: {pr_gen_gd:.3f} [{pr_noi_gd:.3f}]  -  Mode: {mode}')
        for i, ax_p in zip(sorted(cbvs.cbvs.keys()), axar_p):
            # only plot the middle 96% of the objects, like the kepler plots
            sorted_coeffs = sorted(cbvs.fit_coeffs[i][mapp.prior_mask])
            llim = int(np.ceil(len(sorted_coeffs)*0.02))
            ulim = int(np.ceil(len(sorted_coeffs)*0.98))

            # make the plot
            _ = ax_p.hist(sorted_coeffs[llim:ulim], bins=mapp.hist_bins,
                          density=True, label='Theta Histogram')
            # draw a vertical line for the max of each PDF
            _ = ax_p.axvline(mapp.prior_peak_theta[i], color='blue', ls='--', label="prior")
            _ = ax_p.axvline(mapp.cond_peak_theta[i], color='red', ls='--', label="cond")
            _ = ax_p.axvline(mapp.posterior_peak_theta[i], color='green', ls='--', label="post")
            label = f"Theta PDFw ({mapp.prior_peak_theta[i]:.4f})"
            _ = ax_p.plot(cbvs.theta[i], mapp.prior_pdf[i], 'r-',
                          label=label)
            _ = ax_p.legend()

        fig_p.tight_layout()
        fig_p.subplots_adjust(top=0.95)
    except Exception:
        print("Prior plotting failed for star {star_id}")

    fig_p.savefig(f"TIC-{tic_id}_prior_pdfs.png")
    fig_p.clf()
    plt.close()
    gc.collect()

    # PLOT THE POSTERIOR PDFS  #
    fig_pt, axar_pt = plt.subplots(len(cbvs.cbvs.keys()), figsize=(10, 10))
    if len(cbvs.cbvs.keys()) == 1:
        axar_pt = [axar_pt]

    try:
        _ = fig_pt.suptitle(f'Mag: {t_mag} Var: {var:.3f} Prior Wt: {pr_w8:.3f} [{pr_w8_var:.3f}:{pr_w8_gd:.3f}] Prior Gdness: {pr_gen_gd:.3f} [{pr_noi_gd:.3f}]  -  Mode: {mode}')
        for i, ax_pt in zip(sorted(cbvs.cbvs.keys()), axar_pt):
            _ = ax_pt.plot(cbvs.theta[i], mapp.posterior_pdf[i], 'k-')
            # draw a vertical line for the max of each PDF
            _ = ax_pt.axvline(mapp.prior_peak_theta[i], color='blue', ls='--', label="prior")
            _ = ax_pt.axvline(mapp.cond_peak_theta[i], color='red', ls='--', label="cond")
            _ = ax_pt.axvline(mapp.posterior_peak_theta[i], color='green', ls='--', label="post")
            _ = ax_pt.legend()

        fig_pt.tight_layout()
        fig_pt.subplots_adjust(top=0.95)
    except Exception:
        print("Prior plotting failed for star {star_id}")

    fig_pt.savefig(f"TIC-{tic_id}_posterior_pdfs.png")
    fig_pt.clf()
    plt.close()
    gc.collect()


if __name__ == "__main__":
    args = arg_parse()

    # load some things
    catalog = cuts.depicklify(args.catalog_file)
    cbvs = cuts.depicklify(args.cbv_file)
    n_cbvs = len(cbvs.vect_store)

    # if there is an object mask, apply it.
    if args.object_mask:
        obj_mask = cuts.depicklify(args.object_mask)
    else:
        obj_mask = np.array([True]*len(catalog[0]))

    # apply the object mask to the catalog
    tic_ids = catalog[-1][obj_mask].astype(np.int64)
    t_mags = catalog[-2][obj_mask]

    n_targets = len(tic_ids)
    target_ids = np.arange(0, n_targets)

    const = (tic_ids, t_mags, cbvs)

    # make a partial function with the constants baked in
    fn = partial(worker_fn, constants=const)

    # run a pool of 6 workers and set them detrending
    with Pool(args.pool_size) as pool:
        pool.map(fn, target_ids)
