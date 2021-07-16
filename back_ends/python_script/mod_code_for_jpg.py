import sys

code_file_path = sys.argv[1]
# only assign test number if script is called by test code. Otherwise save as 'image_output'
i = sys.argv[2] if len(sys.argv) > 2 else None

with open(code_file_path, "a") as code_file:
    if not i:
        code_file.write(f"""
from matplotlib import pyplot as my_plt_saver
my_plt_saver.savefig('image_output', format='jpg', dpi=150)
my_plt_saver.close()""")
    else:
        code_file.write(f"""
from matplotlib import pyplot as my_plt_saver
my_plt_saver.savefig('test_image_output_{i}', format='jpg', dpi=150)
my_plt_saver.close()""")
