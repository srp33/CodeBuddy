library(plumber)

r <- plumb("plumber.R")

port <- as.integer(Sys.getenv("PORT"))
print(paste0("Running on port, ", port))

lockEnvironment(environment())

r$run(host='0.0.0.0', port=port)
