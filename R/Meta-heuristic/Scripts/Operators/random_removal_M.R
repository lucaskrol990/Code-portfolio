random_removal_M <- function(sol) { 
  q_possible_up <- max(round(0.1 * n), 5) # medium version, remove at most 10%
  q_possible_down <- 3 # dont want overlap with small
  q <- sample(q_possible_down:q_possible_up, 1)
  
  remove_node <- sample(1:n, q)
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