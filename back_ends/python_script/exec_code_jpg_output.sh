bash before_code

cp main_code code.py
echo >> code.py
echo "from matplotlib import pyplot as my_plt_saver" >> code.py
echo "my_plt_saver.savefig('jpg_output', format='jpg', dpi=150, bbox_inches = 'tight')" >> code.py
echo "my_plt_saver.close()" >> code.py

bash after_code

python /clean_txt_output.py > /dev/null 2>&1