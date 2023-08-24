exchange_charge <- function(sol, tabu) {
  s_best <- sol
  ## Finding the route where to take the charge
  valid_routes <- c()
  for (i in 1:length(sol[[1]])) {
    x <- sol[[1]][[i]]
    x <- x[x > 0]
    if (sum(sol[[2]][x] > 0) >= 2 & sum(sol[[3]][x] > 0) >= 1) { 
      # If we have 2 or more charger locations in a route, one with charge, we can change charge amounts there
      valid_routes <- c(valid_routes, i)
    }
  }
  
  if (length(valid_routes) == 0) { # No valid routes
    return(sol)
  } else if (length(valid_routes) == 1) { # Only one valid route, so that will be changed
    route_change <- valid_routes
  } else { # Otherwise sample from valid routes
    route_change <- sample(valid_routes, 1)
  }
  
  ## Finding the location where to take the charge
  route <- sol[[1]][[route_change]]
  route <- route[route > 0]
  charge_locs <- which(sol[[3]][route] > 0) # Which locations have charge in the route
  if (length(charge_locs) == 1) { # If all charge is at one location, but there is an extra charger
    idx_remove_charge <- charge_locs
  } else {
    idx_remove_charge <- sample(charge_locs, 1) # Index at which to remove the charge
  }
  take_charge <- min(0.1 * B, sol[[3]][route[idx_remove_charge]]) # How much charge to take
  sol[[3]][route[idx_remove_charge]] <- sol[[3]][route[idx_remove_charge]] - take_charge
  
  ## Changing the battery levels in the rest of the route
  if (idx_remove_charge < length(route)) { # Battery levels need fixing then
    idx_adjust_battery <- route[(idx_remove_charge + 1):length(route)]
    sol[[4]][idx_adjust_battery] <- sol[[4]][idx_adjust_battery] - take_charge
  }
  
  ## Adding the charge back in the route
  charger_locs <- which(sol[[2]][route] > 0) # Which locations have a charger in the route
  s_best_obj <- Inf # To make sure next solution becomes s_best
  for (i in 1:length(charger_locs)) {
    temp_sol <- sol
    charger_idx <- route[charger_locs[i]]
    temp_sol[[3]][charger_idx] <- temp_sol[[3]][charger_idx] + take_charge
    if (temp_sol[[3]][charger_idx] + temp_sol[[4]][charger_idx] > B + 0.001) { # Too many charge at this location then
      # First add charge here to max 
      charge_left <- take_charge - (temp_sol[[3]][charger_idx] + temp_sol[[4]][charger_idx] - B)
      temp_sol[[3]][charger_idx] <- B - temp_sol[[4]][charger_idx]
      if (charger_locs[i] + 1 > length(route)) { # All battery levels are already correct
        idx_adjust_battery <- c()
      } else {
        idx_adjust_battery <- route[(charger_locs[i] + 1):length(route)]
      }
      temp_sol[[4]][idx_adjust_battery] <- temp_sol[[4]][idx_adjust_battery] + (take_charge - charge_left)
      # Then put rest of charge back at the location where we took charge again
      temp_sol[[3]][route[idx_remove_charge]] <- temp_sol[[3]][route[idx_remove_charge]] + charge_left
      if (idx_remove_charge < length(route)) { # Battery levels need fixing then
        idx_adjust_battery <- route[(idx_remove_charge + 1):length(route)]
        temp_sol[[4]][idx_adjust_battery] <- temp_sol[[4]][idx_adjust_battery] + charge_left
      }
      # Calculating effect of this
      if (sum(temp_sol[[4]] < -0.001) == 0 && sum(temp_sol[[4]] + temp_sol[[3]] > B + 0.001) == 0) { 
        # No negative charges' or overcharged vehicles
        temp_sol[[8]] <- rep(0, length(temp_sol[[1]]))
        temp_sol[[8]][route_change] <- 1
        s_now <- obj_value(a_z_sol(temp_sol))
        s_now_obj <- sum(s_now[[7]])
        if (s_now_obj < s_best_obj) {
          s_best <- s_now
        }
      }
    } else {
      if (charger_locs[i] + 1 > length(route)) { # All battery levels are already correct
        idx_adjust_battery <- c()
      } else {
        idx_adjust_battery <- route[(charger_locs[i] + 1):length(route)]
      }
      temp_sol[[4]][idx_adjust_battery] <- temp_sol[[4]][idx_adjust_battery] + take_charge
      if (sum(temp_sol[[4]] < -0.001) == 0 && sum(temp_sol[[4]] + temp_sol[[3]] > B + 0.001) == 0) { 
        # No negative charges' or overcharged vehicles
        temp_sol[[8]] <- rep(0, length(temp_sol[[1]]))
        temp_sol[[8]][route_change] <- 1
        s_now <- obj_value(a_z_sol(temp_sol))
        s_now_obj <- sum(s_now[[7]])
        if (s_now_obj < s_best_obj) {
          s_best <- s_now
        }
      }
    }
  }
  if (s_best[[3]][route[idx_remove_charge]] == 0) { # If we removed all charge and it never came back
    s_best[[2]][route[idx_remove_charge]] <- 0 # Remove the charger there
    # And change the cost accordingly
    for (i in 1:length(s_best[[1]])) {
      if (idx_remove_charge %in% s_best[[1]][[i]]) {
        s_best[[8]][i] <- 1
        s_best <- obj_value(s_best)
      }
    }
  }
  return(s_best)

}