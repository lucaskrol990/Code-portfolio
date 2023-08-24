## Makes a matrix from a route
route_to_matrix <- function(list_route) {
  mat <- matrix(0, nrow = n + 1, ncol = n + 1)
  colnames(mat) <- c(1:n, 0)
  rownames(mat) <- c(1:n, 0)
  if (is.list(list_route) == FALSE) {
    route <- as.character(list_route)
    for (k in 1:(length(route) - 1)) {
      i <- route[k]
      j <- route[k + 1]
      mat[i, j] <- 1
    }
  } else {
    for (l in 1:length(list_route)) {
      route <- as.character(list_route[[l]])
      for (k in 1:(length(route) - 1)) {
        i <- route[k]
        j <- route[k + 1]
        mat[i, j] <- 1
      }
    }
  }
  return(mat)
}
