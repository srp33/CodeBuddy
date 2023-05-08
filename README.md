# CodeBuddy

CodeBuddy is a learning management system that instructors can use to deliver programming exercises. It was developed by the [Piccolo Lab](https://piccolo.byu.edu) and has been used since 2019 in programming-oriented courses at [BYU](https://www.byu.edu). It uses HTML/CSS/JavaScript on the client side, Python on the front-end servers, and executes code securely within [Docker](https://www.docker.com) containers on the back end. Currently, it supports programming tasks in [bash](https://en.wikipedia.org/wiki/Bash_(Unix_shell)), [Python](https://www.python.org), [R](https://www.r-project.org), and [Rust](https://www.rust-lang.org/). CodeBuddy's design makes it easy to support additional programming languages. Send us [a request](https://github.com/srp33/CodeBuddy/issues) if you would have a need for another language. We also use CodeBuddy to deliver text- and video-based content to students. Instructors can require that students post a code- or text-based response to this content and receive a score for providing a response.

Here are some of CodeBuddy's features:

* TBD...

#### Opening a terminal

If you are using MacOS or Linux, you should already have a terminal.

If you are using a Windows operating system, install [git for windows](https://gitforwindows.org). Then open Git Bash and use that as your terminal.

### Installing dependencies

CodeBuddy can be installed on any system that supports Docker and Python. Here are the steps to install it. You will need to have basic familiarity with [executing commands through a terminal](https://www.freecodecamp.org/news/command-line-for-beginners).

1. Install [Docker Desktop](https://docs.docker.com/engine/install). Make sure it is up and running.
2. Install [Python](https://www.python.org/downloads) (version 3.9+) and the [pip package manager](https://pip.pypa.io/en/stable/installation).
3. In the terminal, execute the following command to install the Python packages: `pip install -r requirements.txt`.
4. Install [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
5. Modify Settings.yaml according to your preferences. The default settings should work in most cases.
6. Create a text file in `front_end/secrets/front_end.yaml` that contains a password that you wish to use for encrypting cookies, as well as Google authentication tokens. (Google authenatication is not supported currently, so you can just use the placeholder values shown below for now.)

```
cookie: "abcdefg"
google_oauth_key: "111111111111-vsig111a11aa11aaaa1aaaaa1aaaa1aa.apps.googleusercontent.com"
google_oauth_secret: "A11AAAAaAAAAaAAAaa1aAAaa"
```

### Clone the repository

At the command line, use the `cd` command to change your working directory to where you wish to download the CodeBuddy code base.

```
git clone <cloneURL>
```

Replace `<cloneURL>` with the GitHub clone address for this project (for example, "https://github.com/srp33/CodeBuddy.git").

This will create a directory called CodeBuddy in your current working directory. Use the `cd` command to navigate to that directory.

### Running the front end

One option is to run the front end within Docker. To do this, run the `run_front_end` script at the terminal. However, that will require rebuilding the image each time you make a change, which slows down the development process. Instead, you can follow the process described below.

There are three commands you'll need to run the front_end app locally. You will run the following steps from the `front_end` directory:

1. First, you need to build the HTML files into single HTML templates. (If you make a change to the HTML files inside of the `templates` directory, you will need to run `make html` again.) Use the `cd` command to change your current working directory to `front_end` and then execute the following.

	```
	make html
	```

2. Build the `static` directory using `esbuild`. This command will continue running and rebuild the application whenever you make changes inside the `ui` directory. (Or you can run it and then cancel the command after it has rebuilt the application.)

	```
	make build-watch
	```
3. Lastly, you need to start the server! This will start the server in DEBUG mode, which will enable auto-reload, disable template caching, print logs to the terminal, and other helpful things for development.

	```
	make dev-server
	```

### Running the middle layer

Use the `cd` command to change your current working directory to `middle_layer`. Then execute the `run_middle_layer` script.

### Ignore this for now...

If you have a proxy, create a self-signed certificate and specify path in Settings.yaml. See https://wiki.debian.org/Self-Signed_Certificate.

If you don't, you need to get a certificate from digicert, etc....
