set term pdfcairo dashlength 0.6 enhanced font "Verdana, 13" size 6cm,3 cm
#set terminal pngcairo  transparent enhanced font "arial,10" fontscale 1.0 size 600, 400 
set output 'Bert_L2_BO_distribution.pdf'
set border 2 front lt black linewidth 1.000 dashtype solid
set boxwidth 0.5 absolute
set style fill   solid 0.50 border lt -1
unset key
set pointsize 0.5
set style data boxplot
set xtics border in scale 0,0 nomirror norotate  autojustify
set xtics  norangelimit 
set xtics   ("Random" 1.00000, "SMLT" 2.00000)
#set ytics []border in scale 1,0.5 nomirror norotate  autojustify
set ytics 0,1,3

set ylabel "Throughput" font ',15'

set xrange [ * : * ] noreverse writeback
set x2range [ * : * ] noreverse writeback
set yrange [ 0.00000 : 3.000 ] noreverse nowriteback
set y2range [ * : * ] noreverse writeback
set zrange [ * : * ] noreverse writeback
set cbrange [ * : * ] noreverse writeback
set rrange [ * : * ] noreverse writeback
NO_ANIMATION = 1
## Last datafile plotted: "silver.dat"
#plot 'silver.dat' using (1):2, '' using (2):($3)
plot 'mydata' using (1):2, '' using (2):($3)
