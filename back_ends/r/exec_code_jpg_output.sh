# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

echo "options(warn=-1)" > code
echo "options(tidyverse.quiet = TRUE)" >> code
echo "options(dplyr.summarise.inform = FALSE)" >> code

cat before_code >> code

# Prevents Rplots.pdf from being created.
echo "pdf(NULL)" >> code

cat main_code >> code

echo "library(ggplot2)" >> code
echo "ggsave('jpg_output', dpi = 150, device = 'jpeg')" >> code

cat after_code >> code

Rscript code
