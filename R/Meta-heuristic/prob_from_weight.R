# Old probabilities + if it was a succes or not + index of succes/failure
prob_from_weight <- function(weight) { 
  prob <- rep(0, length(weight))
  add_to_min <- 0 # Will store how much we added to weights in probability
  exc_weight <- rep(0, length(weight))
  for (i in which(weight / sum(weight) < 0.5 / length(weight))) { # For the ones with too small weight
    add_to_min <- add_to_min + 0.5 / length(weight) - weight[i] / sum(weight)
    prob[i] <- 0.5 / length(weight)
  }
  
  perf_idxs <- which(weight / sum(weight) > 0.5 / length(weight))
  for (i in perf_idxs) { # Loop through the ones with performance bonus
    exc_weight[i] <- weight[i] / sum(weight) - 0.5 / length(weight)
  }
  # For the better performing 
  prob[perf_idxs] <- weight[perf_idxs] / sum(weight) - (exc_weight[perf_idxs] / sum(exc_weight)) * add_to_min
  return(prob)
}