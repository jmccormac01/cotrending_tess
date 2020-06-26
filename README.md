# Cotrending TESS with Cotrendy

Removing systematics from TESS FFI by Sam Gill, using my Cotrendy toolkit

# Example

To remove systematics from the FFI light curves for a given sector, camera and CCD we do the following:

   1. Prepare a Cotrendy config file, see below for example
   1. Run ```prepare_tess_lc_for_cotrendy.py path_to_config_file```
   1. Run ```cotrend_tess_lcs.py path_to_config_file```

The above will generate cotrending basis vectors (CBVs) using stars with 8 < T < 12 and then cotrend all light curves using those vectors.

A simpler version of PDC-MAP is currently used where objects with normalised variability greater than the defined variability limt (default 1.3) are cotrended using the prior information from the neighbouting objects.

Objects with lower normalised variability are cotrended using a robust least squares fit.

# Contributors

James McCormac
