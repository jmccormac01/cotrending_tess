"""
Example layout of using Cotrendy
"""
import gc
from copy import deepcopy
import argparse as ap
import matplotlib
matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
import cotrendy.utils as cuts
import cotrendy.lightcurves as tlc
from cotrendy.catalog import Catalog
from cotrendy.cbvs import CBVs

# pylint: disable=invalid-name

def arg_parse():
    """
    Parse the command line arguments
    """
    p = ap.ArgumentParser()
    p.add_argument('config',
                   help='path to config file')
    return p.parse_args()

if __name__ == "__main__":
    # load the command line arguments
    args = arg_parse()

    # load the configuration
    config = cuts.load_config(args.config)
    camera_id = config['global']['camera_id']

    # grab the locations of the data
    root = config['global']['root']
    cbv_pickle_file = config['data']['cbv_file']
    cbv_pickle_file_output = f"{root}/{cbv_pickle_file}"
    cbv_fit_method = config['cotrend']['cbv_fit_method']

    # load the external catalog
    catalog = Catalog(config)

    # check if we have the cbv pickle file
    print(f"Looking for pickle file {cbv_pickle_file_output}...")
    cbvs = cuts.depicklify(f"{cbv_pickle_file_output}")
    # if there is no pickle file, extract the CBVs from scratch
    if cbvs is None:
        print(f"Pickle file {cbv_pickle_file_output} not found, doing detrending from scratch...")

        # step 1, load the photometry, this is done here and not prior to
        # the check for CBVs because the flux array is pickled with the CBVs
        times, lightcurves = tlc.load_photometry(config)

        # create a CBVs object for our targets, we want the top n_CBVs
        cbvs = CBVs(config, times, lightcurves)
        # pickle the intermediate CBVs object incase it crashes later
        cuts.picklify(cbv_pickle_file_output, cbvs)

        # calculate the basis vectors
        cbvs.calculate_cbvs()
        # pickle the intermediate CBVs object incase it crashes later
        cuts.picklify(cbv_pickle_file_output, cbvs)


    # At this point we have the CBVs, now we need to go back and
    # cotrend everything using them. We have to reload all the phot
    # the catalog and redo the variability calc etc
    print('Copying results...')
    vectors = deepcopy(cbvs.vect_store)
    cbvs_copy = deepcopy(cbvs.cbvs)

    # free up some resources
    print('Freeing up some resources...')
    del cbvs
    del catalog
    del times
    del lightcurves
    gc.collect()

    # start reloading things
    catalog = Catalog(config, apply_mask=False)
    times, lightcurves = tlc.load_photometry(config, apply_mask=False)

    # recreate the cbvs class but now manually insert some stuff from
    # the previous run and rerun the required parts for the cotrending
    cbvs = CBVs(config, times, lightcurves)
    cbvs.calculate_normalised_variability()

    # set the previously calculate parameters
    cbvs.cbvs = cbvs_copy
    cbvs.vect_store = vectors

    # work out the fit coefficients, needed for the Prior PDF
    # calculate them either simultaneously for all CBVs or sequentially
    # from the first to last
    if cbv_fit_method == "sequential":
        cbvs.calculate_robust_fit_coeffs_sequen()
    else:
        cbvs.calculate_robust_fit_coeffs_simult()
    # pickle the intermediate CBVs object incase it crashes later
    cuts.picklify(cbv_pickle_file_output, cbvs)

    # cotrend the data using either the LS or MAP methods
    if config['cotrend']['cbv_mode'] == 'MAP':
        # cotrend the data using the MAP method
        cbvs.cotrend_data_map(catalog, store_map=False)
    else:
        cbvs.cotrend_data_ls()
    # pickle the intermediate CBVs object incase it crashes later
    cuts.picklify(cbv_pickle_file_output, cbvs)
