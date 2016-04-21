for i in $(seq 0 9)
do
    svm-scale -s svm.scale svm/liwc.train.${i}.data > svm/liwc.train.${i}.scale.data
    svm-train -b 1 svm/liwc.train.${i}.scale.data svm.model
    svm-scale -r svm.scale svm/liwc.test.${i}.data > svm/liwc.test.${i}.scale.data
    svm-predict -b 1 svm/liwc.test.${i}.scale.data svm.model svm.output.${i}.temp
    cat svm.output.${i}.temp | tail -n +2 | cut -f2 -d' ' >> svm.output.temp
done

python update_svm_output.py svm.output.temp > svm.output

rm *.temp