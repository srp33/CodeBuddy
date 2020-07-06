code_file_path = commandArgs()[9]
output_type = commandArgs()[10]

output_file_path = "/sandbox/output"
error_file_path = "/sandbox/error"

exec_text <- function(code) {
  capture.output(eval(parse(text=code)), file=output_file_path)
}

exec_jpg <- function(code) {
  suppressPackageStartupMessages(library(magick))
  fig <- image_graph(bg="white", res=150, clip=FALSE)

  eval(parse(text=code))

  if (!is.null(last_plot()))
    print(last_plot())

  dev.off()

  return(image_write(fig, path=output_file_path, format="jpg", flatten=FALSE))
}

tryCatch({
    code <- readChar(code_file_path, file.info(code_file_path)$size)

    if (output_type == "txt") {
      suppressMessages(suppressWarnings(exec_text(code)))
    } else {
      suppressMessages(suppressWarnings(exec_jpg(code)))
    }
}, warning = function(war) {
    #war$message
}, error = function(err) {
    write(err$message, error_file_path)
}, finally = {
})
