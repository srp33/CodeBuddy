#! /bin/bash

set -e

function process_files {
  in_path="$1"
  prefix="$2"
  suffix="$3"

  for f in ${in_path}
  do
    echo $f

    tmp_file1=/tmp/copyright_temp1
    
    cp $f ${tmp_file1}

    python3 misc/remove_copyright_statement.py ${tmp_file1} "${prefix}" "${suffix}"

    tmp_file2=/tmp/copyright_temp2

    python3 misc/add_copyright_statement.py ${tmp_file2} misc/copyright_statement_template.txt "${prefix}" "${suffix}"

    cat ${tmp_file1} >> ${tmp_file2}
    mv ${tmp_file2} $f
  done
}

process_files "*.sh" "#" ""
process_files "back_ends/*/*.sh" "#" ""
process_files "back_ends/*/*.py" "#" ""
process_files "back_ends/*/*.R" "#" ""
process_files "front_end/*.sh" "#" ""
process_files "front_end/migration_scripts/*.py" "#" ""
process_files "front_end/scheduled_scripts/*.py" "#" ""
process_files "front_end/server/*.py" "#" ""
process_files "front_end/server/handlers/*.py" "#" ""
process_files "front_end/templates/*.html" "<!--" "-->"
process_files "front_end/ui/*/*.js" "//" ""
process_files "front_end/ui/*/*.ts" "//" ""
process_files "front_end/ui/*/*/*.ts" "//" ""
process_files "front_end/ui/*/*css" "/*" "*/"
process_files "front_end/ui/*/*/*css" "/*" "*/"
process_files "middle_layer/*.py" "#" ""