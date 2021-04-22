set term pdfcairo dashlength 0.6 enhanced font "Verdana, 11" size 6cm,3 cm

set output 'Bert_medium_time_time_budget.pdf'
source1='plot_data_SLML'
source2='sharded_500_batch_size_Calcualted round time'


set boxwidth 0.5 absolute
set style fill solid 1.00 border lt -1
set key inside Left top maxrows 2 left reverse samplen 0.1 width 0

set style increment default
set style histogram columnstacked title textcolor lt -1
set datafile missing '-'
set style data histograms
set xtics border in scale 1,0.5 nomirror norotate  autojustify
set xtics  norangelimit 
set xtics   ()
set key font ",14"
#set xlabel "Workers" font ',14'
set xrange [ * : * ] noreverse writeback
set x2range [ * : * ] noreverse writeback
set ylabel "Time [min]" font ',14'
set yrange [ 0.0 : 275 ]
set ytics 0,80,275

set lt 3 lc rgb 'orange'
set lt 4 lc rgb 'blue'
set lt 1 lc rgb 'red'
set lt 2 lc rgb 'purple'
#set arrow from 0, graph 0 to 10, graph 1 nohead
set arrow from -1,60 to 3, 60 nohead front lc rgb "black" lw 1  dashtype "-"


plot source1 using ($2/60):key(1) ti col, 'plot_data_cirus' using ($2)/60 ti col , 'plot_data_Siren' using ($2)/60 ti col#, '' using ($5)/1000 ti col, '' using ($6)/1000 ti col#, '' using($7)/1000 ti col#, '' using ($8)/1000 ti col#, source2 using 2 ti "" with linespoints ls 1 pt 5 ps 0.45 lc rgb "black"

#plot source1 using 1:2 ti "Sharded" with linespoints ls 1 pt 3 ps 0.45 lc rgb "red" ,\
  source2 using 1:2 ti "Strawman" with linespoints ls 1 pt 4 ps 0.45 lc rgb "blue" ,\
