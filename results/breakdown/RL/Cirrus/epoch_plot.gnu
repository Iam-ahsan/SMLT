set term pdfcairo dashlength 0.6 enhanced font "Verdana, 11" size 6cm,3 cm
#set terminal pngcairo  transparent enhanced font "arial,10" fontscale 1.0 size 600, 400 
set output 'RL_sharded_breakdwon.pdf'
source1='plot_data'
source2='sharded_500_batch_size_Calcualted round time'

#set border 3 front lt black linewidth 1.000 dashtype solid
set boxwidth 0.75 absolute
set style fill   solid 1.00 border lt -1
set key inside  Left top maxrows 1 center reverse samplen 0.1 width 0

set style increment default
set style histogram columnstacked title textcolor lt -1
set datafile missing '-'
set style data histograms
set xtics border in scale 1,0.5 nomirror rotate by -45  autojustify
set xtics  norangelimit 
set xtics   ()
#set ytics border in scale 0,0 mirror norotate  autojustify
#set ztics border in scale 0,0 nomirror norotate  autojustify
#set cbtics border in scale 0,0 mirror norotate  autojustify
#set rtics axis in scale 0,0 nomirror norotate  autojustify
set title "h) Atari Cirrus"
set lt 3 lc rgb 'orange'
set lt 4 lc rgb 'blue'
set lt 1 lc rgb 'red'
set lt 2 lc rgb 'blue'
set xlabel "Workers" font ",13"
set key font ",13"
set xrange [ * : * ] noreverse writeback
set x2range [ * : * ] noreverse writeback
set ylabel "time [sec]" font ",13"
set yrange [ 0.0 : 55.0 ]
set ytics 0,25,50
set lt 6 lc rgb 'blue'
plot source1 using ($2)/1000 ti col, '' using ($3)/1000:key(1) ti col , '' using ($4)/1000 ti col, '' using ($5)/1000 ti col, '' using ($6)/1000 ti col, '' using ($7)/1000 ti col, '' using ($8)/1000 ti col, '' using ($9)/1000 ti col
#plot source1 using ($2) ti col, '' using ($3):key(1) ti col , '' using ($4) ti col, '' using ($5) ti col, '' using 6 ti col, '' using 7 ti col#, source2 using 2 ti "" with linespoints ls 1 pt 5 ps 0.45 lc rgb "black"

#plot source1 using 1:2 ti "Sharded" with linespoints ls 1 pt 3 ps 0.45 lc rgb "red" ,\
  source2 using 1:2 ti "Strawman" with linespoints ls 1 pt 4 ps 0.45 lc rgb "blue" ,\
