code_file_path="$1"
test_code_file_path="$2"
output_type="$3"

if [[ "$output_type" == "jpg" ]]
then
  python /mod_code_for_jpg.py /sandbox/code
fi

if [ -f "$test_code_file_path" ]
then
  mv "$code_file_path" "$code_file_path".py
  bash "$test_code_file_path"
else
  bash "$code_file_path"
fi
