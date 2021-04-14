code_file_path="$1"
test_code_file_path="$2"
# We won't use this because this back end only supports text-based back ends.
#output_type="$3"

if [ -f "$test_code_file_path" ]
then
  echo >> "$code_file_path"
  cat "$test_code_file_path" >> "$code_file_path"
fi

bash "$code_file_path"
