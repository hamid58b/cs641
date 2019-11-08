rlset reals;
phi := ex({colrank_3, yexp_3, colrank_5, ethnicity_3, colrank_2, ethnicity_2, yexp_2, colrank_4}, ((ethnicity_2 = (10 * ethnicity_1)) and (ethnicity_3 = ethnicity_2) and (colrank_2 = (10 * colrank_1)) and (colrank_3 = (25 + colrank_2)) and (yexp_2 = (5 * yexp_1)) and (yexp_3 = (10 + yexp_2)) and ((ethnicity_3 <= 10) or ((colrank_4 = (5 + colrank_3)) and (colrank_5 = colrank_4))) and ((not ((ethnicity_3 <= 10))) or (colrank_5 = colrank_3)) and (ethnicity_3 > 10)));
out "qelim.res";
rlqe phi;
shut "qelim.res";
quit;
