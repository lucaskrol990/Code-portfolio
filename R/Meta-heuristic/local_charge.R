local_charge <- function(sol, tabu) {
  if (sum(sol[[8]]) == 0) {
    return(sol)
  }

  discharge_matrix <- b * d
  
  routes_changed <- sol[[1]][which(sol[[8]] == 1)]
  
  for (i in 1:length(routes_changed)) {
    route_num <- routes_changed[[i]]
    
    if (sum(sol[[2]][route_num]) < 2) { # zero or only 1 charger 
      return(charge_sol(sol, tabu)) # return sol feasible on entire route ("drastic way")
    }
      
    
    charge_in_route <- which(sol[[2]][route_num] == 1) + 1 # +1 because of depot
    
    sol_dummy <- local_charge_depot(sol, tabu, T, route_num, charge_in_route)
    
    if (is.list(sol_dummy) == F) {
      return(charge_sol(sol, tabu))
    } else {
      sol <- sol_dummy
    }
    

    
    
    
    
    
    # We want to start checking between each set of 2 charging operators
    # charge_in_route <- route_num[route_num %in% which(sol[[2]] == 1)] # find location indices in route that have charger
    for (j in 1:(length(charge_in_route) - 1)) {
      sub_route <- route_num[charge_in_route[j]:charge_in_route[j + 1]] # route part between locations
      # Now we want to check feasibility in this part, i.e. is charge level at second location unchanged
      # so sum distances between customers in this part and check if discharge is equal
      sub_mat <- route_to_matrix(sub_route)
      tot_disc <- sum(discharge_matrix * sub_mat)
      
      if (tot_disc == sol[[4]][sub_route[1]] + sol[[3]][sub_route[1]] - sol[[4]][tail(sub_route, 1)]) {
        next # overbodig maar ff voor het overzicht, slaat dus over als battery upon arrival station 1 plus charge daar - battery level arrival 2 gelijk is aan total discharge
      } else { # we know we found an issue, let's fix
        # We will fix this in three increasingly complicated parts
        wanted_charge_2 <- sol[[4]][tail(sub_route, 1)] + sol[[3]][tail(sub_route, 1)] # battery level upon leaving charging location 2
        
        sol[[3]][sub_route[1]] <- min(B - sol[[4]][sub_route[1]], sol[[3]][sub_route[1]]) # this checks if we dont overcharge because the distance traveled before shrunk
        
        # Part 1: Check if we can reach the next charger without charging more 
        if (tot_disc <= sol[[4]][sub_route[1]] + sol[[3]][sub_route[1]]) {
          # print("part 1")
          curr_bat <- sol[[4]][sub_route[1]] + sol[[3]][sub_route[1]]
          for (k in 1:(length(sub_route) - 1)) {
            curr_bat <- curr_bat - discharge_matrix[as.character(sub_route[k]), as.character(sub_route[k + 1])] # update battery level by subtracting distance between nodes
            sol[[4]][sub_route[k + 1]] <- curr_bat # update battery level at arrival of next node
          } # calculate new battery levels between locations
          sol[[3]][tail(sub_route, 1)] <- wanted_charge_2 - curr_bat # we want to charge to what we usually did, so wanted_charge - current battery level is how much we charge
          if (sol[[3]][tail(sub_route, 1)] < 0) {
            # we have charge left over, dont need charger, too complicated rn
            return(charge_sol(sol, tabu))
          }
        } else if (tot_disc <= B) { # Part 2: If it cannot make it at current battery level, add charge to charge loc 1, provided that the distance can be traversed in one battery charge
          # print("part 2")
          sol[[3]][sub_route[1]] <- tot_disc - sol[[4]][sub_route[1]]
          # charge to tot_disc at charge loc 1, we will arrive at charge loc 2 with zero charge, which is fine
          curr_bat <- tot_disc
          for (k in 1:(length(sub_route) - 1)) {
            curr_bat <- curr_bat - discharge_matrix[as.character(sub_route[k]), as.character(sub_route[k + 1])] # update battery level by subtracting distance between nodes
            sol[[4]][sub_route[k + 1]] <- curr_bat # update battery level at arrival of next node
          } # calculate new battery levels between locations
          # we are now at 0 charge at charge location 2, so we charge wanted_charge_2 there exactly
          sol[[3]][tail(sub_route, 1)] <- wanted_charge_2
        } else { # Part 3: we cannot make it to next charger location at current battery capacity
          # We have to put down an extra charger, let us find the cheapest location to do so
          # print("part 3")
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
              for (k in 1:(length(sub_route_2) - 1)) { # first part of route
                curr_bat <- curr_bat - discharge_matrix[as.character(sub_route_2[k]), as.character(sub_route_2[k + 1])] # update battery level by subtracting distance between nodes
                sol[[4]][sub_route_2[k + 1]] <- curr_bat # update battery level at arrival of next node
              } # calculate new battery levels between locations
              sol[[3]][tail(sub_route, 1)] <- wanted_charge_2 # we should end with 0 charge so sol[[3]] == sol[[4]]
              break
            }
          }
          if (counter == length(charge_loc_sort_index)) {
            return(charge_sol(sol, tabu)) # just return charge_sol
          }
          # now if we went through the for loop above without ever meeting requirement of distances to be feasible, we will need 2 chargers in this part
          # as this becomes incredibly difficult to code "smartly" as above, we will use the idea of charge_sol to rigorously fix this part of the route w.r.t. charging
         
          ### ATTENTIE VERBETERING:
          # - eerst alle veranderde routes door en dan charge sol op rest toepassen, nu doet ie charge sol op de hele boel bij de eerste aangepaste route waar dit niet werkt
          # - wellicht kunnen we t wel smart/hard coden hierin, maar nu ff geen idee hoe
          # - als minder dan 2 chargers moet skippen naar volgende edited route niet returnen
        }
      }
    }
    
    sol <- local_charge_depot(sol, tabu, F, route_num, charge_in_route)
  }
  
  return(sol) # return new solution
  # als ik het goed begrijp willen we deze callen in insertion etc functions, 
  # hier doen we al alles behalve charge feasible maken erbuiten right?
}
