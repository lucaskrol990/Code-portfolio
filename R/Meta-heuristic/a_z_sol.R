# arrive leave combine

a_z_sol <- function(sol) {
  for (k in which(sol[[8]] == 1)) {
    route <- as.character(sol[[1]][[k]])
    t <- 0
    #print(route)
    for (i in 1:(length(route) - 2)) {
      j <- as.numeric(route[i + 1]) # Needs numeric since we access e[j] etc.
      #print(j)
      t <- t + d[route[i], j] / v
      #print(t)
      #print(e[j])
      #print(c(t, e[j]))
      if (t < e[j]) { # If you arrived early
        sol[[11]][j] <- e[j] - t # You were this many units early
        t <- e[j] # You wait till you can serve 
      }
      sol[[5]][j] <- t
      t <- t + max(s[j], sol[[3]][j] / r) # Unloading time / Time spent charging
      sol[[6]][j] <- t # Time you leave
    }
  }
  return(sol)
}
