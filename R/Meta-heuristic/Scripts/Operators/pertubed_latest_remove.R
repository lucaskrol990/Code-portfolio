# This function removes one of the nodes that pay the most, pertubed, penalty costs
pertubed_latest_remove <- function(sol, q = 1, n = 3) {
  pertubed_costs <- runif(length(l), 0.7, 1.3) * (sol[[6]] - l)
  three_latest <- sort(pertubed_costs, decreasing = T)[1:n]
  remove_node <- which(pertubed_costs == sample(three_latest, q))
  sol[[8]] <- rep(0, length(sol[[1]]))
  for (i in 1:length(remove_node)) {
    for (j in 1:length(sol[[1]])) {
      if (remove_node[i] %in% sol[[1]][[j]]) {
        route <- sol[[1]][[j]]
        route <- route[route != remove_node[i]]
        if (length(route) == 2) { # Route is depot to depot
          sol[[1]] <- sol[[1]][-j] # Remove the route
          sol[[7]] <- sol[[7]][-j] # Remove the objective value
          sol[[8]] <- sol[[8]][-j] # Route not changed, cause no route
        } else {
          sol[[1]][[j]] <- route
          sol[[8]][j] <- 1
        }
        break() # The node won't be in any of the other routes anymore
      }
    }
  }
  sol[[9]] <- remove_node
  return(sol)
}