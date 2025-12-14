lim = 2000
retardo = 0.001

set terminal qt size 800,800 enhanced font 'Verdana,10'
set size square

do for [i=0:lim]{
  titulo = sprintf("paso = %.4d - tiempo = %.5f", i, i*5e-5)
  set title titulo
  file = sprintf("/media/hvarkaed/a2e590e8-6eb4-4da7-a766-06b1247531ca/NeighboorsFloodSPH/Output/estabMac2_cut_fluid/Output/state_%.4d.txt", i)
  plot file every ::0::224 u 2:3 w p ps 1 pt 7 lc rgb "black" not,\
       "" every ::225::321 u 2:3 w p ps 1 pt 7 lc rgb "red" not,\
       "" every ::322::783 u 2:3 w p ps 1 pt 7 lc rgb "black" not,\
       "" every ::784::1583 u 2:3 w p ps 1 pt 7 lc rgb "blue" not
  pause retardo
}