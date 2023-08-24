# Chooses a random route and a random position within this route.
# Then, removes the customers between the depot and this random position

single_point_removal <- function(sol) {
  curr_route <- sample(1:length(sol[[1]]), 1)
  temp_route <- sol[[1]][[curr_route]]
  temp_route <- temp_route[-c(1, length(temp_route))]
  
  if (length(temp_route) == 1) {
    sol[[1]] <- sol[[1]][-curr_route]
    sol[[9]] <- temp_route
    sol[[8]] <- rep(0, length(sol[[1]]))
    sol[[7]] <- sol[[7]][-curr_route]
    return(sol)
  }
  
  if (length(temp_route) == 2) {
    sol[[9]] <- temp_route[1]
    sol[[1]] <- sol[[1]][-curr_route]
    sol[[1]][[length(sol[[1]]) + 1]] <- c(0, temp_route[2], 0)
    sol[[8]] <- rep(0, length(sol[[1]]))
    sol[[8]][length(sol[[1]])] <- 1
    sol[[7]] <- sol[[7]][-curr_route]
    return(sol)
  }
  
  remove_before <- sample(2:length(temp_route), 1)
  sol[[9]] <- temp_route[1:(remove_before - 1)] # nodes you removed
  temp_route <- temp_route[remove_before:length(temp_route)]
  
  temp_route <- c(0, temp_route, 0)
  # print(sol[[1]])
  # print(sol[[7]])
  sol[[1]][[length(sol[[1]]) + 1]] <- temp_route
  sol[[1]] <- sol[[1]][-curr_route]
  sol[[8]] <- rep(0, length(sol[[1]]))
  sol[[8]][length(sol[[1]])] <- 1
  sol[[7]] <- sol[[7]][-curr_route]
  # print(sol[[1]])
  # print(sol[[7]])
  return(sol)
}
