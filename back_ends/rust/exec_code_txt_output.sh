# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

cp ./* /app/myapp

cd /app/myapp

#echo "[package]" > Cargo.toml
#echo "name = \"test-project\"" >> Cargo.toml
#echo "version = \"0.1.0\"" >> Cargo.toml
#echo "authors = [\"ChatGPT\"]" >> Cargo.toml
#echo "edition = \"2021\"" >> Cargo.toml
#echo  >> Cargo.toml
#echo "[dependencies]" >> Cargo.toml
#echo "regex = \"1.10.5\"" >> Cargo.toml

cat before_code main_code after_code > src/main.rs

cargo run --quiet
