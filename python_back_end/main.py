from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def hello():
    return "World"

#@app.post("/items/{item_id}")
#@app.get("/items/{item_id}")
#def read_item(item_id: int, q: str = None):
#    return {"item_id": item_id, "q": q}

#@app.post("/items/{item_id}")
@app.get("/exec")
def exec(code: str, timeout_seconds: int, output_type: str)
    print("got here")
#    clean_temp()

#    tmp_dir_path = paste0("/tmp/", create_id())
#
#        tryCatch({
#            setTimeLimit(elapsed = timeout_seconds, transient = TRUE)
#            #on.exit(setTimeLimit(Inf, Inf, FALSE))
#
#            lockEnvironment(env, binding=TRUE)
#
#            #on.exit(unlink(tmp_dir_path, recursive=TRUE, force=TRUE))
#            dir.create(tmp_dir_path)
#            setwd(tmp_dir_path)
#
#            if (output_type == "txt") {
#              res$body <- suppressMessages(suppressWarnings(exec_text(code)))
#            } else {
#              res$body <- suppressMessages(suppressWarnings(exec_jpg(code)))
#            }
#        }, warning = function(war) {
#            #return(paste0("Warning message:\n", war$message))
#        }, error = function(err) {
#            res$body <- paste0("Error: ", err$message)
#            res$status <- 400
#        }, finally = {
#            setwd("/")
#            unlink(tmp_dir_path, recursive=TRUE, force=TRUE)
#            setTimeLimit(Inf, Inf, FALSE)
#        })
#    })
#
#    res
#}
