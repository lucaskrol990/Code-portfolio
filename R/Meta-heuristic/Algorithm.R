#```{r}
tot_time <- 1 * 60
options(digits = 10)

intercept <- 118.270771222   
custs <- 0.291625164
custs2 <- -0.002487726
#```

# Load data
#```{r}
inst <- 1
data <- readLines(paste0("./instances/inst", inst, ".csv"))
inst <- as.numeric(data[1])
v <- as.numeric(data[3]) # speed
c_d <- as.numeric(data[4]) # cost of travelling (per distance unit)
b <- as.numeric(data[5]) # battery discharge per distance unit
r <- as.numeric(data[6]) # battery charge per time unit
B <- as.numeric(data[7]) # battery capacity
c_t <- as.numeric(data[8]) # cost of time window violation, per time unit
c_V <- as.numeric(data[9]) # cost of vehicle usage per vehicle
ncoords <- length(data) - 9 # First 9 data points contain no coords
coords <- vector("list", ncoords) # Coordinates
coords[[ncoords]] <- as.numeric(c(strsplit(data[10], ",")[[1]][2], strsplit(data[10], ",")[[1]][3]))
e <- rep(0, ncoords-1) # Start of time window, hard
l <- rep(0, ncoords-1) # End of time window, soft
s <- rep(0, ncoords-1) # Unloading time
c_c <- rep(0, ncoords-1) # Charging station placement costs
for (i in 1:(ncoords-1)) {
  data_split <- as.numeric(strsplit(data[9 + i + 1], ",")[[1]])
  coords[[i]] <- c(data_split[2], data_split[3])
  e[i] <- data_split[4]
  l[i] <- data_split[5]
  s[i] <- data_split[6]
  c_c[i] <- data_split[7]
}
#```



# Calculates distances between nodes
#```{r}
euclidean_distance <- function(coord1, coord2) {
  d_ij <- sqrt((coord1[1] - coord2[1])^2 + (coord1[2] - coord2[2])^2)
  return(d_ij)
}
d <- sapply(coords, function(x) sapply(coords, function(y) euclidean_distance(x,y))) # Distance matrix
colnames(d) <- c(1:(ncoords - 1), 0)
rownames(d) <- c(1:(ncoords - 1), 0)
#```

# Function library
#```{r}
source("./Scripts/Route_to_matrix.R")
source("./Scripts/Mat_to_routes.R")
source("./Scripts/Clarke_wright2.R")
source("./Scripts/add_charge_local.R")
source("./Scripts/obj_value.R")
source("./Scripts/obj_value_route.R")
source("./Scripts/charge_feasibility.R")
source("./Scripts/infeasibility_check.R")
source("./Scripts/list_from_unlist.R")
source("./Scripts/prob_from_weight.R")
source("./Scripts/charge_sol_2.R")
source("./Scripts/a_z_sol.R")
source("./Scripts/fix_charge_new.R")
source("./Scripts/distance_traversed.R")
source("./Scripts/local_charge.R")
source("./Scripts/local_charge_depot.R")

# Node operators
source("./Scripts/Operators/random_removal_S.R")
source("./Scripts/Operators/random_removal_M.R")
source("./Scripts/Operators/random_removal_L.R")
source("./Scripts/Operators/random_insert.R")
source("./Scripts/Operators/pertubed_greedy_insertion.R")
source("./Scripts/Operators/single_point_removal.R")
source("./Scripts/Operators/two_point_removal.R")
source("./Scripts/Operators/binary_removal.R")
source("./Scripts/Operators/random_split.R")
source("./Scripts/Operators/distance_split.R")
source("./Scripts/Operators/early_remove.R")
source("./Scripts/Operators/latest_remove.R")
source("./Scripts/Operators/pertubed_latest_remove.R")
source("./Scripts/Operators/pertubed_early_insert.R")
# Charger location operators
source("./Scripts/Operators/route_facility_removal.R")
source("./Scripts/Operators/route_facility_placement.R")
# Charge percentage operators
source("./Scripts/Operators/exchange_charge.R")
source("./Scripts/Operators/exchange_charge_unif2.R")
source("./Scripts/Operators/violation_facility_placer.R")
# ALNS ./Scripts
source("./Scripts/prob_calc.R")
source("./Scripts/tabu.R")
source("./Scripts/accept_sol.R")
#```

# Construct initial route using the clarke wright savings algorithm
#```{r}
routes <- clarke_wright(d)
#```

