cp before_code code

cat main_code >> code
echo >> code
echo "from matplotlib import pyplot as my_plt_saver" >> code
echo "my_plt_saver.savefig('jpg_output', format='jpg', dpi=150)" >> code
echo "my_plt_saver.close()" >> code

cat after_code >> code

python code

python /clean_txt_output.py > /dev/null 2>&1
