library(plumber)

r <- plumb("plumber.R")

lockEnvironment(environment())

r$run(host='0.0.0.0', port=9001)
