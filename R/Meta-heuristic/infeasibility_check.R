infeasibility_check <- function(sol) {
  test_mat <- route_to_matrix(sol[[1]])
  ## Route feasibility 
  if (sum(rowSums(test_mat[1:n, ]) == 1) < n && sum(colSums(test_mat[, 1:n]) == 1) < n) { # check if you leave and enter every customer once
    print("Went to the same customer multiple times")
    return(FALSE)
  }
  
  if (sum(test_mat[n + 1, ]) != sum(test_mat[, n + 1])) { # check if you leave depot as much as you enter
    print("Left (entered) depot more than entered (left)")
    return(FALSE)
  }
  
  temp_routes <- mat_to_routes(test_mat)
  if (is.list(temp_routes) == FALSE) { # check if mat_to_routes didn't encounter a loop
    print("Loop in route")
    return(FALSE)
  }
  
  if (sum(unlist(temp_routes) > 0) != n) { # check if every customer is visited
    print("Not every customer was visited")
    return(FALSE)
  }
  
  ## Time feasibility
  if (sum(sol[[6]] <= sol[[5]]) > 0) { # cannot leave before arriving
    print("Left before entering")
    return(FALSE)
  }
  
  # Is misschien wat veel werk en niet per se de belangrijkste check, ook niet precies dus geeft problemen.
  # if (sum((sol[[6]] - s - sol[[3]] / r) == (sol[[5]] - (sol[[5]] - e) * (e - sol[[5]] > 0))) < n) { # Arrival time = leave time - time charged - unloading time
  #   return(FALSE)
  # }
  
  ## Charging feasibility
  if (sum(1 - charge_feasibility(sol, 1:length(sol[[1]]))) != 0) { # Infeasible with respect to charging
    return(FALSE)
  }
  
  ## Right objective values
  temp_sol <- sol
  temp_sol[[8]] <- rep(1, length(temp_sol[[1]]))
  if (sum(obj_value(temp_sol)[[7]]) != sum(sol[[7]])) {
    print(sum(obj_value(temp_sol)[[7]]) - sum(sol[[7]]))
    print("Incorrect obj values")
    return(FALSE)
  }
  
  return(TRUE)
}