accept_sol <- function(sol, s, temperature, cooling_rate) { # sol = current sol, s = previous sol
  if (sum(sol[[7]]) < sum(s[[7]])) { # If current sol is better than previous sol, always accept
    return(c(TRUE, temperature * cooling_rate))
  } else { # Otherwise, we accept if with a certain probability
    # if (sum(sol[[7]]) == sum(s[[7]])) { # Same solution does not get rewarded
    #   return(c(FALSE, temperature))
    # }
    prob_acc <- exp(-(sum(sol[[7]]) - sum(s[[7]])) / temperature)
    #prob_acc <- temperature * sum(s[[7]]) / sum(sol[[7]])
    # Probability acceptance is based on how close to the previous best it was
    accept <- sample(c(TRUE, FALSE), size = 1, prob = c(prob_acc, 1 - prob_acc))
    if (accept) {
      temperature <- temperature * cooling_rate
    }
    return(c(accept, temperature))
  }
}