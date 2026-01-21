if [ $# -eq 0 ]; then
    >&2 echo "No batchgen provided: E.g 20230924"
    exit 1
fi

if [ $# -ne 1 ]; then
    >&2 echo "Too many arguments provided"
    exit 1
fi


batch_gen=$1
re='^[0-9]+$'
if ! [[ $batch_gen =~ $re ]] ; then
   echo "error: batch gen must be a number E.g 20230924" >&2; exit 1
fi

batch_gen_len=`expr "$batch_gen" : '.*'`

if [ $batch_gen_len -ne 8 ]; then
    >&2 echo "Batchgen has incorrect format. Corect format is 8-digit `yyyymmdd`"
    exit 1
fi



echo "Cleanup storage .."
rm -rf Intermediate_steps/ xml_dumps/ txt-files/ metamap_* conditions/ interventions/ *stats.txt
echo "Done"
sleep 2

mkdir $PWD/xml_dumps
cd $PWD/xml_dumps
wget  https://classic.clinicaltrials.gov/AllAPIXML.zip
unzip *
rm -rf Contents.txt
mv AllAPIXML.zip $1_xml_dumps.zip
mv $1_xml_dumps.zip ../

cd ..
mkdir -p $PWD/Intermediate_steps
logs_dir=$PWD/${batch_gen}_logs
mkdir -p  "$logs_dir"

echo "Start xml parsing .."
python3 CT_01_extraction.py $PWD/xml_dumps $PWD/Intermediate_steps/CT_${batch_gen}_01.tsv 2>&1 | tee ${logs_dir}/01.log
echo  "Done"

echo "Start metamap server if not already started .."
if [  $(netstat -tulpn | grep :::1795 | wc -l) -eq 0 ]; then
  bash /tools/metamap_2020/public_mm/bin/skrmedpostctl start &&
  sleep 30
fi

if [  $(netstat -tulpn | grep :::5554 | wc -l) -eq 0 ]; then
  bash /tools/metamap_2020/public_mm/bin/wsdserverctl start &&
  sleep 120
fi


echo "Start conditions metamapping .."
bash CT_02_metamap_condition.sh $PWD/Intermediate_steps/CT_${batch_gen}_01.tsv $PWD/Intermediate_steps/CT_${batch_gen}_02.tsv 2>&1 | tee ${logs_dir}/02.log
echo  "Done"
sleep 60

echo "Start metamap server if not already started .."
if [  $(netstat -tulpn | grep :::1795 | wc -l) -eq 0 ]; then
  bash /tools/metamap_2020/public_mm/bin/skrmedpostctl start &&
  sleep 30
fi

if [  $(netstat -tulpn | grep :::5554 | wc -l) -eq 0 ]; then
  bash /tools/metamap_2020/public_mm/bin/wsdserverctl start &&
  sleep 120
fi

echo "Start interventions metamapping .."
bash CT_03_metamap_intervention.sh $PWD/Intermediate_steps/CT_${batch_gen}_02.tsv $PWD/Intermediate_steps/CT_${batch_gen}_03.tsv 2>&1 | tee ${logs_dir}/03.log
echo  "Done"
sleep 60

echo "Start deduplication .."
/usr/bin/python2.7 CT_05_deduplication.py $PWD/Intermediate_steps/CT_${batch_gen}_03.tsv $PWD/Intermediate_steps/CT_${batch_gen}_05.tsv 2>&1 | tee ${logs_dir}/05.log
echo  "Done"
sleep 10

echo "Start aggregation .."
/usr/bin/python2.7 CT_06_aggregation.py $PWD/Intermediate_steps/CT_${batch_gen}_05.tsv $PWD/Intermediate_steps/CT_${batch_gen}_06.tsv $batch_gen 0.6 2>&1 | tee ${logs_dir}/06.log
echo  "Done"
sleep 10

echo "Start NGS scoring .."
/usr/bin/python2.7 CT_07_ngs_scoring.py $PWD/Intermediate_steps/CT_${batch_gen}_06.tsv $PWD/Intermediate_steps/CT_${batch_gen}_07.tsv 2>&1 | tee ${logs_dir}/07.log
echo  "Done"
sleep 10

echo "Start Title tagging .."
/usr/bin/python2.7 CT_08_title_tagging_agg.py $PWD/Intermediate_steps/CT_${batch_gen}_07.tsv $PWD/Intermediate_steps/CT_${batch_gen}_08.tsv 2>&1 | tee ${logs_dir}/08.log
echo  "Done"
sleep 10

echo "Start mesh generation for evidence (main) file .."
python3 CT_09_mesh_generation.py $PWD/Intermediate_steps/CT_${batch_gen}_08.tsv $PWD/Intermediate_steps/CT_${batch_gen}_09.tsv $PWD/cui2mesh_2025AB_merged_2023AB.pkl 2>&1 | tee ${logs_dir}/09.log
echo  "Done"
sleep 10

echo "Start (enhanced) mesh generation for txt files .."
python3 CT_10_mesh_generation_txt_files.py $PWD/Intermediate_steps/CT_${batch_gen}_08.tsv $PWD/Intermediate_steps/CT_${batch_gen}_10.tsv $PWD/cui2mesh_2025AB_merged_2023AB.pkl 2>&1 | tee ${logs_dir}/10.log
echo  "Done"
sleep 10

echo "Generate txt files"
python3 CT_11_text_generation.py $PWD/Intermediate_steps/CT_${batch_gen}_10.tsv $PWD/xml_dumps txt-files 2>&1 | tee ${logs_dir}/11.log
echo "Done"
sleep 10

# Add count of txt-files (ls) to stats file
echo "# txt_files (ls txt-files | wc -l): " $(ls txt-files | wc -l) >> $PWD/${batch_gen}_stats.txt

echo "Archiving txt-files .."
tar -czvf  $PWD/${batch_gen}_ctgov_text.tar.gz txt-files
echo "Done"
sleep 5

echo "Upload data to gcs .."
gcloud auth activate-service-account --key-file $PWD/gcloud_service_account.json
gsutil -m cp $PWD/${batch_gen}_xml_dumps.zip gs://prd-ngs-ctgov/${batch_gen}/${batch_gen}_xml_dumps.zip
gsutil -m cp -R $PWD/${batch_gen}_logs gs://prd-ngs-ctgov/${batch_gen}
gsutil -m cp -R $PWD/Intermediate_steps gs://prd-ngs-ctgov/${batch_gen}
gsutil -m cp  $PWD/${batch_gen}_ctgov_text.tar.gz gs://prd-ngs-ctgov/${batch_gen}/${batch_gen}_ctgov_text.tar.gz
cp $PWD/Intermediate_steps/CT_${batch_gen}_09.tsv $PWD/${batch_gen}_ctgov_main.tsv
gsutil -m cp  $PWD/${batch_gen}_ctgov_main.tsv gs://prd-ngs-ctgov/${batch_gen}/${batch_gen}_ctgov_main.tsv
echo "Done"
sleep 5

echo "create stats file .."
tail -n 4 ${logs_dir}/01.log >> $PWD/${batch_gen}_stats.txt
python3 $PWD/misc/CT_stats.py $PWD/${batch_gen}_ctgov_main.tsv >> $PWD/${batch_gen}_stats.txt
echo "Done"
