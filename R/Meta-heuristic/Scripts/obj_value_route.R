obj_value_route <- function(route) {
  route_mat <- route_to_matrix(route)
  idx <- route[route > 0]
  return(c_V + sum(c_d * (d * route_mat)) + c_t * sum((z[idx] - l[idx]) * (z[idx] > l[idx])) + sum(c_c[idx] * charger_locations[idx]))
}
obj_value_route <- Vectorize(obj_value_route, "route")
