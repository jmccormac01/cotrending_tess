#!/bin/tcsh
if ($#argv != 4) then
    echo "Usage: $0 sector camera chip n_cores"
    goto done
endif

set config="/tess/photometry/tessFFIextract/lightcurves/$1/config_$1_$2_$3.toml"
echo "/usr/local/python3/bin/python /home/jmcc/dev/cotrending_tess/write_cotrendy_config_file.py $1 $2 $3 $4"
echo "/usr/local/python3/bin/python /home/jmcc/dev/cotrending_tess/prepare_tess_lcs_for_cotrendy.py $config"
echo "/usr/local/python3/bin/python /home/jmcc/dev/cotrending_tess/cotrend_tess_lcs.py $config"

done:
 exit 1
