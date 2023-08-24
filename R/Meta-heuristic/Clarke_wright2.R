## Constructs initial solution (in matrix format) with the clark_wright algorithm
clarke_wright <- function(d) {
  n <- nrow(d) - 1
  # Stage 1: make n routes, all from depot to customer and back
  routes <- list()
  dist_route <- c()
  for (i in 1:n) {
    routes[[i]] <- c(0, i, 0)
    dist_route[i] <- 2 * d[n + 1, i]
  }
  max_dist <- 1.2 * max(l) * v # Don't want unnecessary long routes
  
  # Stage 2: calculate savings
  savings_matrix <- matrix(NA, nrow = n, ncol = n)
  for (i in 1:n) {
    for (j in 1:n) {
      savings_matrix[i, j] <- d[n + 1, i] + d[n + 1, j] - d[i, j]
    }
  }
  savings_unsorted <- savings_matrix[upper.tri(savings_matrix)]
  savings <- sort(savings_unsorted, decreasing = T)
  savings <- savings[savings > 0]
  
  # Stage 3: merge routes
  if (length(savings) == 0) {
    return(routes)
  }
  
  for (k in 1:length(savings)) {
    index <- which(savings[k] == savings_matrix)[1] # Position where this savings was found
    i <- 1 + (index - 1) %/% n
    j <- index - (i-1) * n
    
    # Stop if in the same routes:
    for (t in 1:length(routes)) {
      if (i %in% routes[[t]]) {
        route_i <- t
        ind_i <- which(i == routes[[t]])
      }
      if (j %in% routes[[t]]) {
        route_j <- t
        ind_j <- which(j == routes[[t]])
      }
    }
    
    if (route_i == route_j) { # Can't merge if they are in the same route
      next
    }
    if ((ind_i == length(routes[[route_i]]) - 1) && (ind_j == 2)) { # if i endpoint, j startpoint
      new_dist <- dist_route[route_i] + dist_route[route_j] - savings[k] + d[i, j]
      if (new_dist < max_dist) {
        new_route <- c(routes[[route_i]], routes[[route_j]])
        new_route <- new_route[new_route > 0]
        new_route <- c(0, new_route, 0)
        routes <- routes[-c(route_i, route_j)]
        dist_route[length(dist_route) + 1] <- new_dist
        dist_route <- dist_route[-c(route_i, route_j)]
        routes[[length(routes) + 1]] <- new_route
      }
    } else if ((ind_j == length(routes[[route_j]]) - 1) && (ind_i == 2)) { # if j endpoint, i startpoint
      new_dist <- dist_route[route_i] + dist_route[route_j] - savings[k] + d[i, j]
      if (new_dist < max_dist) {
        new_route <- c(routes[[route_j]], routes[[route_i]])
        new_route <- new_route[new_route > 0]
        new_route <- c(0, new_route, 0)
        routes <- routes[-c(route_i, route_j)]
        dist_route[length(dist_route) + 1] <- new_dist
        dist_route <- dist_route[-c(route_i, route_j)]
        routes[[length(routes) + 1]] <- new_route
      }
    }
  }
  
  return(routes)
}