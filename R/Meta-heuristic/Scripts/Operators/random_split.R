# Random split routes operator, randomly selects a route and splits it into two routes at a random point
# Could also make a variation where it splits at the place where the distance between customers is largest

random_split <- function(sol, tabu) {
  curr_route <- sample(1:length(sol[[1]]), 1)
  temp_route <- sol[[1]][[curr_route]]
  temp_route <- temp_route[-c(1, length(temp_route))]
  
  if (length(temp_route) == 1) {
    return(sol)
  }
  
  if (length(temp_route) == 2) {
    r1 <- temp_route[1]
    r2 <- temp_route[2]
    sol[[1]] <- sol[[1]][-curr_route]
    sol[[8]] <- rep(0, length(sol[[1]]))
    sol[[1]][[length(sol[[1]]) + 1]] <- c(0, r1, 0)
    sol[[8]][[length(sol[[1]])]] <- 1
    sol[[1]][[length(sol[[1]]) + 1]] <- c(0, r2, 0)
    sol[[8]][[length(sol[[1]])]] <- 1
    
    # Put already calculated objective values at the right place in sol[[7]]:
    sol[[7]] <- sol[[7]][match(sol[[1]], sol[[10]])]
    
    sol[[10]] <- sol[[1]]
    
    ## Fixing the solution w.r.t. charging + arrive/leave time
    sol <- obj_value(a_z_sol(local_charge(sol, tabu)))
    
    return(sol)
  }
  
  split_at <- sample(2:(length(temp_route) - 1), 1)
  
  r1 <- temp_route[1:split_at]
  r2 <- temp_route[(split_at + 1):length(temp_route)]
  
  sol[[1]] <- sol[[1]][-curr_route]
  sol[[8]] <- rep(0, length(sol[[1]]))
  sol[[1]][[length(sol[[1]]) + 1]] <- c(0, r1, 0)
  sol[[8]][[length(sol[[1]])]] <- 1
  sol[[1]][[length(sol[[1]]) + 1]] <- c(0, r2, 0)
  sol[[8]][[length(sol[[1]])]] <- 1

  # Put already calculated objective values at the right place in sol[[7]]:
  sol[[7]] <- sol[[7]][match(sol[[1]], sol[[10]])]
  
  sol[[10]] <- sol[[1]]

  ## Fixing the solution w.r.t. charging + arrive/leave time
  sol <- obj_value(a_z_sol(charge_sol(sol, tabu)))
  
  return(sol)
}

