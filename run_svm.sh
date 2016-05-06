feature_file=$1
prefix=$2

echo 'Generating training splits...'
python generate_splits.py $1 $2 svm

echo 'Run SVM...'
for i in $(seq 0 9)
do
    svm-scale -s svm.scale.temp ${2}.train.${i}.data > ${2}.train.${i}.scale.data
    svm-train -c 50 -b 1 -q ${2}.train.${i}.scale.data svm.model.temp
    svm-scale -r svm.scale.temp ${2}.test.${i}.data > ${2}.test.${i}.scale.data
    svm-predict -b 1 -q ${2}.test.${i}.scale.data svm.model.temp svm.output.${i}.temp
    cat svm.output.${i}.temp | tail -n +2 | cut -f2 -d' ' >> svm.output.temp
    cut -f1 -d' ' ${2}.test.${i}.scale.data >> groundtruth.temp
done

mv groundtruth.temp ${2}.groundtruth.txt
python update_svm_output.py svm.output.temp > ${2}.svm.output
python evaluation.py ${2}.svm.output ${2}.groundtruth.txt ${2}.svm.tpfp ${2}.svm.png

echo 'Run VW...'
for i in $(seq 0 9)
do
    python svm_to_vw.py ${2}.train.${i}.data > ${2}.train.${i}.scale.vw.data
    python svm_to_vw.py ${2}.test.${i}.data > ${2}.test.${i}.scale.vw.data
    vw --quiet --binary --passes 20 -c -k -f vw.model.temp ${2}.train.${i}.scale.vw.data
    vw --quiet --binary -t -i vw.model.temp -r vw.output.${i}.temp ${2}.test.${i}.scale.vw.data
    cat vw.output.${i}.temp >> vw.output.temp
done
mv vw.output.temp ${2}.vw.output
python evaluation.py ${2}.vw.output ${2}.groundtruth.txt ${2}.vw.tpfp ${2}.vw.png
rm *.temp ${2}.*.data ${2}.*.cache

