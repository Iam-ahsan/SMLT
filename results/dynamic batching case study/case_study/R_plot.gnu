set term pdfcairo dashlength 0.4 enhanced font "Verdana, 13" size 5cm,3cm

max(x,y) = (x>=y)?x:y

slo = 4.0
Rmax = slo

fileName = 'R_dynamic.pdf'
titleName = "95th-percentile Latency"
sourceData = 'latency'

set output fileName
set size 1.2, 1
set origin -0.1, 0

set xrange [0:240]
set yrange [0:1.05]
set y2range [70:640]

#set title titleName
set xlabel "time [min]" offset 0,0.25,0
set ylabel "Normalized" offset 2,0,0
set y2label "Users" rotate by -90 offset -2.5,0,0

#set xtics font "13"
#set ytics font "13"

set xtics 0,60,240
set ytics 0,0.2,1.05 nomirror
set y2tics 70,90,610 nomirror

#set logscale x
#set logscale y

set key below maxcols 2 Left reverse samplen 1 width 0.5

set label "S" at 12,1.13
set label "M" at 50,1.13
set label "xL" at 116,1.13
set label "M" at 170,1.13
set label "S" at 210,1.13

set style line 1 lt 2.5 lw 0.75 ps 0.2
set style fill transparent solid 0.25

set arrow from 0,slo/Rmax, graph 0 to 241,slo/Rmax, graph 1 nohead ls 1 dt 2 lc rgb "green" front
set arrow from 36,0, graph 0 to 36,1.05, graph 1 nohead ls 1 dt 2 lc rgb "red" front
set arrow from 80,0, graph 0 to 80,1.05, graph 1 nohead ls 1 dt 2 lc rgb "red" front
set arrow from 160,0, graph 0 to 160,1.05, graph 1 nohead ls 1 dt 2 lc rgb "red" front
set arrow from 190,0, graph 0 to 190,1.05, graph 1 nohead ls 1 dt 2 lc rgb "red" front

plot \
1/0 ti "SLO" ls 1 dt 2 lc rgb "green", \
1/0 ti "Change VM type" ls 1 dt 2 lc rgb "red", \
sourceData using ($1/60):($4) ti "Users" with steps ls 1 lc rgb "black" axes x1y2, \
sourceData using ($1/60):($3/Rmax) ti "CEDULE+" with steps ls 1 lc rgb "blue" axes x1y1
