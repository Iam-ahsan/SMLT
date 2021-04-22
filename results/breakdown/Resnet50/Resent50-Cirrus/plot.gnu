set term pdfcairo dashlength 0.6 enhanced font "Verdana, 11" size 6cm,3 cm

set output 'Resnet50_sharded_cluster_5_comm_cirrus.pdf'
source1='plot_data'
source2='sharded_500_batch_size_Calcualted round time'


set boxwidth 0.5 absolute
set style fill   solid 1.00 border lt -1
#set key inside left top maxrows 1 center reverse samplen 0.1 width 0
set key inside  Left top maxrows 2 left reverse samplen 0.1 width 0
set style increment default
set style histogram columnstacked title textcolor lt -1
set datafile missing '-'
set style data histograms
set xtics border in scale 1,0.5 nomirror norotate  autojustify
set xtics  norangelimit 
set xtics   ()
set key font ",13"
set title "b) Resnet 50 Cirrus"
set xlabel "Workers" font', 13'
set xrange [ * : * ] noreverse writeback
set x2range [ * : * ] noreverse writeback
set ylabel "time [sec]" font', 13'
set yrange [ 0.0 : 30 ]
set ytics 0,6,30
set lt 1 lc rgb 'red'
set lt 2 lc rgb 'blue'
set lt 3 lc rgb 'brown'
set lt 4 lc rgb 'dark-green'

plot source1 using ($2) ti col, '' using ($3):key(1) ti col , '' using ($4) ti col, '' using ($5) ti col, '' using ($6) ti col#, '' using($7)/1000 ti col#, '' using ($8)/1000 ti col#, source2 using 2 ti "" with linespoints ls 1 pt 5 ps 0.45 lc rgb "black"

#plot source1 using 1:2 ti "Sharded" with linespoints ls 1 pt 3 ps 0.45 lc rgb "red" ,\
  source2 using 1:2 ti "Strawman" with linespoints ls 1 pt 4 ps 0.45 lc rgb "blue" ,\
