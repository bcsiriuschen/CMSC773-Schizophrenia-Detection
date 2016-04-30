feature_file=$1
prefix=$2

echo 'Generating training splits...'
python generate_splits.py $1 $2

for i in $(seq 0 9)
do
    svm-scale -s svm.scale.temp ${2}.train.${i}.data > ${2}.train.${i}.scale.data
    svm-train -b 1 ${2}.train.${i}.scale.data svm.model.temp
    svm-scale -r svm.scale.temp ${2}.test.${i}.data > ${2}.test.${i}.scale.data
    svm-predict -b 1 ${2}.test.${i}.scale.data svm.model.temp svm.output.${i}.temp
    cat svm.output.${i}.temp | tail -n +2 | cut -f2 -d' ' >> svm.output.temp
    cut -f1 -d' ' ${2}.test.${i}.scale.data >> groundtruth.temp
done

python update_svm_output.py svm.output.temp > ${2}.output
python evaluation.py ${2}.output groundtruth.temp ${2}.tpfp ${2}.png
rm *.temp