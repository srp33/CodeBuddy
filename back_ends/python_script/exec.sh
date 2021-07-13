code_file_path="$1"
tests_dir_path="$2"
check_code_file_path="$3"
output_type="$4"

if [ -f "$check_code_file_path" ]
then
  # adds a newline to student's code if not already present, ensures that bash
  # checking code doesn't skip the final line
  sed -i -e '$a\' "$code_file_path"
  value=$(bash $check_code_file_path)
  if [[ "$value" ]]
  then
    echo "$value"
    exit
  fi
fi

mv "$code_file_path" "$code_file_path".py

if [ -d "$tests_dir_path" ]
then
  mv "$code_file_path".py $tests_dir_path
  cd $tests_dir_path
  # save code in temporary file
  touch temp.py
  cat code.py > temp.py
  for test_path in test*
  do
    if [[ "$output_type" == "jpg" ]]
    then
      # overwrite code with original
      cat temp.py > code.py
      python /test_mod_code_for_jpg.py ${test_path:5}
      test_outputs_path="${tests_dir_path}outputs/test_${test_path:5}/image_output"
    else
      test_outputs_path="${tests_dir_path}outputs/test_${test_path:5}/text_output"
    fi
    bash "$test_path" > $test_outputs_path
  done
else
  if [[ "$output_type" == "jpg" ]]
  then
    python /mod_code_for_jpg.py /sandbox/code
  fi
  python "$code_file_path".py
fi
