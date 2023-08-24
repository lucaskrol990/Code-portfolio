charge_feasibility <- function(sol, route_idx) { # route_idx indicates for which routes we need to check charge                                                   # feasibility
  locs <- unlist(sol[[1]][route_idx])
  locs <- locs[locs > 0] # Don't want depot in it
  if (sum(sol[[3]][locs] + sol[[4]][locs] > B + 0.01) > 0) { # Checks if vehicle is not overcharged
    print("Vehicle overcharged")
    return(FALSE)
  }
  
  if (sum(sol[[4]][locs] < -0.01) > 0) { # Checks if battery level is always positive
    print("Negative battery level")
    print(locs[which(sol[[4]][locs] < 0)])
    return(FALSE)
  }
  
  if (sum(sol[[2]][locs] >= (sol[[3]][locs] > 0)) < n) { # Only charge when we have a charger
    print("Charged when no charger available")
    wrong_loc <- which(sol[[2]][locs] < (sol[[3]][locs] > 0))
    print(wrong_loc)
    print(sol[[2]][wrong_loc])
    print(sol[[3]][wrong_loc])
    return(FALSE)
  } 
  
  for (route_list in sol[[1]][route_idx]) { # Checks if the correct amount is discharged
    route <- as.numeric(unlist(route_list))
    charge <- B
    discharge_matrix <- b * d
    # for (i in 1:(length(route) - 1)) {
    #   charge <- charge - discharge_matrix[route[i], route[i + 1]]
    #   if (charge < -0.01) {
    #     print("Incorrect amounts discharged")
    #     print(c(route[i], route[i + 1], charge))
    #     return(FALSE)
    #   }
    #   charge <- charge + sol[[3]][as.numeric(route[i + 1])]
    # }
    for (i in 1:(length(route) - 1)) {
      actual_discharge <- discharge_matrix[as.character(route[i]), as.character(route[i + 1])]
      if (i == 1) {
        obs_discharge <- B - sol[[4]][route[i + 1]]
      } else if (i == length(route) - 1) {
        if (sol[[4]][route[i]] + sol[[3]][route[i]] < actual_discharge - 0.01) {
          print("Incorrect amounts discharged endofroute")
          print(c(route[i], route[i + 1], actual_discharge, sol[[4]][route[i]]))
          return(FALSE)
        } else {
          next
        }
      } else {
        obs_discharge <- sol[[4]][route[i]] + sol[[3]][route[i]] - sol[[4]][route[i + 1]]
      }
      
      if (obs_discharge - actual_discharge < -0.001 | obs_discharge - actual_discharge > 0.01) {
        print("Incorrect amounts discharged")
        print(c(route[i], route[i + 1], actual_discharge, obs_discharge))
        return(FALSE)
      }
    }
  }
  
  return(TRUE)
}