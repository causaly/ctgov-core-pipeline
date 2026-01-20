#!/bin/bash
DIR_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# set bash to 'debug' mode, it will exit on :
# -e 'error', -u 'undefined variable', -o ... 'error in pipeline', -x 'print commands'
set -e
set -u
set -o pipefail
set -x

NUM_PROCS=10
input_rows=$(wc -l < $1)
chunk_size=$(( ( input_rows + NUM_PROCS - 1 ) / NUM_PROCS ))

START_TIME=`date +%s`
mkdir -p ${DIR_ROOT}/interventions

echo '[Split input file to smaller chunks] start ...'

cp $1 ${DIR_ROOT}/interventions
interventions_file="${1##*/}"

python3 splitcsvk.py ${DIR_ROOT}/interventions/${interventions_file=} $chunk_size
rm -rf ${DIR_ROOT}/interventions/${interventions_file}

echo "[Split input file] Done."

echo '[Metamapping interventions] start ...'
mkdir -p ${DIR_ROOT}/metamap_interventions
mkdir -p ${DIR_ROOT}/metamap_interventions_logs
mkdir -p ${DIR_ROOT}/metamap_interventions_cache

for file in ${DIR_ROOT}/interventions/*.tsv; do

    file_no_path=${file##*/}
    basefile="${file_no_path%.tsv}"
    echo $basefile
    if [ ! -f ${DIR_ROOT}/metamap_interventions/$basefile.tsv ]; then

        # When the max number of processes is reached, sleep for 3 secs intervals until a process becomes availiable to assign the next job
        while [  $(ps -ef | grep -v grep | grep CT_03_metamap_intervention.py | wc -l) -ge $NUM_PROCS ]; do
            sleep 3
        done

        /usr/bin/python2.7 ${DIR_ROOT}/CT_03_metamap_intervention.py $file ${DIR_ROOT}/metamap_interventions/$basefile.tsv ${DIR_ROOT}/metamap_interventions_cache/$basefile.pkl ${DIR_ROOT}/metamap_interventions_logs/$basefile.txt  \ &

    fi
done
wait

echo '[Merging] start ...'

head -1 ${DIR_ROOT}/metamap_interventions/$(ls ${DIR_ROOT}/metamap_interventions | head -1) > $2
for filename in  ${DIR_ROOT}/metamap_interventions/*.tsv;
do
echo $filename && tail -n+2 $filename >> $2;
done

END_TIME=`date +%s`
TOTALTIME=$((END_TIME-START_TIME))
echo "[Metamapping interventions] Done in $TOTALTIME secs."
