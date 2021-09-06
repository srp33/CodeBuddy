code_file_path = commandArgs()[9]
tests_dir_path = commandArgs()[10]
check_code_file_path = commandArgs()[11]
output_type = commandArgs()[12]

options(warn=-1) # Silences printing to console globally.
options(tidyverse.quiet = TRUE)

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
  #system(paste("Rscript", code_file_path)) # Runs code using Rscript.
  suppressMessages(suppressWarnings(suppressPackageStartupMessages(eval(parse(text=code)))))
  
} else {
  #code <- readChar(code_file_path, file.info(code_file_path)$size)
  suppressMessages(suppressWarnings(suppressPackageStartupMessages(exec_jpg(code))))
}

if (dir.exists(tests_dir_path)) {
    setwd(file.path(tests_dir_path, "outputs"))
    outputs_dir <- getwd()
    tests <- list.files(path=tests_dir_path, pattern="test*", full.names=TRUE, recursive=FALSE)

    for (i in seq_along(tests)) {
        setwd(file.path(outputs_dir, paste("test_", i, sep="")))

        test_code <- readChar(tests[i], file.info(tests[i])$size)

        if (output_type == "txt") {
          test_code = paste("options(warn=-1)", "options(tidyverse.quiet = TRUE)", test_code, sep="\n")
          cat(test_code, file=tests[i], sep="\n", append=FALSE)

          out <- system(paste("Rscript", tests[i]), intern = TRUE) # Runs test code using Rscript and saves it to variable.

          cat(out, file="text_output", sep="\n", append=TRUE) # Writes variable to output file.
        } else {
          #test_code <- readChar(tests[i], file.info(tests[i])$size)
          out <- suppressMessages(suppressWarnings(suppressPackageStartupMessages(exec_jpg(test_code, i)))) # Executes code to save image as jpg.

          cat(out, file="image_output", sep="\n", append=FALSE) # Saves text output to file in case of traceback.
        }
    }
}
