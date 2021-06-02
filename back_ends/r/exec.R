code_file_path = commandArgs()[9]
test_code_file_path = commandArgs()[10]
check_code_file_path = commandArgs()[11]
output_type = commandArgs()[12]

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

if (file.exists(check_code_file_path)) {
  check_code <- readChar(check_code_file_path, file.info(check_code_file_path)$size)
  check_output <- capture.output(suppressMessages(suppressWarnings(suppressPackageStartupMessages(eval(parse(text=check_code))))),split=TRUE)
  if (length(check_output) > 0) {
    quit()
  }
}

exec_jpg <- function(code) {
  library(ggplot2)

  pdf(NULL) # Prevents Rplots.pdf from being created.

  eval(parse(text=code))
  ggsave("/sandbox/image_output", dpi = 150, device = "jpeg")
}

code <- readChar(code_file_path, file.info(code_file_path)$size)

if (file.exists(test_code_file_path)) {
  test_code <- readChar(test_code_file_path, file.info(test_code_file_path)$size)
  code <- paste(code, test_code, sep="\n\n")
}

if (output_type == "txt") {
  suppressMessages(suppressWarnings(suppressPackageStartupMessages(eval(parse(text=code)))))
} else {
  suppressMessages(suppressWarnings(suppressPackageStartupMessages(exec_jpg(code))))
}
