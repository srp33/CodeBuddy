with open("/VERSION") as version_file:
    version = version_file.read()

with open("footer.html") as footer_file:
    footer = footer_file.read().replace("VERSION", version)

with open("footer.html", "w") as footer_file:
    footer_file.write(footer)
