code_file_path="$1"
test_code_file_path="$2"
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

if [[ "$output_type" == "jpg" ]]
then
  python /mod_code_for_jpg.py /sandbox/code
fi

mv "$code_file_path" "$code_file_path".py

if [ -f "$test_code_file_path" ]
then
  bash "$test_code_file_path"
else
  python "$code_file_path".py
fi
