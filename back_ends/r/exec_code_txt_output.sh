cp before_code code

echo "options(warn=-1)" >> code
echo "options(tidyverse.quiet = TRUE)" >> code
echo "options(dplyr.summarise.inform = FALSE)" >> code

cat main_code >> code
cat after_code >> code

Rscript code
