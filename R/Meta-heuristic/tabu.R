tabu <- function(tabu, sol, m, k) {
  charge_costs <- c_c * sol[[2]]
  charge_costs <- charge_costs / sol[[3]]
  charge_costs[tabu] <- 0 # Set it very small such that it is never chosen as new tabu location 
  is_infeasible <- T
  
  i <- 1
  worst_locs <- order(charge_costs, decreasing = T)[1:m]
  remove_locs <- sample(worst_locs, k)
  # while (m > 0 && is_infeasible) {
  #   worst_locs <- order(charge_costs, decreasing = T)[1:m]
  #   remove_locs <- sample(worst_locs, k)
  #   if (sum(which(charge_sol(sol, remove_locs)[[2]] == 1) %in% tabu) == 0) { 
  #     # If V_charge was not forced to put a charger on a tabu spot
  #     is_infeasible <- F
  #   }
  #   
  #   if (k <= m) {
  #     m <- m - 1
  #   }
  #   if (k == m) {
  #     k <- k - 1
  #   }
  #   
  # }
  tabu <- c(tabu, remove_locs)
  if (length(tabu) > len_tabu) { # Length of tabu list is 5
    tabu <- tabu[-(1:(length(tabu) - len_tabu))]
  }
  #sol <- charge_sol(sol, tabu) # Remove chargers from solution, if possible
  return(list(tabu, sol))
}