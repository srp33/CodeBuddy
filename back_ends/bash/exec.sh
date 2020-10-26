code_file_path="$1"
# We won't use this because this back end only supports text-based back ends.
#output_type="$2"

#bash "$code_file_path" 1> /sandbox/output 2> /sandbox/error

bash "$code_file_path"

#sed -i -e 's/\/sandbox\/code: //g' /sandbox/error