# Data structure
#```{r}
n <- ncoords - 1

sol <- list()

sol[[1]] <- routes # List of routes
sol[[2]] <- rep(0,n) # binary vector with charge locations
sol[[3]] <- rep(0,n) # amount charged per location
sol[[4]] <- rep(0,n) # battery level upon arrival
sol[[5]] <- rep(0,n) # arrival times
sol[[6]] <- rep(0,n) # departure times
sol[[7]] <- rep(NA, length(sol[[1]])) # objective value per route
sol[[8]] <- rep(1, length(sol[[1]])) # Indicates in which routes changes have been made
sol[[9]] <- rep(0, n) # Indicates what nodes were removed
sol[[10]] <- routes # old routes
sol[[11]] <- rep(0, n) # How much early you are at your location



sol <- obj_value(a_z_sol(charge_sol(sol, c())))
sol[[8]] <- rep(0, length(sol[[1]]))
#```

#```{r}
n_its <- round(tot_time * (intercept + custs * n + custs2 * n ^ 2))
len_tabu <- ceiling(0.3 * n) # Tabu list length
#```

# Compatibility matrix ALNS
#```{r}
# The node removal/insertion operators
names_node_fix <- c("random_insert", "pertubed_greedy_insertion", "pertubed_early_insert")
names_node_destroy <- c("random_removal_S", "random_removal_M", "single_point_removal", "two_point_removal", "binary_removal", "early_remove", "latest_remove", "pertubed_latest_remove")
compatibility_mat <- matrix(1, nrow = length(names_node_destroy), ncol = length(names_node_fix))
# The facility location operators
names_facility_fix <- c("Route facility placement")
names_facility_destroy <- c("Route facility removal")
for (i in 1:length(names_facility_destroy)) {
  compatibility_mat <- rbind(compatibility_mat, c(rep(0, length(names_node_fix))))
}
rownames(compatibility_mat) <- c(names_node_destroy, names_facility_destroy)
for (i in 1:length(names_facility_fix)) {
  compatibility_mat <- cbind(compatibility_mat, c(rep(0, length(names_node_destroy)), rep(1, nrow(compatibility_mat) - length(names_node_destroy))))
}
colnames(compatibility_mat) <- c(names_node_fix, names_facility_fix)
#```

# Compatibility matrix local improvement
#```{r}
# The node removal/insertion operators
names_node_fix <- c("random_insert", "pertubed_greedy_insertion", "pertubed_early_insert")
names_node_destroy <- c("random_removal_S", "early_remove", "latest_remove", "pertubed_latest_remove")
compatibility_mat_local <- matrix(1, nrow = length(names_node_destroy), ncol = length(names_node_fix))
# The facility location operators
names_facility_fix <- c("Route facility placement")
names_facility_destroy <- c("Route facility removal")
for (i in 1:length(names_facility_destroy)) {
  compatibility_mat_local <- rbind(compatibility_mat_local, c(rep(0, length(names_node_fix))))
}
rownames(compatibility_mat_local) <- c(names_node_destroy, names_facility_destroy)
for (i in 1:length(names_facility_fix)) {
  compatibility_mat_local <- cbind(compatibility_mat_local, c(rep(0, length(names_node_destroy)), rep(1, nrow(compatibility_mat_local) - length(names_node_destroy))))
}
colnames(compatibility_mat_local) <- c(names_node_fix, names_facility_fix)
#```

