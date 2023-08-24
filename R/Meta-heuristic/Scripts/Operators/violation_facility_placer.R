## Idea: charging large amounts means you pay more time window violation costs
## so, place extra chargers at place where you are unloading already anyway

violation_facility_placer <- function(sol, tabu, n = 5, q = 2) {
  ## First we find the facilities to target
  charge_amounts_sorted <- sort(sol[[3]], decreasing = T)[1:n]
  if (q == 1) {
    charge_target <- charge_amounts_sorted
  } else {
    charge_target <- sample(charge_amounts_sorted, size = q)
  }
  target_facilities <- c()
  for (i in 1:length(charge_target)) {
    target_facilities <- c(target_facilities, which(sol[[3]] == charge_target[i]))
  }
  # print("In violation")
  ## Then we loop through them
  for (i in target_facilities) {
    # print("In loop")
    # We find in which route this facility can be found
    for (j in 1:length(sol[[1]])) {
      if (i %in% sol[[1]][[j]]) {
        break # Facility is in route j
      }
    }
    
    # We isolate this route
    route <- sol[[1]][[j]]
    route <- route[route > 0]
    old_charger_idx <- which(route == i)
    # Find if there are chargers before this charger
    if (old_charger_idx == 1) { # Charger is at first location, so we can't add charger before
      next
    }
    before_idx <- which(sol[[2]][route[1:(old_charger_idx - 1)]] == 1)
    if (length(before_idx) == 0) { # No charger before
      sub_route <- route[1:(old_charger_idx - 1)]
    } else {
      if (max(before_idx) + 1 == old_charger_idx) { # Already a charger directly before it
        sub_route <- c()
      } else {
        sub_route <- route[(max(before_idx) + 1):(old_charger_idx - 1)]
      }
      
    }
    if (length(sub_route) == 0) { # Nothing inbetween the two chargers
      next
    }
    # We add our new charger at a spot in the route where the ratio of cost over free charge is minimized, sampled
    c_c_temp <- c_c
    c_c_temp[tabu] <- 1000000
    cost_chargers <- c_c_temp[sub_route] / s[sub_route]
    cost_charger_sorted <- sort(cost_chargers)[1:min(3, length(cost_chargers))]
    if (length(cost_charger_sorted) == 1) {
      placement_cost <- cost_charger_sorted
    } else {
      placement_cost <- sample(cost_charger_sorted, size = 1)
    }
    #cost_charger_sorted <- sort(cost_chargers, decreasing = T)[1:min(3, length(cost_chargers))]
    # placement_cost <- sample(cost_charger_sorted, size = 1)
    place_in_sub <- which(cost_chargers == placement_cost)[1]
    placement_idx <- sub_route[place_in_sub]
    sol[[2]][placement_idx] <- 1
    # We then add charge here for as long as the EV is unloading, given that we do not overcharge the vehicle
    sol[[3]][placement_idx] <- min(B - sol[[4]][placement_idx], s[placement_idx] * r, sol[[3]][i], sol[[4]][i])
    # print(placement_idx)
    # print(sol[[2]][placement_idx])
    # print(sol[[3]][placement_idx])
    # print(sub_route)
    # print(sol[[3]][i])
    # We can then charge this amount less at the old charger
    sol[[3]][i] <- sol[[3]][i] - sol[[3]][placement_idx]
    # print(sol[[3]][i])
    sol[[4]][i] <- sol[[4]][i] + sol[[3]][placement_idx]
    # print(sol[[4]][sub_route])
    # We now only need to adjust the battery levels accordingly and indicate the route was changed
    if (place_in_sub < length(sub_route)) {
      sol[[4]][sub_route[(place_in_sub + 1):length(sub_route)]] <- 
        sol[[4]][sub_route[(place_in_sub + 1):length(sub_route)]] + sol[[3]][placement_idx]
    }
    # print(sol[[4]][sub_route])
    sol[[8]][j] <- 1
  }
  sol <- obj_value(a_z_sol(sol))
  return(sol)
}