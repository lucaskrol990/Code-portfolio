insert_options <- function(sol, tabu, insert_chosen) {
  if (insert_chosen == 1) {
    sol <- random_insert(sol, tabu)
  } else if (insert_chosen == 2) {
    sol <- pertubed_greedy_insertion(sol, tabu)
  } else if (insert_chosen == 3) {
    sol <- pertubed_early_insert(sol, tabu)
  } else if (insert_chosen == 4) {
    sol <- route_facility_placement(sol, tabu)
  } else {
    print("Error")
  }
  return(sol)
}
