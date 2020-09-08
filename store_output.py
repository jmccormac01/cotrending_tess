"""
Take the products from SGE tmpdir and store them
"""
import os
import glob as g
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
templist = g.glob('TIC-*.fits')
n_templist = len(templist)
for i, t in zip(range(n_templist), templist):
    comm = f"cp -fv {t} {root}/"
    print(f"[{i+1}/{n_templist}] " + comm)
    os.system(comm)

templist2 = g.glob('*.pkl')
n_templist2 = len(templist2)
for i, t in zip(range(n_templist2), templist2):
    comm2 = f"cp -fv {t} {root}/"
    print(f"[{i+1}/{n_templist2}] " + comm2)
    os.system(comm2)

templist3 = g.glob('*.toml')
n_templist3 = len(templist3)
for i, t in zip(range(n_templist3), templist3):
    comm3 = f"cp -fv {t} {root}/"
    print(f"[{i+1}/{n_templist3}] " + comm3)
    os.system(comm3)
