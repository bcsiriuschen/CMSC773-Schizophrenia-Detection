#!/usr/bin/gnuplot

set term png enhanced font 'Verdana,16'
set termoption lw 2
set size 1,1
set output "roc.png"
set xtics .1
set ytics .1
set ylabel "true positive rate"
set xlabel "false positive rate"
set key right bottom
plot \
    "vw.tpfp" using 2:1 with lines title "VW", \
    "svm.tpfp" using 2:1 with lines title "LIWC-SVM"
