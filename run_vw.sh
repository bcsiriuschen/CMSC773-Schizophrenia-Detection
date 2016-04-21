for i in $(seq 0 9)
do
    vw --binary --passes 20 -c -k -f vw.model vw/vw.train.${i}.data
    vw --binary -t -i vw.model -r vw.output.${i} vw/vw.test.${i}.data
done

cat vw.output.* > vw.output
rm vw.output.*
