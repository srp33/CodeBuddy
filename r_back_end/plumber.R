libraries <- scan('/libraries', what=character(), quiet=TRUE)
for (l in libraries)
  library(l, character.only = TRUE)

#* This function can get used to test connectivity to the API.
#* @get /hello
#' @html
function(res) {
    return(paste0("Hello, world"))
}

#* Execute code to generate text output.
#* @param code The code to execute
#* @param timeout_seconds How long the code should execute before timing out
#* @param output_type The type of output to create (txt, jpg)
#* @post /exec
#' @html
function(res, code, timeout_seconds, output_type) {
    clean_temp()
    env = environment()

    local({
        tryCatch({
            setTimeLimit(elapsed = timeout_seconds, transient = TRUE)
            on.exit(setTimeLimit(Inf, Inf, FALSE))

            lockEnvironment(env, binding=TRUE)

            tmp_dir_path = paste0("/tmp/", create_id())
            on.exit(unlink(tmp_dir_path, recursive=TRUE, force=TRUE))
            dir.create(tmp_dir_path)
            setwd(tmp_dir_path)

            if (output_type == "txt") {
              res$body <- suppressMessages(suppressWarnings(exec_text(code)))
            } else {
              res$body <- suppressMessages(suppressWarnings(exec_jpg(code)))
            }
        }, warning = function(war) {
            #return(paste0("Warning message:\n", war$message))
        }, error = function(err) {
            res$body <- paste0("Error: ", err$message)
            res$status <- 400
        }, finally = {
        })
    })

    res
}

exec_text <- function(code) {
  return(paste(capture.output(eval(parse(text=code)), type="output"), collapse="\n"))
}

exec_jpg <- function(code) {
  fig <- image_graph(bg="white", res=150, clip=FALSE)

  eval(parse(text=code))

  if (!is.null(last_plot()))
    print(last_plot())

  dev.off()

  return(image_write(fig, path=NULL, format="jpg", flatten=FALSE))
}

create_id <- function(){
  pool <- c(letters, LETTERS, 0:9)
  
  n <- 20
  res <- character(n)
  for(i in seq(n)){
    res[i] <- sample(pool, 1)
  }

  paste(res, collapse="")
}

clean_temp = function(keep_minutes=30) {
  file_info = file.info(list.files("/tmp", pattern=glob2rx("*"), full.names=TRUE, include.dirs=TRUE), extra_cols =    FALSE)
  file_info = file_info[difftime(Sys.time(), file_info[,"mtime"], units = "mins") > keep_minutes, 1:2]
  
  tryCatch({
    for (name in rownames(file_info))
    {
      value = unlink(name, recursive = TRUE, force=TRUE)
    }
  }, warning = function(war) {
    #print(war$message)
  }, error = function(err) {
    #print(err$message)
  }, finally = {
  })
}
