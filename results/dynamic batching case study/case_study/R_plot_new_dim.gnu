set term pdfcairo dashlength 0.4 enhanced font "Verdana,9" size 8cm,3.03 cm

slo = 4.0
Rmax = slo

fileName = 'case_study_dynamic_batching.pdf'
titleName = "95th-percentile Latency"
sourceData = 'data'

set output fileName
#set size 1.2, 1
#set origin -0.13, 0

set xrange [0:210]
set yrange [0:7.5]
set y2range [0:4500]


set xlabel "Epochs" offset 0,0.25,0 #font "14"
set ylabel "Throughput" offset -0.2,-1.5,0 #font "14"
set y2label "Batch size" offset 1.5,0,0

set xlabel font ",13"
set ylabel font ",13"
set y2label font ",13"
set xtics font ",13"
set ytics font ",13"
set y2tics font ",13"
set key font ',13'

set xtics 0,50,210 #font ',10'
set ytics 0,3,6 nomirror #font ',10'
set y2tics 0,1024,4500 nomirror offset 0.2,-1.5,0
#nomirror

set key top left maxrows 2 Left reverse samplen 1 width 0.5

#set label "1024" at 50,7 font ',13'
#set label "2048" at 110,7 font ',13'
#set label "4096" at 160,7 font ',13'


set style line 1 lt 2.5 lw 0.75 ps 0.2
set style fill transparent solid 0.25


#set arrow from 100,0, graph 0 to 100,7.5, graph 1 nohead ls 1 dt 2 lc rgb "red" front
#set arrow from 150,0, graph 0 to 150,7.5, graph 1 nohead ls 1 dt 2 lc rgb "red" front
#set arrow from 200,0, graph 0 to 200,7.5, graph 1 nohead ls 1 dt 2 lc rgb "red" front

#1/0 ti "Batch size" ls 1 dt 2 lc rgb "red", \

plot \
sourceData using ($1):($2) ti "User" with lp ls 1 lc rgb "blue" axes x1y1, \
sourceData using ($1):($3) ti "SMLT" with lp ls 1 lc rgb "black" axes x1y1 ,\
sourceData using ($1):($4) ti "Batch size" with l  ls 1 lc rgb "green" axes x1y2

