local_charge_depot <- function(sol, tabu, begin, route_num, charge_in_route) {
  # print("we gebruiken local charge depot")
  discharge_matrix <- b * d
  # create sub_route from depot to first charger:
  if (begin) {
    sub_route <- route_num[1:charge_in_route[1]]
    sub_mat <- route_to_matrix(sub_route)
    tot_disc <- sum(discharge_matrix * sub_mat)
    
    if (tot_disc == B - sol[[4]][tail(sub_route, 1)]) {
      return(sol) # overbodig maar ff voor het overzicht, slaat dus over als battery upon arrival station 1 plus charge daar - battery level arrival 2 gelijk is aan total discharge
    } else {
      wanted_charge_2 <- sol[[4]][tail(sub_route, 1)] + sol[[3]][tail(sub_route, 1)]
      # Part 1: check if we can reach next charger:
      if (tot_disc <= B) {
        # print("begin 1")
        curr_bat <- B
        for (k in 1:(length(sub_route) - 1)) {
          curr_bat <- curr_bat - discharge_matrix[as.character(sub_route[k]), as.character(sub_route[k + 1])] # update battery level by subtracting distance between nodes
          sol[[4]][sub_route[k + 1]] <- curr_bat # update battery level at arrival of next node
        } # calculate new battery levels between locations
        sol[[3]][tail(sub_route, 1)] <- wanted_charge_2 - curr_bat # we want to charge to what we usually did, so wanted_charge - current battery level is how much we charge
        if (sol[[3]][tail(sub_route, 1)] < 0) { # we have charge left over, dont need charger, too complicated rn
          return(F)
        }
      } else { # Part 3: we cannot make it to next charger location at current battery capacity
        # We have to put down an extra charger, let us find the cheapest location to do so
        # print("begin 2")
        c_c_temp <- c_c
        c_c_temp[tabu] <- 1e4
        valid_idx <- sub_route[2:(length(sub_route)-1)] # valid idx to place charger, so without location 1 and end, cause they are chargers
        charge_avail <- sort(unique(c_c_temp[valid_idx])) # available charge costs
        charge_loc_sort_index <- c()
        for (l in 1:length(charge_avail)) {
          charge_loc_sort_index <- c(charge_loc_sort_index, which(c_c_temp[valid_idx] == charge_avail[l]))
        }
        # now we have a vector that has the location indices sorted on lowest cost
        # ik denk dat we hier gewoon deze vector - tabu kunnen doen en dat het dan werkt, not sure though
        
        # if (length(charge_loc_sort_index) == 0) {
        #   return(charge_sol(sol, tabu)) # just return charge_sol
        # }
        counter <- 0
        for (m in 1:length(charge_loc_sort_index)) {
          cheapest_index <- charge_loc_sort_index[m] + 1
          cheapest_loc <- sub_route[cheapest_index]
          
          # check if charge loc 1 - cheap and cheap - charge loc 2 is less than B
          sub_route_1 <- sub_route[1:cheapest_index]
          sub_route_2 <- sub_route[cheapest_index:length(sub_route)]
          dist1 <- sum(route_to_matrix(sub_route_1) * discharge_matrix)
          dist2 <- sum(route_to_matrix(sub_route_2) * discharge_matrix)
          
          if ((dist1 <= B && dist2 <= B) == F) {
            counter <- counter + 1# location is infeasible
            next # go to next location in charge_loc_sort_index
          } else { # location is feasible
            
            sol[[2]][cheapest_loc] <- 1 # add charger there
            # now we update battery levels
            curr_bat <- B # battery at loc 1
            for (k in 1:(length(sub_route_1) - 1)) { # first part of route
              curr_bat <- curr_bat - discharge_matrix[as.character(sub_route_1[k]), as.character(sub_route_1[k + 1])] # update battery level by subtracting distance between nodes
              sol[[4]][sub_route_1[k + 1]] <- curr_bat # update battery level at arrival of next node
            } # calculate new battery levels between locations
            sol[[3]][cheapest_loc] <- dist2 - sol[[4]][cheapest_loc] # charge so we arrive at loc 2 with 0 charge
            curr_bat <- dist2
            for (k in 1:(length(sub_route_2) - 1)) { # first part of route
              curr_bat <- curr_bat - discharge_matrix[as.character(sub_route_2[k]), as.character(sub_route_2[k + 1])] # update battery level by subtracting distance between nodes
              sol[[4]][sub_route_2[k + 1]] <- curr_bat # update battery level at arrival of next node
            } # calculate new battery levels between locations
            sol[[3]][tail(sub_route, 1)] <- wanted_charge_2 # we should end with 0 charge so sol[[3]] == sol[[4]]
            break
          }
        }
        if (counter == length(charge_loc_sort_index)) {
          return(F) # just return charge_sol
        }
        # now if we went through the for loop above without ever meeting requirement of distances to be feasible, we will need 2 chargers in this part
        # as this becomes incredibly difficult to code "smartly" as above, we will use the idea of charge_sol to rigorously fix this part of the route w.r.t. charging
      }
    }
    
    
  } else { #end of route
    sub_route <- route_num[tail(charge_in_route, 1):length(route_num)]
    sub_mat <- route_to_matrix(sub_route)
    tot_disc <- sum(discharge_matrix * sub_mat)
    
    tail_sub_batt <- sol[[4]][(tail(sub_route, 2)[1])] - discharge_matrix[as.character(tail(sub_route, 2)[1]), "0"]
    if (tot_disc == sol[[4]][sub_route[1]] + sol[[3]][sub_route[1]] - max(tail_sub_batt, 0)) {
      return(sol) # overbodig maar ff voor het overzicht, slaat dus over als battery upon arrival station 1 plus charge daar - battery level arrival 2 gelijk is aan total discharge
    } else { # we know we found an issue, let's fix
      # We will fix this in three increasingly complicated parts
      wanted_charge_2 <- 0 # we want to aim at reaching the depot with 0 charge
      # print("end 1")
      sol[[3]][sub_route[1]] <- min(B - sol[[4]][sub_route[1]], sol[[3]][sub_route[1]]) # this checks if we dont overcharge because the distance traveled before shrunk, should never trigger but will leave it in for now
      
      if (tot_disc < sol[[4]][sub_route[1]]) { # we have too much battery even before charging
        # too complicated for now
        return(charge_sol(sol, tabu))
      } else if (tot_disc >= sol[[4]][sub_route[1]] & tot_disc <= B) { # we do need charging in order to reach end AND we can get all that charge in 1 battery
        sol[[3]][sub_route[1]] <- tot_disc - sol[[4]][sub_route[1]] # charge the exact right amount
        curr_bat <- tot_disc
        if (length(sub_route) - 2 >= 1) { # if sub_route is only last location in route where we have charger, we need no further calculations
          for (k in 1:(length(sub_route) - 2)) { # fix rest of route, minus 2 cause we dont want to calculate for depot, we can do this since we calculated the exact amount needed anyway so we know we will make it
            curr_bat <- curr_bat - discharge_matrix[as.character(sub_route[k]), as.character(sub_route[k + 1])] # update battery level by subtracting distance between nodes
            sol[[4]][sub_route[k + 1]] <- curr_bat # update battery level at arrival of next node
          }
        }
 
      } else if (tot_disc >= B) { # we cannot make it to next charger location at current battery capacity
                                    # We have to put down an extra charger, let us find the cheapest location to do so
        # print("end 2")
        c_c_temp <- c_c
        c_c_temp[tabu] <- 1e4
        valid_idx <- sub_route[2:(length(sub_route)-1)] # valid idx to place charger, so without location 1 and end, cause they are chargers
        charge_avail <- sort(unique(c_c_temp[valid_idx])) # available charge costs
        charge_loc_sort_index <- c()
        for (l in 1:length(charge_avail)) {
          charge_loc_sort_index <- c(charge_loc_sort_index, which(c_c_temp[valid_idx] == charge_avail[l]))
        }
        counter <- 0
        for (m in 1:length(charge_loc_sort_index)) {
          cheapest_index <- charge_loc_sort_index[m] + 1
          cheapest_loc <- sub_route[cheapest_index]
          
          # check if charge loc 1 - cheap and cheap - charge loc 2 is less than B
          sub_route_1 <- sub_route[1:cheapest_index]
          sub_route_2 <- sub_route[cheapest_index:length(sub_route)]
          dist1 <- sum(route_to_matrix(sub_route_1) * discharge_matrix)
          dist2 <- sum(route_to_matrix(sub_route_2) * discharge_matrix)
          
          if ((dist1 <= B && dist2 <= B) == F) {
            counter <- counter + 1# location is infeasible
            next # go to next location in charge_loc_sort_index
          } else { # location is feasible
            if (dist1 > sol[[3]][sub_route[1]] + sol[[4]][sub_route[1]]) {
              sol[[3]][sub_route[1]] <- dist1 - sol[[4]][sub_route[1]]
            }
            
            sol[[2]][cheapest_loc] <- 1 # add charger there
            # now we update battery levels
            curr_bat <- sol[[4]][sub_route_1[1]] + sol[[3]][sub_route_1[1]] # battery at loc 1
            for (k in 1:(length(sub_route_1) - 1)) { # first part of route
              curr_bat <- curr_bat - discharge_matrix[as.character(sub_route_1[k]), as.character(sub_route_1[k + 1])] # update battery level by subtracting distance between nodes
              sol[[4]][sub_route_1[k + 1]] <- curr_bat # update battery level at arrival of next node
            } # calculate new battery levels between locations
            sol[[3]][cheapest_loc] <- dist2 - sol[[4]][cheapest_loc] # charge so we arrive at loc 2 with 0 charge
            curr_bat <- dist2
            if (length(sub_route_2) - 2 >= 1) {
              for (k in 1:(length(sub_route_2) - 2)) { # second part of route, -2 cause we dont want to calculate for depot
                curr_bat <- curr_bat - discharge_matrix[as.character(sub_route_2[k]), as.character(sub_route_2[k + 1])] # update battery level by subtracting distance between nodes
                sol[[4]][sub_route_2[k + 1]] <- curr_bat # update battery level at arrival of next node
              } # calculate new battery levels between locations
            } 
            break
          }
        }
        if (counter == length(charge_loc_sort_index)) {
          return(charge_sol(sol, tabu)) # just return charge_sol
        }
        
      }
    }
  }
  return(sol)
}
