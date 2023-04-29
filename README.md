# CodeBuddy

CodeBuddy is a learning management system that instructors can use to deliver programming exercises. It was developed by the [Piccolo Lab](https://piccolo.byu.edu) and has been used since 2019 in programming-oriented courses at [BYU](https://www.byu.edu). It has an HTML/CSS/JavaScript front end and executes code securely within [Docker](https://www.docker.com) containers on the back end. Currently, it supports programming tasks in [bash](https://en.wikipedia.org/wiki/Bash_(Unix_shell)), [Python](https://www.python.org), [R](https://www.r-project.org), and [Rust](https://www.rust-lang.org/). CodeBuddy's design makes it easy to support additional programming languages. Send us [a request](https://github.com/srp33/CodeBuddy/issues) if you would have a need for another language. We also use CodeBuddy to deliver text- and video-based content to students. Instructors can require that students post a code- or text-based response to this content and receive a score for providing a response.

Here are some of CodeBuddy's features:

* TBD...

### Installing CodeBuddy

CodeBuddy can be installed on any system that supports Docker and Python. Here are the steps to install it.

1. Install [Docker Desktop](https://docs.docker.com/engine/install). Make sure it is up and running.
2. Install [Python](https://www.python.org/downloads) (version 3.8+) and the [pip package manager](https://pip.pypa.io/en/stable/installation).
3. 

You must create a text file called `front_end/secrets/front_end.yaml` that contains a password that you wish to use for encrypting cookies, as well as Google authentication tokens. Below is an example. Details to come...

```
cookie: "abcdefg"
google_oauth_key: "111111111111-vsig111a11aa11aaaa1aaaaa1aaaa1aa.apps.googleusercontent.com"
google_oauth_secret: "A11AAAAaAAAAaAAAaa1aAAaa"
```



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

### Ignore this for now...

If you have a proxy, create a self-signed certificate and specify path in Settings.yaml. See https://wiki.debian.org/Self-Signed_Certificate.

If you don't, you need to get a certificate from digicert, etc....
