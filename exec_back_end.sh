do_verification=$1
output_type=$2

base_dir="$(pwd)"
done_with_verification=False

cd tests

for test_title in *
do
  cd "${base_dir}/tests/${test_title}"

  if [[ "${do_verification}" == "True" ]]
  then
    if [[ "${done_with_verification}" == "False" ]]
    then
      cp main_code code
      value="$(bash /verify_code.sh ${base_dir}/verification_code)"
      rm -f code

      if [[ "$value" ]]
      then
        echo "$value" &> txt_output
        exit
      fi

      done_with_verification=True
    fi
  fi

  if [[ "${output_type}" == "jpg" ]]
  then
    # We may get some text output when creating images.
    bash /exec_code_jpg_output.sh &>> txt_output
  else
    bash /exec_code_txt_output.sh &>> txt_output
  fi

  if [ -f /clean_txt_output.py ]
  then
    python3 /clean_txt_output.py > /dev/null 2>&1
  fi
done
