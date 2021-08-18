with open("/VERSION") as version_file:
    version = version_file.read()

with open("/tmp/footer_version.html") as footer_file:
    footer = footer_file.read().replace("VERSION", version)

with open("/tmp/footer_version.html", "w") as footer_file:
    footer_file.write(footer)
