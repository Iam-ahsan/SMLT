set term pdfcairo dashlength 0.6 enhanced font "Verdana, 13" size 6cm,3 cm
#set terminal pngcairo  transparent enhanced font "arial,10" fontscale 1.0 size 600, 400 
set output 'tensorflow_cifar10_time.pdf'
source1='plotting_data'
source2='sharded_500_batch_size_Calcualted round time'

#set border 3 front lt black linewidth 1.000 dashtype solid
set boxwidth 0.25 absolute

set style fill   solid 1.00 border lt -1

set key inside  right top maxrows 2 center reverse samplen 0.1 width 0

set style increment default
set style histogram columnstacked title textcolor lt -1
set datafile missing '-'
set style data histograms
set xtics border in scale 1,0.5 nomirror norotate  autojustify
set xtics  norangelimit 
set xtics   ()
set y2range [ * : * ] noreverse writeback
set xlabel "Framework"  font ',15'
set xrange [ * : * ] noreverse writeback
set x2range [ * : * ] noreverse writeback
set ylabel "Time [hours]"  font ',15'
set yrange [ 0.0 : 12.0 ]
set ytics 0,6,12
set grid ytics
set lt 1 lc rgb 'red'
set lt 2 lc rgb 'black'
set lt 6 lc rgb 'blue'

plot source1 using ($2) ti col, '' using ($3):key(1) ti col #, '' using ($4)/1000 ti col, '' using ($5)/1000 ti col, '' using ($6)/1000 ti col, '' using ($7)/1000 ti col, '' using ($8)/1000 ti col, '' using ($9)/1000 ti col

