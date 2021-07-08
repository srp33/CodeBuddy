code_file_path = commandArgs()[9]
tests_dir_path = commandArgs()[10]
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

exec_jpg <- function(code, i=0) {
  library(ggplot2)

  pdf(NULL) # Prevents Rplots.pdf from being created.

  eval(parse(text=code))
  if (i == 0) {
    ggsave("/sandbox/image_output", dpi = 150, device = "jpeg")
  }
  else {
    ggsave(paste("/sandbox/test_image_output_", i, sep=""), dpi = 150, device = "jpeg")
  }
}

code <- readChar(code_file_path, file.info(code_file_path)$size)

if (output_type == "txt") {
  suppressMessages(suppressWarnings(suppressPackageStartupMessages(eval(parse(text=code)))))
} else {
  suppressMessages(suppressWarnings(suppressPackageStartupMessages(exec_jpg(code))))
}

setwd(file.path(tests_dir_path, "outputs"))
outputs_dir <- getwd()

tests <- list.files(path=tests_dir_path, pattern="test*", full.names=TRUE, recursive=FALSE)
for (i in seq_along(tests)) {
    setwd(file.path(outputs_dir, paste("test_", i, sep="")))
    test_code <- readChar(tests[i], file.info(tests[i])$size)

    # need to find a way to suppress printing to stdout while saving test code output so test outputs don't show up in submission output
    if (output_type == "txt") {
      out <- invisible(suppressMessages(suppressWarnings(suppressPackageStartupMessages(eval(parse(text=test_code))))))
      filename <- "text_output"
      invisible(write.table(out, filename, sep="\n"))
    } else {
      out <- invisible(suppressMessages(suppressWarnings(suppressPackageStartupMessages(exec_jpg(test_code, i)))))
      filename <- "image_output"
      invisible(write.table("", filename, sep="\n"))
    }
}
