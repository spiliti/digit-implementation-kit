export DB_NAME=legacy_data
export DB_USER=legacy
export DB_PASSWORD='Ejb`gu=4<!_f%)M~'
export TENANT=pb.patiala
export DB_HOST=localhost
export BATCH_NAME=22
export TABLE_NAME=patiala_pt_legacy_data
export BATCH_SIZE=100
export DRY_RUN=TRUE
export PYTHONPATH=$PYTHONPATH:.
rm -rf *.log
    echo "Launching Batch $BATCH_NAME"
        python3 uploader/PropertyTaxDBProcess.py
	sleep 5
