#!/bin/tcsh
if ($#argv != 5) then
    echo "Usage: $0 sector camera chip n_cores cbv_mode"
    goto done
endif

set config="$TMPDIR/config_$1_$2-$3.toml"
/usr/local/python3/bin/python /home/jmcc/dev/cotrending_tess/write_cotrendy_config_file.py $1 $2 $3 $4 $5
/usr/local/python3/bin/python /home/jmcc/dev/cotrending_tess/prepare_tess_lcs_for_cotrendy.py $config
/usr/local/python3/bin/python /home/jmcc/dev/cotrending_tess/cotrend_tess_lcs.py $config
/usr/local/python3/bin/python /home/jmcc/dev/cotrending_tess/store_output.py $1 $2 $3

done:
 exit 1
