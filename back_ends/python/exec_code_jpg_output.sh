# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

cp before_code code

cat main_code >> code
echo >> code
echo "from matplotlib import pyplot as my_plt_saver" >> code
echo "my_plt_saver.savefig('jpg_output', format='jpg', dpi=150, bbox_inches = 'tight')" >> code
echo "my_plt_saver.close()" >> code

cat after_code >> code

python code