#```{r}
Local_improvement <- function(sol, time) {
  ptc <- proc.time()
  temperature <- 0.005 * sum(sol[[7]])
  cooling_rate <- (3/4) ^ (1 / (n_its / 10))
  
  remove_options <- list(random_removal_S, early_remove, latest_remove, pertubed_latest_remove, route_facility_removal) # list met functions
  insert_options <- list(random_insert, pertubed_greedy_insertion, pertubed_early_insert, route_facility_placement) # list met functions
  exchange_options <- list(exchange_charge, exchange_charge_unif, violation_facility_placer) # list met functions
  
  weight_remove <- rep(10, length(remove_options))
  weight_insert <- rep(10, length(insert_options))
  weight_exchange <- rep(10, length(exchange_options))
  
  s_best <- sol
  it <- 1
  obj_best <- sum(sol[[7]])
  t_imp_made <- proc.time() # How long ago an improvement was made
  
  while ((proc.time() - ptc)[3] < time) {
    prob_rem_or_ex <- prob_calc(c(sum(weight_remove), sum(weight_exchange)))
    
    rem_or_ex <- sample(c(TRUE, FALSE), 1, prob = prob_rem_or_ex)
    
    if (rem_or_ex) {
      remove_chosen <- sample(1:length(remove_options), 1, prob = prob_calc(weight_remove))
      valid_inserts <- which(compatibility_mat_local[remove_chosen,] == 1)
      if (length(valid_inserts) == 1) {
        insert_chosen <- valid_inserts
      } else {
        insert_chosen <- sample(valid_inserts, 1, prob = prob_calc(weight_insert[valid_inserts]))
      }
      s_prime <- insert_options[[insert_chosen]](remove_options[[remove_chosen]](sol), c())
    } else {
      exchange_chosen <- sample(1:length(exchange_options), 1, prob = prob_calc(weight_exchange))
      s_prime <- exchange_options[[exchange_chosen]](sol, c())
    }
    
    if (sum(s_prime[[7]]) < obj_best) { # If the solution is better than whatever we have found before
      # we will set it as the new best
      t_imp_made <- proc.time()
      obj_best <- sum(s_prime[[7]])
      s_best <- s_prime
      if (it > 1000) { # The first few iterations it is very easy to make an improvement
        if (rem_or_ex) {
          weight_remove[remove_chosen] <- weight_remove[remove_chosen] + 100
          weight_insert[insert_chosen] <- weight_insert[insert_chosen] + 100
        } else {
          weight_exchange[exchange_chosen] <- weight_exchange[exchange_chosen] + 100
        }
      }
    }
    
    ## Update weights
    k <- accept_sol(s_prime, sol, temperature, cooling_rate) # Returns accept, temperature
    temperature <- k[2]
    if (rem_or_ex) {
      if (k[1]) {
        weight_remove[remove_chosen] <- weight_remove[remove_chosen] + ifelse(sum(sol[[7]]) == sum(s_prime[[7]]), 0, 1)
        weight_insert[insert_chosen] <- weight_insert[insert_chosen] + ifelse(sum(sol[[7]]) == sum(s_prime[[7]]), 0, 1)
        sol <- s_prime
      } 
    } else {
      if (k[1]) {
        weight_exchange[exchange_chosen] <- weight_exchange[exchange_chosen] + ifelse(sum(sol[[7]]) == sum(s_prime[[7]]), 0, 1)
        sol <- s_prime
      } 
    }
    
    it <- it + 1
    if ((proc.time() - t_imp_made)[3] > 0.02 * time) { # If we haven't made an improvement for a long time
      t_imp_made <- proc.time()
      sol <- s_best # We reset to the previous best solution
    }
  }
  return(s_best)
}
#```




# ALNS

