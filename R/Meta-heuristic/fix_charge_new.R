fix_charge_new <- function(sol, tabu) {
  route_changed <- sol[[1]][[which(sol[[8]] == 1)]] # The changed route
  discharge_matrix <- b * d
  c_c[tabu] <- 100000 # Make tabu chargers very expensive
  
  charge_vec <- c(0) # Charge upon arriving at location
  cost_vec <- c(0) # Cost of placing at end is zero
  placement_list <- list(c()) # No charger placement at depot as that is obvious
  for (i in length(route_changed):2) { # Start at the end
    discharge_edge <- discharge_matrix[as.character(route_changed[i]), as.character(route_changed[i - 1])]
    j <- 1
    # In here we calculate for every option how much charge we would need when leaving node i - 1
    # to get to the solution
    while (j <= length(charge_vec)) { # Loop through the charge_vec
      charge_vec[j] <- charge_vec[j] + discharge_edge
      if (charge_vec[j] > B) { # This option is infeasible
        # So remove this option
        charge_vec <- charge_vec[-j]
        cost_vec <- cost_vec[-j]
        placement_list <- placement_list[-j]
        j <- j - 1
      }
      j <- j + 1
    }
    
    if (i == 2) { # We are the depot, so we do not have to consider adding chargers anymore
      break()
    }
    
    # Here we consider for every possible solution at the moment, adding a charging location at node
    # i - 1 and then leaving with the charge as given in charge_vec
    for (j in 1:length(charge_vec)) {
      charge_vec <- c(charge_vec, 0) # If you add a charger here, the charge upon arriving is zero
      cost_vec <- c(cost_vec, cost_vec[j] + c_c[as.numeric(route_changed[i - 1])]) # Cost of charger
      placement_list[[length(placement_list) + 1]] <- c(placement_list[[j]], i - 1) 
      # Place in route charger added
    }
    
    # Lastly, we loop through charge_vec and find the equal elements. For these, we choose the minimum
    # to keep, the others we can remove
    j <- 0
    while (j < length(charge_vec)) {
      j <- j + 1
      idx_identical <- which(charge_vec == charge_vec[j]) # Indices of identical elements
      if (length(idx_identical) > 1) {
        idx_remove <- idx_identical[-which.min(cost_vec[idx_identical])] # Worst options
        # Remove those here
        charge_vec <- charge_vec[-idx_remove]
        cost_vec <- cost_vec[-idx_remove]
        placement_list <- placement_list[-idx_remove]
        if (sum(idx_remove == j) > 0) { # If j is one of the removed ones, consider same j again
          j <- j - 1
        }
      }
    }
  }
  
  ## First we find the optimal solution and improve it by using the unused charge at the start location
  
  opt_idx <- which.min(cost_vec) # Index of optimal charger placements
  placement_idx <- placement_list[[opt_idx]] # Indices of where we placed chargers in the route
  # Here we loop through it again
  charge <- 0
  battery_vec <- rep(0, length(route_changed) - 2)
  charge_vec <- rep(0, length(route_changed) - 2)
  for (i in length(route_changed):3) {
    discharge_edge <- discharge_matrix[as.character(route_changed[i - 1]), as.character(route_changed[i])]
    charge <- charge + discharge_edge
    if (sum((i - 1) == placement_idx) > 0) { # We put a charger here
      sol[[2]][route_changed[i - 1]] <- 1 # Add to chargers
      charge_vec[i - 2] <- charge # Amount charged is amount we needed to get to here
      charge <- 0 # So charge at arrival equals 0
    }
    battery_vec[i - 2] <- charge
  }
  
  ## In here, we make sure that the we start with a full charge and therefore charge less at other
  ## places
  discharge_to_1 <- discharge_matrix[as.character(route_changed[1]), as.character(route_changed[2])]
  unused_charge <- B - (battery_vec[1] + discharge_to_1) # Charge amount under B at the depot
  i <- 1
  while (unused_charge > 0 && i <= length(charge_vec)) {
    battery_vec[i] <- battery_vec[i] + unused_charge
    if (charge_vec[i] > 0) { # If a charger here
      remove_charge <- min(unused_charge, charge_vec[i])
      charge_vec[i] <- charge_vec[i] - remove_charge
      unused_charge <- unused_charge - remove_charge
      if (unused_charge > 0) {
        print("A charger was not needed here")
        sol[[2]][route_changed[i + 1]] <- 0
      }
    }
    i <- i + 1
  }
  
  ## Then we add our charge and battery levels to the solution and fix it w.r.t. arrival/leave time
  sol[[3]][route_changed[which(route_changed > 0)]] <- charge_vec
  sol[[4]][route_changed[which(route_changed > 0)]] <- battery_vec
  return(sol)
}