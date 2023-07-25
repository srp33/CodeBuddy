# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

do_verification=$1
output_type=$2

base_dir="$(pwd)"
done_with_verification=False

cd tests

for test_title in *
do
  cd "${base_dir}/tests/${test_title}"

  if [[ "${do_verification}" == "True" ]]
  then
    if [[ "${done_with_verification}" == "False" ]]
    then
      cp main_code code
      value="$(bash /verify_code.sh ${base_dir}/verification_code 2>&1)"
      rm -f code

      if [[ "$value" ]]
      then
        echo "$value" &> txt_output
        exit
      fi

      done_with_verification=True
    fi
  fi

  if [[ "${output_type}" == "jpg" ]]
  then
    # We may get some text output when creating images.
    bash /exec_code_jpg_output.sh &>> txt_output
  else
    bash /exec_code_txt_output.sh &>> txt_output
  fi

  if [ -f /clean_txt_output.py ]
  then
    python3 /clean_txt_output.py > /dev/null 2>&1
  fi
done
