"""
Take the cbvs file, find an object that went wrong
and plot all the steps of the correction
"""
import gc
import argparse as ap
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
    p.add_argument('--object_mask',
                   help='use the object mask if limited set')
    p.add_argument('--tic_id',
                   type=int,
                   help='TIC ID of specific target to plot')
    return p.parse_args()

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

    for tic_id in tic_ids:
        if args.tic_id and tic_id != args.tic_id:
            continue
        else:
            # map file
            map_filename = f"TIC-{tic_id}_map.pkl"
            print(f"Plotting from {map_filename}")
            mapp = cuts.depicklify(map_filename)

            # find the object we're working on
            loc = np.where(tic_ids == tic_id)[0][0]

            # set up the plot
            fig, ax = plt.subplots(ncols=3, nrows=n_cbvs+3, figsize=(20, 20), sharex=True, sharey=True)

            # row 0 is the raw fluxes, duplicate them to guide the eye
            title = f"Var: {cbvs.variability[loc]:.3f} Pw: {mapp.prior_weight:.3f} Pg: {mapp.prior_goodness:.3f}"
            ax[0, 0].plot(cbvs.norm_flux_array[loc], 'k.', label='raw data')
            ax[0, 0].set_title(f"Var: {cbvs.variability[loc]:.4f}")
            ax[0, 0].legend()
            ax[0, 1].plot(cbvs.norm_flux_array[loc], 'k.', label='raw data')
            ax[0, 1].set_title(f"Var: {cbvs.variability[loc]:.4f}")
            ax[0, 1].legend()
            ax[0, 2].plot(cbvs.norm_flux_array[loc], 'k.', label='raw data')
            ax[0, 2].set_title(f"Var: {cbvs.variability[loc]:.4f}")
            ax[0, 2].legend()

            # cbvs
            cond_cbvs = []
            prior_cbvs = []
            post_cbvs = []

            for i, cbv_id in enumerate(sorted(cbvs.cbvs.keys())):
                # conditional
                this_cbv_cond = cbvs.cbvs[cbv_id]*cbvs.fit_coeffs[cbv_id][loc]
                cond_cbvs.append(this_cbv_cond)
                ax[i+1, 0].plot(this_cbv_cond, 'r.',
                                label=f'CBV {cbv_id} [{cbvs.fit_coeffs[cbv_id][loc]:.5f}]')
                ax[i+1, 0].legend()
                # prior
                this_cbv_prior = cbvs.cbvs[cbv_id]*mapp.prior_peak_theta[cbv_id]
                prior_cbvs.append(this_cbv_prior)
                ax[i+1, 1].plot(this_cbv_prior, 'r.',
                        label=f'CBV {cbv_id} [{mapp.prior_peak_theta[cbv_id]:.5f}]')
                ax[i+1, 1].legend()
                # posterior
                this_cbv_post = cbvs.cbvs[cbv_id]*mapp.posterior_peak_theta[cbv_id]
                post_cbvs.append(this_cbv_post)
                ax[i+1, 2].plot(this_cbv_post, 'r.',
                        label=f'CBV {cbv_id} [{mapp.posterior_peak_theta[cbv_id]:.5f}]')
                ax[i+1, 2].legend()

            # combine the cbvs using the conditional
            cond_cbvs = np.sum(np.array(cond_cbvs), axis=0)
            corrected_cond = cbvs.norm_flux_array[loc] - cond_cbvs
            # combine the cbvs using the prior
            prior_cbvs = np.sum(np.array(prior_cbvs), axis=0)
            corrected_prior = cbvs.norm_flux_array[loc] - prior_cbvs
            # combine the cbvs using the posterior
            post_cbvs = np.sum(np.array(post_cbvs), axis=0)
            corrected_post = cbvs.norm_flux_array[loc] - post_cbvs

            # plot the commbined cond CBVs
            ax[n_cbvs+1, 0].plot(cond_cbvs, '.', color='orange', label='Cond')
            ax[n_cbvs+1, 0].legend()
            # plot the commbined prior CBVs
            ax[n_cbvs+1, 1].plot(prior_cbvs, '.', color='orange', label='Prior')
            ax[n_cbvs+1, 1].legend()
            # plot the commbined posterior CBVs
            ax[n_cbvs+1, 2].plot(post_cbvs, '.', color='orange', label='Post')
            ax[n_cbvs+1, 2].legend()

            # then the detrended lc cond
            ax[n_cbvs+2, 0].plot(corrected_cond, 'g.', label='Cotrended Cond')
            ax[n_cbvs+2, 0].legend()
            # then the detrended lc prior
            ax[n_cbvs+2, 1].plot(corrected_prior, 'g.', label='Cotrended Prior')
            ax[n_cbvs+2, 1].legend()
            # then the detrended lc posterior
            ax[n_cbvs+2, 2].plot(corrected_post, 'g.', label='Cotrended Post')
            ax[n_cbvs+2, 2].legend()

            fig.tight_layout()
            fig.savefig(f'TIC-{tic_id}_step_by_step.png')
            fig.clf()
            plt.close()
            gc.collect()
