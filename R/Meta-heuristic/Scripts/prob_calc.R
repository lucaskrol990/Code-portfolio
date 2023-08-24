prob_calc <- function(w) {
  p_vec <- rep(0, length(w))
  if (min(w) < (0.3 / length(w)) * sum(w)) {
    # calc prob with scaling from min
    k <- which(w == min(w))
    p_vec[k] <- 0.3 / length(w)
    w <- w - min(w)
    p_vec <- p_vec +  w / sum(w) * (1 - (0.3 / length(w) * length(k)))
  } else {
    p_vec <- w / sum(w)
  }
  return(p_vec)
}
