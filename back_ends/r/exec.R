code_file_path = commandArgs()[9]
output_type = commandArgs()[10]

# Code that didn't work right for both base R graphics and ggplot2
#exec_jpg <- function(code) {
#  library(magick)
#  library(ggplot2)
#
#  fig <- image_graph(bg="white", res=150, clip=FALSE)
#
#  eval(parse(text=code))
#
#  if (!is.null(ggplot2::last_plot()))
#    print(ggplot2::last_plot())
#
#  dev.off()
#
#  return(image_write(fig, path="/sandbox/image_output", format="jpg", flatten=FALSE))
#}

exec_jpg <- function(code) {
  library(ggplot2)

  pdf(NULL) # Prevents Rplots.pdf from being created.

  eval(parse(text=code))
  ggsave("/sandbox/image_output", dpi = 150, device = "jpeg")
}

code <- readChar(code_file_path, file.info(code_file_path)$size)

if (output_type == "txt") {
  suppressMessages(suppressWarnings(suppressPackageStartupMessages(eval(parse(text=code)))))
} else {
  suppressMessages(suppressWarnings(suppressPackageStartupMessages(exec_jpg(code))))
}
