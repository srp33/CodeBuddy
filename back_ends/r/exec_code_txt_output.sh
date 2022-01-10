cp before_code code

echo "options(warn=-1)" >> code
echo "options(tidyverse.quiet = TRUE)" >> code

cat main_code >> code
cat after_code >> code

Rscript code

python /clean_txt_output.py > /dev/null 2>&1
