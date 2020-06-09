#! /bin/bash

##wget -O fontawesome.js https://use.fontawesome.com/releases/v5.3.1/js/all.js
#wget -O jquery.min.js https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js

# From https://jenil.github.io/bulmaswatch/flatly/#blog/
# This is a basic way to install bulmaswatch, which is used for the styles.
# For more advanced used, may need to use this strategy: https://bulma.io/documentation/customize/with-node-sass/
rm -f *css*
curl https://raw.githubusercontent.com/jenil/bulmaswatch/gh-pages/flatly/bulmaswatch.min.css | sed -En 's/.footer\{background-color:#ecf0f1;padding:3rem 1.5rem 6rem\}/.footer\{background-color:#ecf0f1;padding:1rem 3.0rem 1rem\}/p' > bulmaswatch.min.css
