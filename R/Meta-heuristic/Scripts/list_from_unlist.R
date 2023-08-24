list_from_unlist <- function(l) {
  route_list_temp <- list()
  i <- 1
  while(length(l) > 0) {
    route_list_temp[[i]] <- c(0)
    l <- l[-1]
    while(l[1] != 0) {
      route_list_temp[[i]] <- c(route_list_temp[[i]], as.numeric(l[1]))
      l <- l[-1]
    }
    route_list_temp[[i]] <- c(route_list_temp[[i]], 0)
    l <- l[-1]
    i <- i + 1
  }
  
  for (j in length(route_list_temp):1) {
    if (sum(route_list_temp[[j]]) == 0) {
      route_list_temp <- route_list_temp[-j]
    }
  }
  
  return(route_list_temp)
}
