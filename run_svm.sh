feature_file=$1
csv_file=$2
prefix=$3

echo 'Generating training splits...'
python generate_splits.py ${feature_file} ${csv_file} ${prefix}

echo 'Run SVM...'
for i in $(seq 0 9)
do
    svm-scale -s svm.scale.temp ${prefix}.train.${i}.data > ${prefix}.train.${i}.scale.data
    svm-train -c 50 -b 1 -q ${prefix}.train.${i}.scale.data svm.model.temp
    svm-scale -r svm.scale.temp ${prefix}.test.${i}.data > ${prefix}.test.${i}.scale.data
    svm-predict -b 1 -q ${prefix}.test.${i}.scale.data svm.model.temp svm.output.${i}.temp
    cat svm.output.${i}.temp | tail -n +2 | cut -f2 -d' ' >> svm.output.temp
    cut -f1 -d' ' ${prefix}.test.${i}.scale.data >> groundtruth.temp
done

mv groundtruth.temp ${prefix}.groundtruth.txt
python update_svm_output.py svm.output.temp > ${prefix}.svm.output
python evaluation.py ${prefix}.svm.output ${prefix}.groundtruth.txt ${prefix}.svm.tpfp ${prefix}.svm.png

echo 'Run VW...'
for i in $(seq 0 9)
do
    python svm_to_vw.py ${prefix}.train.${i}.data > ${prefix}.train.${i}.scale.vw.data
    python svm_to_vw.py ${prefix}.test.${i}.data > ${prefix}.test.${i}.scale.vw.data
    vw --quiet --binary --passes 20 -c -k -f vw.model.temp ${prefix}.train.${i}.scale.vw.data
    vw --quiet --binary -t -i vw.model.temp -r vw.output.${i}.temp ${prefix}.test.${i}.scale.vw.data
    cat vw.output.${i}.temp >> vw.output.temp
done
mv vw.output.temp ${prefix}.vw.output
python evaluation.py ${prefix}.vw.output ${prefix}.groundtruth.txt ${prefix}.vw.tpfp ${prefix}.vw.png
rm *.temp ${prefix}.*.data ${prefix}.*.cache

