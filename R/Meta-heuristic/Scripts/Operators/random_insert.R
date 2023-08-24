random_insert <- function(sol, tabu) {
  ## Inserting the nodes randomly into routes again
  if (is.list(sol[[1]]) == F) {
    sol[[1]] <- list(sol[[1]])
  }
  need_fixing <- sol[[9]]
  # print(sol[[1]])
  # print(need_fixing)
  possibilities <- 1:(n + 1)
  possibilities <- possibilities[-need_fixing]
  for (i in 1:length(need_fixing)) {
    fix_now <- need_fixing[i]
    insert_after <- sample(possibilities, 1)
    possibilities <- c(possibilities, fix_now)
    # print(fix_now)
    # print(insert_after)
    # print(possibilities)
    if (insert_after == (n + 1)) { # Depot ==> new route
      sol[[1]][[length(sol[[1]]) + 1]] <- c(0, fix_now, 0)
      sol[[8]] <- c(sol[[8]], 1) # Extra route, so we have to make sol[[8]] one larger as well
    } else {
      for (j in 1:length(sol[[1]])) {
        if (insert_after %in% sol[[1]][[j]]) {
          route <- sol[[1]][[j]]
          idx_insert_after <- which(route == insert_after)
          sol[[1]][[j]] <- append(route, fix_now, idx_insert_after)
          sol[[8]][j] <- 1
          break() # The node won't be in any of the other routes anymore
        }
      }
    }
  }
  if (is.list(sol[[1]]) == F) {
    sol[[1]] <- list(sol[[1]])
  }
  
  
  if (sum(sol[[8]] == 1) == 0) { # No changes made at all
    sol[[10]] <- sol[[1]]
    return(sol)
  }
  
  ## If solutions stayed the same, we won't have to recalculate them
  # recalc <- sol[[8]] # We still have to recalculate objective value, but no charging
  # for (i in which(sol[[8]] == 1)) {
  #   for (j in 1:length(sol[[10]])) {
  #     if (identical(sol[[1]][[i]],sol[[10]][[j]])) {
  #       sol[[8]][i] <- 0
  #     }
  #   }
  # }
  sol[[10]] <- sol[[1]]
  ## Fixing the solution w.r.t. charging + arrive/leave time
  sol <- local_charge(sol, c())
  sol <- a_z_sol(sol)
  
  ## Calculating new objective value
  # sol[[8]] <- recalc
  sol <- obj_value(sol)
  
  return(sol)
}