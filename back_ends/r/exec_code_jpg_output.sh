cp before_code code

echo "options(warn=-1)" >> code
echo "options(tidyverse.quiet = TRUE)" >> code
echo "options(dplyr.summarise.inform = FALSE)" >> code

echo "library(ggplot2)" >> code

# Prevents Rplots.pdf from being created.
echo "pdf(NULL)" >> code

cat main_code >> code

echo "ggsave('jpg_output', dpi = 150, device = 'jpeg')" >> code

cat after_code >> code

Rscript code
