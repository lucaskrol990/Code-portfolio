## This function puts new nodes before nodes which arrive too early at location
## and therefore have to wait
pertubed_early_insert <- function(sol, tabu) {
  need_fixing <- sol[[9]]
  possibilities <- 1:(n)
  possibilities <- possibilities[-need_fixing]
  if (is.list(sol[[1]]) == F) {
    sol[[1]] <- list(sol[[1]])
  }
  
  for (i in 1:length(need_fixing)) {
    fix_now <- need_fixing[i]
    criterion <- runif(length(possibilities), 0.7, 1.3) * sol[[11]][possibilities]
    insert_before <- possibilities[which.max(criterion)]
    for (j in 1:length(sol[[1]])) {
      if (insert_before %in% sol[[1]][[j]]) {
        route <- sol[[1]][[j]]
        idx_insert_before <- which(route == insert_before) - 1 # -1 because append does after idx
        route <- append(route, fix_now, idx_insert_before)
        sol[[1]][[j]] <- route
        sol[[8]][j] <- 1
        sol[[11]][fix_now] <- 0 # Too computationally expensive to actually calculate this
        # Update the arrival times (very simply, does not take charging into account)
        for (j in (idx_insert_before + 1):(length(route) - 1)) {
          sol[[11]][route[j + 1]] <- sol[[11]][route[j + 1]] - d[route[j], route[j + 1]]
        }
        
        break() # The node won't be in any of the other routes anymore
      }
    }
  }
  
  if (is.list(sol[[1]]) == F) {
    sol[[1]] <- list(sol[[1]])
  }
  
  # Put already calculated objective values at the right place in sol[[7]]:
  recalc <- sol[[8]] # We still have to recalculate objective value, but no charging
  for (i in which(sol[[8]] == 1)) {
    for (j in 1:length(sol[[10]])) {
      if (identical(sol[[1]][[i]],sol[[10]][[j]])) {
        sol[[8]][i] <- 0
      }
    }
  }
  sol[[10]] <- sol[[1]]
  ## Fixing the solution w.r.t. charging + arrive/leave time
  sol <- local_charge(sol, c())
  sol <- a_z_sol(sol)
  
  ## Calculating new objective value
  sol[[8]] <- recalc
  sol <- obj_value(sol)
  
  return(sol)
}