set term pdfcairo dashlength 0.6 enhanced font "Verdana, 13" size 6cm,3 cm
#set terminal pngcairo  transparent enhanced font "arial,10" fontscale 1.0 size 600, 400 
set output 'resnet18_comm_compare.pdf'
source1='data_SMLT'
source2='data_Siren'
source3='data_Cirrius'

#set border 3 front lt black linewidth 1.000 dashtype solid
set boxwidth 0.75 absolute
set style fill   solid 1.00 border lt -1
#set grid nopolar
#set grid noxtics nomxtics ytics nomytics noztics nomztics nortics nomrtics \
# nox2tics nomx2tics noy2tics nomy2tics nocbtics nomcbtics
#set grid layerdefault   lt 0 linecolor 0 linewidth 0.500,  lt 0 linecolor 0 linewidth 0.500
#set key outside right top maxcols 3 vertical Left reverse samplen 1.0 width 0#noenhanced autotitle columnhead box lt black linewidth 1.000 dashtype solid
#set key inside  Left top maxcols 2 center reverse samplen 1.0 width 0
set key inside  left top maxrows 2 center reverse samplen 0.1 width 0

set style increment default
set style histogram columnstacked title textcolor lt -1
set datafile missing '-'
set style data histograms
set xtics border in scale 1,0.5 nomirror norotate  autojustify
set xtics  norangelimit 
set xtics   ()
#set ytics border in scale 0,0 mirror norotate  autojustify
#set ztics border in scale 0,0 nomirror norotate  autojustify
#set cbtics border in scale 0,0 mirror norotate  autojustify
#set rtics axis in scale 0,0 nomirror norotate  autojustify

set xlabel "Workers" font ',15'
set xrange [ 40 : 205 ] noreverse writeback
set x2range [ * : * ] noreverse writeback
set ylabel "time [sec]" font ',15'
set yrange [ 0.0 : 150.0]
set ytics 0,50,150
set xtics 50,50,200
#plot source1 using 1:2 ti "4.xlarge" with linespoints ls 1 pt 5 ps 0.45 lc rgb "blue", source2 using 1:2 ti "12.xlarge" with linespoints ls 1 pt 5 ps 0.45 lc rgb "black", source3 using 1:2 ti "16.xlarge" with #linespoints ls 1 pt 5 ps 0.45 lc rgb "red"
#plot source1 using ($2) ti col, '' using ($3):key(1) ti col , '' using ($4) ti col, '' using ($5) ti col#, '' using 6 ti col#, '' using 7 ti col#, source2 using 2 ti "" with linespoints ls 1 pt 5 ps 0.45 lc rgb #"red"

plot source1 using 1:($2) ti "SMLT" with linespoints ls 1 pt 3 ps 0.45 lc rgb "black" ,\
  source2 using 1:($2) ti "Siren" with linespoints ls 1 pt 4 ps 0.45 lc rgb "red" ,\
 source3 using 1:($2) ti "Cirrus" with linespoints ls 1 pt 6 ps 0.45 lc rgb "blue" ,\
