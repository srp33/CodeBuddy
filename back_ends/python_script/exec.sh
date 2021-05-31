code_file_path="$1"
test_code_file_path="$2"
is_checking_code="$3"
output_type="$4"

if [[ "$is_checking_code" == "True" ]]
then
  bash "$test_code_file_path"
else  
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
fi
