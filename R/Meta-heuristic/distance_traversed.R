distance_traversed <- function(sol, idx) {
  current_route <- as.character(sol[[1]][[idx]])
  distance_traversed <- 0
  for (j in 1:(length(current_route) - 1)) {
    distance_traversed <- distance_traversed + d[current_route[j], current_route[j + 1]]
  }
  return(distance_traversed)
}