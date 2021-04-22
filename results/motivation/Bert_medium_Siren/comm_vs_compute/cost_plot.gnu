set term pdfcairo dashlength 0.6 enhanced font "Verdana, 13" size 6cm,3 cm
set output 'Bert_L12_strawman_S3_train.pdf'
set boxwidth 0.9 absolute
set style fill   solid 1.00 border lt -1
set key fixed right top vertical Left noreverse noenhanced autotitle nobox
set key inside  center top maxrows 2 center reverse samplen 0.05 width 0

set style histogram clustered gap 1 title textcolor lt -1
set datafile missing '-'
set style data histograms
set xtics border in scale 0,0 nomirror rotate by -45  autojustify
set xtics  norangelimit 
set xtics   ()
set ylabel "Time [sec]"   font ',15'
set xlabel "# workers"   font ',15'
set xrange [ * : * ] noreverse writeback
set x2range [ * : * ] noreverse writeback
set yrange [ 0.00000 : 110 ] noreverse writeback
set ytics 0,50,100
set y2range [ * : * ] noreverse writeback
set zrange [ * : * ] noreverse writeback
set cbrange [ * : * ] noreverse writeback
set rrange [ * : * ] noreverse writeback
NO_ANIMATION = 1
set lt 1 lc rgb 'blue'
set lt 2 lc rgb 'red'
set lt 3 lc rgb 'blue'
## Last datafile plotted: "immigration.dat"
plot 'overall_data' using (($2)+($3))/1000:xtic(1) ti col fs pattern 1 , '' u ($4)/1000 ti col #, '' u 3 ti col#, '' u 4 ti col

