charge_sol <- function(sol, tabu) {
  if (sum(sol[[8]]) == 0) {
    return(sol)
  } 
  discharge_matrix <- b * d
  
  routes_changed <- sol[[1]][which(sol[[8]] == 1)]
  for (i in 1:length(routes_changed)) {
    charge <- B
    route <- as.character(routes_changed[[i]])
    j <- 1
    while (j < length(route)) {
      charge <- charge - discharge_matrix[route[j], route[j + 1]]
      if (charge < 0) { # We want to add a charger at the previous node (route[j])
        k <- j # Node to add charger
        while (sum(as.numeric(route[k]) == tabu) > 0) { # If that node was tabu
          k <- k - 1 # Go to the node before it
          if (k == 1 || sum(route[k] == which(sol[[2]] == 1)) > 0) { # If location to charge is depot 
            # or has charger already
            k <- j # This would be infeasible, so we disobey tabu list
            break
          }
        }
        j <- k - 1
        sol[[2]][as.numeric(route[k])] <- TRUE # Add charger at the first node that was not tabu
        sol[[3]][as.numeric(route[k])] <- B - sol[[4]][as.numeric(route[k])] # Charge to max
        charge <- B  # Charge at that point is B
      } else {
        sol[[2]][as.numeric(route[j + 1])] <- 0 # no charger cause enough charge
        sol[[3]][as.numeric(route[j + 1])] <- 0 # no charging cause no charger
        sol[[4]][as.numeric(route[j + 1])] <- charge # battery level
      }
      j <- j + 1
    }
  }
  return(sol)
}
