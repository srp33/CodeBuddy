# CodeBuddy

CodeBuddy is a learning management system that instructors can use to deliver programming exercises. It was developed by the [Piccolo Lab](https://piccolo.byu.edu) and has been used since 2019 in programming-oriented courses at [BYU](https://www.byu.edu). It uses HTML/CSS/JavaScript on the client side, Python on the server side, and executes code securely within [Docker](https://www.docker.com containers) on the back end. Currently, it supports programming tasks in [bash](https://en.wikipedia.org/wiki/Bash_(Unix_shell)), [C](https://en.wikipedia.org/wiki/C_(programming_language)), [Python](https://www.python.org), [R](https://www.r-project.org), and [Rust](https://www.rust-lang.org/). CodeBuddy's design makes it easy to support additional programming languages; send us [a request](https://github.com/srp33/CodeBuddy/issues) if you would like to see another language supported. We also use CodeBuddy to deliver text- and video-based content to students. Instructors can require that students post a code- or text-based response to content and receive a score for providing a response.

Here are some of CodeBuddy's features:

* 

### How to run a CodeBuddy instance

We have a live server running CodeBuddy [here](https://codebuddy.byu.edu). If you would like to run your own instance, follow the instructions below.

##### Open a terminal

If you are using MacOS or Linux, you should already have a terminal. Go to the Applications menu, and open it. Then make sure you have installed the [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) command-line tool.

If you are using a Windows operating system, install [git for windows](https://gitforwindows.org). Then open Git Bash and use that as your terminal.

##### Install dependencies

CodeBuddy can be installed on any system that supports Docker and Python. Here are the steps to install it. You will need to have basic familiarity with [executing commands through a terminal](https://www.freecodecamp.org/news/command-line-for-beginners).

1. Install [Docker Desktop](https://docs.docker.com/engine/install). Make sure it is up and running.
2. Install [Python](https://www.python.org/downloads) (version 3.9+) and the [pip package manager](https://pip.pypa.io/en/stable/installation).
3. In the terminal, execute the following command to install the Python packages: `pip install -r requirements.txt`.
4. Modify Settings.yaml according to your preferences. The default settings should work in most cases.
5. Create a text file in `front_end/secrets/front_end.yaml` that contains a password that you wish to use for encrypting cookies, as well as Google authentication tokens. (Google authentication is not supported currently, so you can just use the placeholder values shown below for now.)

```
cookie: "abcdefg"
google_oauth_key: "123456789012-abc123a12aa12aaaa1aaaaa1aaaa1aa.apps.googleusercontent.com"
google_oauth_secret: "ABCDEFGHIJKLMNOP"
```

If you would like to contribute to developing CodeBuddy, complete these additional steps.

6. Install [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
7. Install Make. (Try [these instructions](https://stackoverflow.com/questions/66525016/how-to-run-make-command-in-gitbash-in-windows) for Windows.)

##### Clone the repository

From a terminal window, use the `cd` command to change your working directory to where you wish to store the CodeBuddy code.

```
git clone <cloneURL>
```

Replace `<cloneURL>` with the GitHub clone address for this project (for example, https://github.com/srp33/CodeBuddy.git).

This will create a directory called CodeBuddy in your current working directory. Use the `cd` command to navigate to that directory.

##### Running the front end

For most users, the preferred option is to run the front end within Docker. To do this, execute the `run_front_end` script at the terminal. If you want to contribute to developing CodeBuddy, it might be helpful to run CodeBuddy outside of Docker so that you do not need to rebuild the Docker image each time you make a change. To do so, follow the steps described below.

1. Use the `cd` command to change your current working directory to `front_end`.
2. Build the HTML files. Execute the following command. `make html`
3. Build the `static` directory. Execute the following command. When it is done, hit Ctrl-C to move on. `make build-watch`
4. Start the development server. Execute the following command. `make dev-server`

When you modify files in the `front_end/templates` directory, you will need to re-run `make html`. When you change any of the Python code, you will need to hit Ctrl-C to stop the development server and then re-execute `make dev-server`.

##### Running the middle layer

Use the `cd` command to change your current working directory to `middle_layer`. Then execute the `run_middle_layer` script.