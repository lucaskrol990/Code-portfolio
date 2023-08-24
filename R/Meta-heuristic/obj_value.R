obj_value <- function(sol) {
  route_idx <- which(sol[[8]] == 1)
  for (i in route_idx) {
    route <- sol[[1]][[i]]
    route <- route[route > 0]
    idx <- as.numeric(route)
    sol[[7]][i] <- c_V + c_d * distance_traversed(sol, i) + c_t * sum((sol[[6]][idx] - l[idx]) * (sol[[6]][idx] > l[idx])) + sum(c_c[idx] * sol[[2]][idx])
  }
  return(sol)
}