code_file_path="$1"
test_code_file_path="$2"
check_code_file_path="$3"
# We won't use this because this back end only supports text-based back ends.
#output_type="$3"

if [ -f "$check_code_file_path" ]
then
  # adds a newline to student's code if not already present, ensures that bash
  # checking code doesn't skip the final line
  sed -i -e '$a\' "$code_file_path"
  value=`bash $check_code_file_path`
  if [[ $value ]]
  then
    echo "$value"
    exit
  fi
fi

if [ -f "$test_code_file_path" ]
then
  echo >> "$code_file_path"
  cat "$test_code_file_path" >> "$code_file_path"
fi

bash "$code_file_path"
