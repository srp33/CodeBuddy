More details to come...

You must create a text file called `front_end/secrets/front_end.yaml` that contains a password that you wish to use for encrypting cookies, as well as Google authentication tokens. Below is an example. Details to come...

```
cookie: "abcdefg"
google_oauth_key: "111111111111-vsig111a11aa11aaaa1aaaaa1aaaa1aa.apps.googleusercontent.com"
google_oauth_secret: "A11AAAAaAAAAaAAAaa1aAAaa"
```

Also in the secrets directory:

MARIADB_ROOT_PASSWORD - This will be the root password. Use whatever password you would like to use.
MARIADB_USER - This will be the user ID that the app will use to access the database.
MARIADB_PASSWORD - This will be the password that the app will use to access the database.
MARIADB_DATABASE - The name of the database.

For middle layer, install gunicorn, uvicorn, arrow, fastapi. pip will also need to be installed...


## Running front-end locally

There are three commands you'll need to run the front_end app locally. You will run the following steps from the `front_end` directory:

1. 
	First, you need to build the HTML files into single HTML templates.

	```
	make html
	```

	**NOTE**: If you make a change to the HTML files inside of the `templates` directory, you will need to run `make html` again.

1.
	Then, you need to build the `static` directory using `esbuild`. This command will continue running and rebuild the application whenever you make changes inside the `ui` directory.

	```
	make build-watch
	```
1. 
	Lastly, you need to start the server! This will start the server in DEBUG mode, which will enable auto-reload, disable template caching, print logs to the terminal, and other helpful things for development.

	```
	make dev-server
	```

	**NOTE**: This requires you to have Python 3 installed (3.9 or later should work), as well as all of the dependencies. For now, refer to the [`Containerfile`](./front_end/Containerfile) for the Python dependencies.

If you would rather run the app in Docker, you can run the `run_front_end` script, but that will require rebuilding the image each time you make a change.

### SSL

If you have a proxy, create a self-signed certificate and specify path in Settings.yaml. See https://wiki.debian.org/Self-Signed_Certificate.

If you don't, you need to get a certificate from digicert, etc....
