# Constructs a route from a matrix
mat_to_routes <- function(m) {
  n <- nrow(m) - 1
  starts <- which(m[n + 1,] > 0)
  routes <- lapply(starts, function(x) {c(0, x)})
  for (i in 1:length(starts)) {
    next_node <- -1
    while (next_node != 0) {
      curr_node <- routes[[i]][length(routes[[i]])]
      next_node <- which(m[as.numeric(curr_node),] > 0)
      next_node <- ifelse(next_node == n+1, 0, next_node)
      routes[[i]] <- as.vector(c(routes[[i]], next_node))
      if (length(routes[[i]]) > (n + 2)) {
        print(routes[[i]])
        return(FALSE)
      }
    }
  }
  return(routes)
}
