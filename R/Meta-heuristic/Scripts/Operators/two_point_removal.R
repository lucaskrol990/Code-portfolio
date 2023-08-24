# Two point removal: Selects a random route and two random positions within this route.
# Then, removes the customers between these positions

two_point_removal <- function(sol) {
  curr_route <- sample(1:length(sol[[1]]), 1)
  temp_route <- sol[[1]][curr_route][[1]]
  temp_route <- temp_route[-c(1, length(temp_route))]
  
  if (length(temp_route) <= 2) {
    sol[[1]] <- sol[[1]][-curr_route]
    sol[[9]] <- temp_route
    sol[[8]] <- rep(0, length(sol[[1]]))
    sol[[7]] <- sol[[7]][-curr_route]
    return(sol)
  }
  
  
  remove_before <- as.numeric(sample(1:length(temp_route), 2))
  
  # dit is denk ik nodig, not sure
  if (identical(as.numeric(sort(remove_before)), as.numeric(c(1, length(temp_route))))) {
    if (length(sol[[1]]) > 1) { # Can't destroy the only route we have
      sol[[1]] <- sol[[1]][-curr_route]
      sol[[9]] <- temp_route
      sol[[8]] <- rep(0, length(sol[[1]]))
      sol[[7]] <- sol[[7]][-curr_route]
    } else {
      sol[[8]] <- 1
      destroy <- as.numeric(sample(2:length(temp_route), 2))
      sol[[9]] <- temp_route[min(destroy):max(destroy)]
      sol[[1]] <- c(0, temp_route[-(min(destroy):max(destroy))], 0)
      sol[[7]] <- sol[[7]][-curr_route]
    }
    return(sol)
  }
  
  sol[[9]] <- temp_route[min(remove_before):max(remove_before)]
  temp_route <- temp_route[-(min(remove_before):max(remove_before))]
  temp_route <- c(0, temp_route, 0)
  sol[[1]][[length(sol[[1]]) + 1]] <- temp_route
  sol[[1]] <- sol[[1]][-curr_route]
  sol[[8]] <- rep(0, length(sol[[1]]))
  sol[[8]][length(sol[[1]])] <- 1
  sol[[7]] <- sol[[7]][-curr_route]
  
  return(sol)
}