#```{r}
ALNS <- function(sol) {
  sol <- Local_improvement(sol, 10)
  ptc <- proc.time()
  tabu_list <- c()
  temperature <- 0.5 * sum(sol[[7]])
  cooling_rate <- (3/4) ^ (1 / (n_its / 10))
  reset_done <- 0
  it_imp_made <- 0
  remove_options <- list(random_removal_S, random_removal_M, single_point_removal, two_point_removal, binary_removal, early_remove, latest_remove, pertubed_latest_remove, route_facility_removal) # list met functions
  insert_options <- list(random_insert, pertubed_greedy_insertion, pertubed_early_insert, route_facility_placement) # list met functions
  exchange_options <- list(random_split, distance_split, exchange_charge, exchange_charge_unif, violation_facility_placer) # list met functions
  
  weight_remove <- rep(10, length(remove_options))
  weight_insert <- rep(10, length(insert_options))
  weight_exchange <- rep(10, length(exchange_options))
  
  s_best <- sol
  obj_best <- sum(sol[[7]])
  t_imp_made <- proc.time() # How long ago an improvement was made
  t_big_step <- proc.time()
  it <- 1
  
  while ((proc.time() - ptc)[3] < 0.9 * tot_time) {
    prob_rem_or_ex <- prob_calc(c(sum(weight_remove), sum(weight_exchange)))
    
    rem_or_ex <- sample(c(TRUE, FALSE), 1, prob = prob_rem_or_ex)
    
    if (rem_or_ex) {
      remove_chosen <- sample(1:length(remove_options), 1, prob = prob_calc(weight_remove))
      valid_inserts <- which(compatibility_mat[remove_chosen,] == 1)
      if (length(valid_inserts) == 1) {
        insert_chosen <- valid_inserts
      } else {
        insert_chosen <- sample(valid_inserts, 1, prob = prob_calc(weight_insert[valid_inserts]))
      }
      s_prime <- insert_options[[insert_chosen]](remove_options[[remove_chosen]](sol), tabu_list)
    } else {
      exchange_chosen <- sample(1:length(exchange_options), 1, prob = prob_calc(weight_exchange))
      s_prime <- exchange_options[[exchange_chosen]](sol, tabu_list)
    }
    
    if (sum(s_prime[[7]]) < obj_best) { # If the solution is better than whatever we have found before
      # we will set it as the new best
      t_imp_made <- proc.time()
      t_big_step <- proc.time()
      it_imp_made <- 0
      if ((proc.time() - ptc)[3] > 0.01 * tot_time) { # After 1% of total iterations, we will apply local improvement
        s_prime <- Local_improvement(s_prime, 0.001 * tot_time)
      }
      obj_best <- sum(s_prime[[7]])
      s_best <- s_prime
      if (it > 1000) { # The first few iterations it is very easy to make an improvement
        if (rem_or_ex) {
          weight_remove[remove_chosen] <- weight_remove[remove_chosen] + 100
          weight_insert[insert_chosen] <- weight_insert[insert_chosen] + 100
        } else {
          weight_exchange[exchange_chosen] <- weight_exchange[exchange_chosen] + 100
        }
      }
    }
    
    ## Update weights
    k <- accept_sol(s_prime, sol, temperature, cooling_rate) # Returns accept, temperature
    temperature <- k[2]
    if (rem_or_ex) {
      if (k[1]) {
        sol <- s_prime
        weight_remove[remove_chosen] <- weight_remove[remove_chosen] + ifelse(
          sum(sol[[7]]) == sum(s_prime[[7]]), 0, 1)
        weight_insert[insert_chosen] <- weight_insert[insert_chosen] + ifelse(
          sum(sol[[7]]) == sum(s_prime[[7]]), 0, 1)
      } 
    } else {
      if (k[1]) {
        sol <- s_prime
        weight_exchange[exchange_chosen] <- weight_exchange[exchange_chosen] + ifelse(
          sum(sol[[7]]) == sum(s_prime[[7]]), 0, 1)
      } 
    }
    
    
    
    ## Reset weights at 45% of total iterations
    if (it == round(0.45 * n_its)) {
      weight_remove <- rep(10, length(remove_options))
      weight_insert <- rep(10, length(insert_options))
      weight_exchange <- rep(10, length(exchange_options))
      reset_done <- 1
    }
    
    if (it %% max(round(0.001 * n_its), 100) == 0) { # Update tabu list every 100 iterations or 0.1%
      temp <- tabu(tabu_list, sol, len_tabu, ceiling(0.2 * len_tabu))
      tabu_list <- temp[[1]]
      sol <- temp[[2]]
    }
    
    it <- it + 1
    
    if ((proc.time() - t_big_step)[3] >= 0.3 * tot_time) { # If we suspect we are stuck in a local optimum
      t_big_step <- proc.time()
      temperature <- 0.1 * sum(sol[[7]])
      it_imp_made <- 0
      sol <- random_removal_L(sol)
      sol <- pertubed_greedy_insertion(sol, tabu)
    }
    
  }
  print(paste("Iteration", it))
  return(s_best)
}
#```



# Output to excel
#```{r}
sol <- ALNS(sol)
sol <- Local_improvement(sol, 0.05 * tot_time)
sol[[2]][which(sol[[3]] == 0)] <- 0 # Manually set unused chargers to zero

if (is.list(sol[[1]]) == F) {
  sol[[1]] <- list(sol[[1]])
}

out <- list()

out[[1]] <- inst
out[[2]] <- sum(sol[[7]])
out[[3]] <- length(sol[[1]])
for (i in 1:length(sol[[1]])) {
  out[[3 + i]] <- paste(sol[[1]][[i]], collapse = ",")
}
len_out <- length(out)

# location id, arrival time, battery lvl, charge placed, quantity charged, leave time, time window violation
for (i in 1:n) {
  out[[len_out + i]] <- paste(c(i, sol[[5]][i], sol[[4]][i], sol[[2]][i], sol[[3]][i], sol[[6]][i], max(sol[[6]][i] - l[i], 0)), collapse = ",")
}

df <- as.data.frame(out)
df <- t(df)
colnames(df) <- "A4"
write.csv(df, file = paste0("./Data/sol", inst, ".csv"), row.names = F)
#```