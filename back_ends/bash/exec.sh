code_file_path="$1"
tests_dir_path="$2"
check_code_file_path="$3"
# We won't use this because this back end only supports text-based back ends.
#output_type="$4"

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

bash "$code_file_path"

if [ -d "$tests_dir_path" ]
then
  cd $tests_dir_path
  for test_path in test*
  do
    test_outputs_path="${tests_dir_path}outputs/test_${test_path:5}/text_output"
    touch $test_outputs_path
    bash "$test_path" > $test_outputs_path
  done
fi
