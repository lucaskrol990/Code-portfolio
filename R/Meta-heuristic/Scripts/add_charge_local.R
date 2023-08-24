# This function will do the following:
# First:
# - Can we still reach next charger with current charge?
# - If so, only charge more add next location
# - If not, go to second
# 
# Second:
#   - If so, only edit the charges. Do this by adding the extra discharge as charge at the last node with a charging station, given that one does not overcharge. 
# - If one does overcharge, go to third
# 
# Third: 
#   - Is it possible to follow the route without having less than zero charge. I.e., the discharge from charging location to charging location should be less than B
# - Charge (extra discharge - amount extra charged at last node) at next node with charging station
# 
# Fourth: 
#   - Add charging station at new node
# - Make sure you still have the same charge at next node with charging station as in the previous solution
# 
# sol[[1]] <- routes # route matrix
# sol[[2]] <- charger_locations # binary vector with charge locations
# sol[[3]] <- charge_amount # amount charged per location
# sol[[4]] <- battery_lvl # battery level upon arrival
# sol[[5]] <- a # arrival times
# sol[[6]] <- z # departure times
# sol[[7]] <- obj_vec # objective value per route
# sol[[8]] <- mat_to_routes(routes) # List of routes
# sol[[9]] <- rep(0, length(sol[[8]])) # Indicates in which routes changes have been made

add_charge_local <- function(sol) {
  discharge_mat <- b * d
  routes_need_fixing <- which(sol[[9]] > 0)
  # First: reach next charger with current charge
  for (i in routes_need_fixing) {
    curr_route <- sol[[8]][i]
    for (j in 1:(length(curr_route) - 1)) {
      next_dist <- discharge_mat[curr_route[i], curr_route[i + 1]]
    }
  }
}
