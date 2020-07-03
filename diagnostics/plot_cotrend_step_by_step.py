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



