"""
Take the products from SGE tmpdir and store them
"""
import os
import argparse as ap

# pylint: disable=invalid-name

def arg_parse():
    """
    Parse the command line arguments
    """
    p = ap.ArgumentParser()
    p.add_argument('sector_id',
                   type=str,
                   help='TESS sector ID (e.g. S05)')
    p.add_argument('camera_id',
                   type=str,
                   help='Camera ID (e.g. 1)',
                   choices=["1", "2", "3", "4"])
    p.add_argument('chip_id',
                   type=str,
                   help='Chip ID (e.g. 1)',
                   choices=["1", "2", "3", "4"])
    return p.parse_args()

args = arg_parse()
tmpdir = os.getenv('TMPDIR')
root = f"/tess/photometry/tessFFIextract/lightcurves/{args.sector_id}_{args.camera_id}-{args.chip_id}"

os.chdir(tmpdir)

# copy all the fits files etc back to main data dir
comm = f"cp -f TIC-*.fits {root}/"
print(comm)
os.system(comm)
comm2 = f"cp -f *.pkl {root}/"
print(comm2)
os.system(comm2)
comm3 = f"cp -f *.toml {root}/"
print(comm3)
os.system(comm3)
