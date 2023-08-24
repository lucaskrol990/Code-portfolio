route_facility_removal <- function(sol) {
  sample_options <- rep(1, length(sol[[1]]))
  for (i in 1:length(sol[[1]])) {
    route <- sol[[1]][[i]]
    route <- route[route > 0]
    if (length(route) < 3) { # Barely profit to make sure
      sample_options[i] <- 0
    } else {
      charger_locs <- sol[[2]][route]
      if (sum(charger_locs) <= 1) {
        sample_options[i] <- 0
      }
    }
  }
  route_remove <- sample(1:length(sol[[1]]), 1) # For which route to remove all chargers
  nodes <- unlist(sol[[1]][[route_remove]]) # Nodes in the route
  nodes <- nodes[nodes > 0] # Remove depot
  sol[[2]][nodes] <- 0 # Set chargers to zero
  sol[[8]] <- rep(0, length(sol[[1]])) # Tell no changes made
  sol[[8]][route_remove] <- 1 # Except for the route where we just removed all chargers
  return(sol)
}