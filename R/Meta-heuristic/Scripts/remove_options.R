remove_options <- function(sol, remove_chosen) {
  if (remove_chosen == 1) {
    sol <- random_removal_M(sol)
  } else if (remove_chosen == 2) {
    sol <- single_point_removal(sol)
  } else if (remove_chosen == 3) {
    sol <- two_point_removal(sol)
  } else if (remove_chosen == 4) {
    sol <- binary_removal(sol)
  } else if (remove_chosen == 5) {
    sol <- early_remove(sol)
  } else if (remove_chosen == 6) {
    sol <- latest_remove(sol)
  } else if (remove_chosen == 7) {
    sol <- pertubed_latest_remove(sol)
  } else if (remove_chosen == 8) {
    sol <- route_facility_removal(sol)
  } else {
    print("Error")
  }
  return(sol)
}
