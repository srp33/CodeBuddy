import sys

code_file_path = sys.argv[1]

with open(code_file_path, "a") as code_file:
    code_file.write(f"""
from matplotlib import pyplot as my_plt_saver
my_plt_saver.savefig('image_output', format='jpg', dpi=150)
my_plt_saver.close()""")
