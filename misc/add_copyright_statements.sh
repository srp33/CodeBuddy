#! /bin/bash

set -e

function process_files {
  in_path="$1"
  prefix="$2"

  for f in back_ends/*/*
  do
    tmp_file=/tmp/copyright_temp

    echo "${prefix} <copyright_statement>" > ${tmp_file}

    sed "s/^/$prefix   /" misc/copyright_statement_template.txt >> ${tmp_file}

    echo "${prefix} </copyright_statement>" >> ${tmp_file}

    echo >> ${tmp_file}
    cat $f >> ${tmp_file}
  done
}

process_files "back_ends/*/*" "#"
