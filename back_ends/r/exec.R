code_file_path = commandArgs()[9]
output_type = commandArgs()[10]

exec_jpg <- function(code) {
  library(magick)
  library(ggplot2)

  fig <- image_graph(bg="white", res=150, clip=FALSE)

  eval(parse(text=code))

  if (!is.null(ggplot2::last_plot()))
    print(ggplot2::last_plot())

  dev.off()

  return(image_write(fig, path="/sandbox/image_output", format="jpg", flatten=FALSE))
}

code <- readChar(code_file_path, file.info(code_file_path)$size)

if (output_type == "txt") {
  suppressMessages(suppressWarnings(suppressPackageStartupMessages(eval(parse(text=code)))))
} else {
  suppressMessages(suppressWarnings(suppressPackageStartupMessages(exec_jpg(code))))
}
