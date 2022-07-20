install.packages("trend")
library(trend)
install.packages("zoo")
library(zoo)

setwd('C:/SFS')
head = read.csv('./data/head_IT03GWBISSAPTA.csv')

head_fill = head

for(col in names(head)[-1]){
  idx = min(which(!is.na(head[col])))
  head_fill[, col][idx:nrow(head)] = na.approx(head[, col][idx:nrow(head)], maxgap = 12)
}

#Mann-Kendall
mk_db <- as.data.frame(array(dim = c(length(names(head_fill)[-1]), 2)))
names(mk_db) <- c("p_value", "z", "S")
rownames(mk_db) <- names(head_fill)[-1]

for(col in names(head_fill)[-1]){
  mk_db[col, 1] <- mk.test(head_fill[!is.na(head_fill[, col]), col])$p.value
  mk_db[col, 2] <- mk.test(head_fill[!is.na(head_fill[, col]), col])$statistic
  mk_db[col, 3] <- mk.test(head_fill[!is.na(head_fill[, col]), col])$estimates[1]
}

#Sen's slope
sen_db <- as.data.frame(array(dim = c(length(names(head_fill)[-1]), 2)))
names(sen_db) <- c("slope", "stat")
rownames(sen_db) <- names(head_fill)[-1]

for(col in names(head_fill)[-1]){
  sen_db[col, 1] <- sens.slope(head_fill[!is.na(head_fill[, col]), col])$estimates
  sen_db[col, 2] <- sens.slope(head_fill[!is.na(head_fill[, col]), col])$statistic
}
