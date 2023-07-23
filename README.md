# CodeBuddy

CodeBuddy is a [learning management system](https://en.wikipedia.org/wiki/Learning_management_system) that instructors can use to deliver computer-programming exercises. It was developed by the [Piccolo Lab](https://piccolo.byu.edu) and has been used since 2019 in programming-oriented courses. It uses HTML/CSS/JavaScript on the client side and Python on the server side. It executes students' code securely within  on the back end. 

Here are some of CodeBuddy's features:

* Students' code is executed in [Docker](https://www.docker.com) containers to provide isolation and make it easier to add new programming languages.
* Currently, CodeBuddy supports the following programming languages: [bash](https://en.wikipedia.org/wiki/Bash_(Unix_shell)), [C](https://en.wikipedia.org/wiki/C_(programming_language)), [C++](https://en.wikipedia.org/wiki/C%2B%2B), [Java](https://en.wikipedia.org/wiki/Java_(programming_language)),  [Javascript](https://en.wikipedia.org/wiki/JavaScript), [Julia](https://en.wikipedia.org/wiki/Julia_(programming_language)), [Python](https://www.python.org), [R](https://www.r-project.org), [Rust](https://www.rust-lang.org/). Send us [a request](https://github.com/srp33/CodeBuddy/issues) if you would like to see another language supported.
* Instructors can require students to write code that generates either text or graphics. Currently, graphics are supported for Python (*seaborn* package) and R (*ggplot2* package). CodeBuddy compares the student's output against the master solution and shows a [diffed](https://en.wikipedia.org/wiki/File_comparison) version.
* Instructors can configure exercises so that students can see the instructor's solution or anonymized solutions from peers.
* Instructors can create exercises that require students to write a reflection about how their code compares to the instructor's solution or anonymized solutions from peers.
* Instructors can see a list of "at-risk" students who have not made any submissions in the past *x* number of hours (or days).
* Instructors can configure exercises to support pair programming, an [evidence-based teaching practice](https://dl.acm.org/doi/10.1145/1921607.1921609). When one student submits, the code (and score) show up under the other student's account as well.
* Timed assignments can be used. Instructors can use this feature for exams. During timed exams, instructors can restrict access so that other assignments in the course cannot be accessed.
* Instructors can create "hidden" tests. For example, they can ask students to write a function that accepts certain arguments but not tell them what the values will be. This prevents students from circumventing test requirements.
* Instructors can write "verification" code to [statically analyze](https://en.wikipedia.org/wiki/Static_program_analysis) students' code before it is executed.
* Instructors can provide starter code and hints with exercise instructions.
* Instructors can upload data files that students must use when solving a problem.
* Instructors can deliver video-based content to students. For example, they can embed a YouTube video and require students to post a code- or text-based response to that content.
* When students are completing an assignment (exam) in a controlled environment that has no Internet access, instructors can configure the assignment to allow access to specific external URLs.
* Instructors can allow students to download all of their code from a course as a single HTML file.
* Teaching assistants can be given access to the instructor's solutions and students' scores. But they do not have the ability to change some course settings.
* Instructors can import and export assignments.
* Instructors can configure an exercise so that it is easy for students to copy their (last successful) solution from the previous exercise.
* [As of July 21, 2023] Instructors can configure a "Virtual Assistant" to provide help to students. The Virtual Assistant connects to OpenAI using the same models that ChatGPT uses. Students can ask questions about their code and request help when their code is not functioning correctly. Instructors can limit the number of interactions per student per exercise. This feature is currently experimental and requires a paid account with OpenAI.
* [As of July 24, 2023] Students are randomly assigned to a research cohort ("A" or "B"). Optionally, the instructor can configure a given assignment so that some students have access to the Virtual Assistant and others do not. Also optionally, the instructor can configure a given exercise so that some students can see the instructor's solution or anonymized peer solutions and others cannot. Researchers can use this feature for [A/B testing](https://en.wikipedia.org/wiki/A%2FB_testing). **Please** [let us know](https://codebuddy.byu.edu/static/contact_us.html) if you are interested in using this feature. It would be great to collaborate!

### How to run a CodeBuddy instance

We have a live server running CodeBuddy [here](https://codebuddy.byu.edu). If you would like to run your own instance, follow the instructions below.

##### Open a terminal

If you are using MacOS or Linux, you should already have a terminal. Go to the Applications menu, and open it. Then make sure you have installed the [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) command-line tool.

If you are using a Windows operating system, install [git for windows](https://gitforwindows.org). Then open Git Bash and use that as your terminal.

##### Install dependencies

CodeBuddy can be installed on any system that supports Docker and Python. Here are the steps to install it. You will need to have basic familiarity with [executing commands through a terminal](https://www.freecodecamp.org/news/command-line-for-beginners).

1. Install [Docker Desktop](https://docs.docker.com/engine/install). Make sure it is up and running.
2. Install [Python](https://www.python.org/downloads) (version 3.9+) and the [pip package manager](https://pip.pypa.io/en/stable/installation).
3. In the terminal, execute the following command to install the Python packages: `pip install -r front_end/requirements.txt`.
4. Modify Settings.yaml according to your preferences. The default settings should work in most cases.
5. Create a text file in `front_end/secrets/front_end.yaml` that contains three key/value pairs, as illustrated below. The first is a password for encrypting cookies (use a strong password). The second and third are a client ID and secret that enable CodeBuddy to perform Google authentication. You can obtain these from [here](https://console.developers.google.com).

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

For most users, the preferred option is to run the front end within Docker. To do this, execute the `run_front_end` script at the terminal.

If you want to contribute to developing CodeBuddy, it might be helpful to run CodeBuddy outside of Docker so that you do not need to rebuild the Docker image each time you make a change. To do so, follow these steps.

1. Use the `cd` command to change your current working directory to `front_end`.
2. Execute the following command: `make build-watch`. After waiting about 60 seconds, hit Ctrl-C.
3. Execute the following command: `make dev`. This will rebuild the HTML pages and start the front-end server.

When you modify files in the `front_end/templates` directory, you will need to re-run `make dev`. When you change any of the Python code, you will need to hit Ctrl-C to stop the development server and then re-execute `make dev`.

##### Running the middle layer

Use the `cd` command to change your current working directory to `middle_layer`. Then execute the `run_middle_layer` script.
