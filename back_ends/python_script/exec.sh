code_file_path="$1"
tests_dir_path="$2"
check_code_file_path="$3"
output_type="$4"

if [ -f "$check_code_file_path" ]
then
  # Adds a newline to student's code if not already present and ensures that bash checking code doesn't skip the final line.
  sed -i -e '$a\' "$code_file_path"
  value=$(bash $check_code_file_path)
  if [[ "$value" ]]
  then
    echo "$value"
    exit
  fi
fi

# Renames code file.
mv "$code_file_path" "$code_file_path".py

if [ -d "$tests_dir_path" ]
then
  # Moves code file into tests directory so that they can access it.
  mv "$code_file_path".py $tests_dir_path
  cd $tests_dir_path
  # Saves code in temporary file.
  cat code.py > temp.py
  for test_path in test*
  do
    if [[ "$output_type" == "jpg" ]]
    then
      # Refresh code from temporary copy.
      cat temp.py > code.py
      # Adds code specifying where to save image.
      python /mod_code_for_jpg.py "$tests_dir_path"code.py ${test_path:5}
      test_outputs_path="${tests_dir_path}outputs/test_${test_path:5}/image_output"
    else
      test_outputs_path="${tests_dir_path}outputs/test_${test_path:5}/text_output"
    fi
    # Saves test output to file.
    bash "$test_path" > $test_outputs_path
  done
else
  if [[ "$output_type" == "jpg" ]]
  then
    python /mod_code_for_jpg.py "$code_file_path".py
  fi
  python "$code_file_path".py
fi
