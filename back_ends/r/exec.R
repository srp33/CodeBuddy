code_file_path = commandArgs()[9]
output_type = commandArgs()[10]

#output_file_path = "/sandbox/output"
#error_file_path = "/sandbox/error"

exec_jpg <- function(code) {
  #suppressPackageStartupMessages(library(magick))
  #suppressPackageStartupMessages(library(ggplot2))
  library(magick)
  library(ggplot2)

  fig <- image_graph(bg="white", res=150, clip=FALSE)

  eval(parse(text=code))

  if (!is.null(ggplot2::last_plot()))
    print(ggplot2::last_plot())

  dev.off()

  return(image_write(fig, path="/sandbox/image_output", format="jpg", flatten=FALSE))
}

#tryCatch({
    code <- readChar(code_file_path, file.info(code_file_path)$size)

    if (output_type == "txt") {
      #capture.output(suppressMessages(suppressWarnings(exec_text(code))), file=output_file_path)
      #capture.output(eval(parse(text=code)), file=output_file_path)
      suppressPackageStartupMessages(eval(parse(text=code)))
    } else {
      #suppressMessages(suppressWarnings(exec_jpg(code)))
      #TODO: print the result of exec_jpg to standard out?
      suppressPackageStartupMessages(code)
    }
#}, warning = function(war) {
#    #war$message
#}, error = function(err) {
#    write(err$message, error_file_path)
#}, finally = {
#})
