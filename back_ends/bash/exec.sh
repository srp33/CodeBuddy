# We won't use this because this back end only supports text-based back ends.
#output_type="$1"

if [ -f "verification_code" ]
then
  # Adds a newline to student's code if not already present and ensures that verifcation code doesn't skip the final line.
  sed -i -e '$a\' "$code_file_path"
  value=$(bash verification_code)
  if [[ "$value" ]]
  then
    echo "$value"
    exit
  fi
fi

cd tests

for test_id in *
do
  # Saves test output to file.
  bash ${test_id}/code > ${test_id}/text_output
done
