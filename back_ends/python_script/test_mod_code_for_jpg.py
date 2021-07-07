import sys

i = sys.argv[1]

with open("code.py", "a") as test_file:
    test_file.write(f"""
from matplotlib import pyplot as my_plt_saver
my_plt_saver.savefig('test_image_output_{i}', format='jpg', dpi=150)
my_plt_saver.close()""")
