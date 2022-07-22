cp before_code code

echo "options(warn=-1)" >> code
echo "options(tidyverse.quiet = TRUE)" >> code

echo "library(ggplot2)" >> code

# Prevents Rplots.pdf from being created.
echo "pdf(NULL)" >> code

cat main_code >> code

echo "ggsave('image_output', dpi = 150, device = 'jpeg')" >> code

cat after_code >> code

Rscript code

python3 /clean_txt_output.py > /dev/null 2>&1
