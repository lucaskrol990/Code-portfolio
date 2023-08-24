# Single point removal, but instead of a random position it always chooses
# the middle of the route. 

binary_removal <- function(sol) {
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
  
  if (length(temp_route) == 2) { # not sure if this is necessary for binary, it is for single, but it wont hurt
    sol[[9]] <- temp_route[1]
    sol[[1]] <- sol[[1]][-curr_route]
    sol[[1]][[length(sol[[1]]) + 1]] <- c(0, temp_route[2], 0)
    sol[[8]] <- rep(0, length(sol[[1]]))
    sol[[8]][length(sol[[1]])] <- 1
    sol[[7]] <- sol[[7]][-curr_route]
    return(sol)
  }
  
  remove_before <- ceiling(length(temp_route) / 2)
  sol[[9]] <- temp_route[1:(remove_before - 1)] # nodes you removed
  temp_route <- temp_route[remove_before:length(temp_route)]
  
  temp_route <- c(0, temp_route, 0)
  
  sol[[1]] <- sol[[1]][-curr_route]
  sol[[1]][[length(sol[[1]]) + 1]] <- temp_route
  sol[[8]] <- rep(0, length(sol[[1]]))
  sol[[8]][length(sol[[1]])] <- 1
  sol[[7]] <- sol[[7]][-curr_route]
  return(sol)
}