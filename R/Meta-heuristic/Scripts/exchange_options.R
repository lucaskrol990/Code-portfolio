exchange_options <- function(sol, tabu, exchange_chosen) {
  if (exchange_chosen == 1) {
    sol <- random_split(sol, tabu)
  } else if (exchange_chosen == 2) {
    sol <- distance_split(sol, tabu)
  } else if (exchange_chosen == 3) {
    sol <- exchange_charge(sol, tabu)
  } else if (exchange_chosen == 4) {
    sol <- exchange_charge_unif(sol, tabu)
  } else if (exchange_chosen == 5) {
    sol <- violation_facility_placer(sol, tabu)
  } else {
    print("Error")
  }
  return(sol)
}
