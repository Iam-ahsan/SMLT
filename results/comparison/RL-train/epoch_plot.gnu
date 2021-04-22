set term pdfcairo dashlength 0.6 enhanced font "Verdana, 13" size 6cm,3 cm
#set terminal pngcairo  transparent enhanced font "arial,10" fontscale 1.0 size 600, 400 
set output 'RL_train_compare.pdf'
source1='data_SMLT'
source2='data_Siren'
source3='data_Cirrius'

#set border 3 front lt black linewidth 1.000 dashtype solid
set boxwidth 0.75 absolute
set style fill   solid 1.00 border lt -1
set key inside  right top maxrows 2 left reverse samplen 0.1 width 0
set key font ", 13"
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
set key font ', 13'
set xlabel "Workers" font ', 15'
set xrange [ * : * ] noreverse writeback
set x2range [ * : * ] noreverse writeback
set ylabel "time [sec]" font ', 15'
set yrange [ 0.0 : 110.0]
set ytics 0,50,100
set xtics 0,40,200
#plot source1 using 1:2 ti "4.xlarge" with linespoints ls 1 pt 5 ps 0.45 lc rgb "blue", source2 using 1:2 ti "12.xlarge" with linespoints ls 1 pt 6 ps 0.45 lc rgb "black", source3 using 1:2 ti "16.xlarge" with #linespoints ls 1 pt 5 ps 0.45 lc rgb "red"
#plot source1 using ($2) ti col, '' using ($3):key(1) ti col , '' using ($4) ti col, '' using ($5) ti col#, '' using 6 ti col#, '' using 7 ti col#, source2 using 2 ti "" with linespoints ls 1 pt 5 ps 0.45 lc rgb #"red"

plot source1 using 1:($2)/1000 ti "SMLT" with linespoints ls 1 pt 3 ps 0.45 lc rgb "black" ,\
  source2 using 1:($2)/1000 ti "Siren" with linespoints ls 1 pt 4 ps 0.45 lc rgb "blue" ,\
 source3 using 1:($2)/1000 ti "Cirrus" with linespoints ls 1 pt 6 ps 0.45 lc rgb "red" ,\
