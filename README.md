# CodeBuddy

CodeBuddy is a programming-assignment management system ([a type of learning management system](https://en.wikipedia.org/wiki/Learning_management_system) that instructors can use to deliver computer-programming exercises. It was developed by the [Piccolo Lab](https://piccolo.byu.edu) and has been used since 2019 in programming-oriented courses. It uses HTML/CSS/JavaScript on the client side and Python on the server side. It executes students' code securely within  on the back end. 

# Features

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
* [July 21, 2023] Instructors can configure a "Virtual Assistant" to provide help to students. The Virtual Assistant connects to OpenAI using the same models that ChatGPT uses. Students can ask questions about their code and request help when their code is not functioning correctly. Instructors can limit the number of interactions per student per exercise. This feature is currently experimental and requires a paid account with OpenAI.
* [July 24, 2023] Students are randomly assigned to a research cohort ("A" or "B"). Optionally, the instructor can configure a given assignment so that some students have access to the Virtual Assistant and others do not. Also optionally, the instructor can configure a given exercise so that some students can see the instructor's solution or anonymized peer solutions and others cannot. Researchers can use this feature for [A/B testing](https://en.wikipedia.org/wiki/A%2FB_testing). **Please** [let us know](https://codebuddy.byu.edu/static/contact_us.html) if you are interested in using this feature. It would be great to collaborate!
* [May 2, 2024] Instructors can configure an assignment so that other assignment(s) must be completed as prerequisite(s). Students will be unable to access the assignment(s) until they have completed the prerequisite(s).
* [June 21, 2024] Instructors can require students to have a security code to access an assignment. The instructor can generate a PDF with a separate page for each student that has a security code. The student would then receive one of these pages upon starting the assignment to ensure that the student takes the assignment in a secure location (i.e., testing center). Optionally, the instructor can configure the assignment so that a confirmation code is generated when the student completes the assignment (or ends it early). They must give this confirmation code to the instructor (or a proxy) to ensure that they completed the assignment in the secure location.
* [June 21, 2024] Instructors can include multiple-choice (or multiple-answer) exercises in assignments.
* [July 10, 2024] By default, the assignment score is calculated as the average of the exercise scores within the assignment. Now instructors can specify custom scoring logic. For example, suppose an assignment has five exercises. An instructor might specify that if a student successfully completes one exercise (20%), the student receives a passing grade (60%). And/or they might specify that if a student completes all but one of the exercises (80%), the student receives full points (100%) for the assignment.
* [August 7, 2024] Instructors can paste images into the instructions on the "Edit exercise" pages.
* [August 20, 2024] Sometimes, to answer a multiple-choice question, students need to execute code (e.g., to perform calculations, apply a statistical test) to answer the question. Instructors can configure an exercise so that it includes a "sandbox" on the page. With this option, students can execute code, but the code is not evaluated directly (or saved).
* [June 12, 2025] Instructors can create assignment groups.
* [June 25, 2025] Instructors can configure courses and assignments so that students can submit questions about the material. An instructor / assistant are notified by email. They answer the questions via CodeBuddy. If the student and instructor / assistant agree, the question is shared with other students in the same class.
* [June 30, 2025] For assignments that are timed, students do not know whether they have answered multiple-choice questions correctly until after the assignment has ended. This helps to reduce student anxiety on quizzes and exams.

# How to run a CodeBuddy instance

We have a live server running CodeBuddy [here](https://codebuddy.byu.edu). If you would like to run your own instance, follow the instructions below.

##### Open a terminal

You will need to have basic familiarity with [executing commands through a terminal](https://www.freecodecamp.org/news/command-line-for-beginners).

If you are using MacOS or Linux, you should already have a terminal. Open it. Then make sure you have installed the [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) command-line tool.

If you are using a Windows operating system, install [git for windows](https://gitforwindows.org). Then open Git Bash and use that as your terminal.

##### Install dependencies

1. Install [Docker Desktop](https://docs.docker.com/engine/install). Make sure it is up and running.
2. Install [Python](https://www.python.org/downloads) (version 3.9+) and the [pip package manager](https://pip.pypa.io/en/stable/installation). After installing them, Python should be available at the command line as `python3`. You might need to close and reopen the terminal before this command will be available to you.

##### Clone the GitHub repository

From a terminal window, use the `cd` command to change your working directory to the location on your file system where you wish to store the CodeBuddy code.

```
git clone <cloneURL>
```

Replace `<cloneURL>` with the GitHub clone address for this project (for example, https://github.com/srp33/CodeBuddy.git).

This will create a directory called CodeBuddy in your current working directory. Use the `cd` command to navigate to that directory. Then do the following:

1. At the terminal, execute the following command to install the Python packages: `pip install -r front_end/requirements.txt`.
2. Modify Settings.yaml according to your preferences. The default settings should work in most cases.
3. Create a text file in `front_end/secrets/front_end.yaml`. It should contain three key/value pairs, as illustrated below. The first is a password for encrypting cookies (use a strong password). The second and third are a client ID and secret that enable CodeBuddy to perform Google authentication. You can obtain these from [here](https://console.developers.google.com).

```
cookie: "abcdefg"
google_oauth_key: "123456789012-abc123a12aa12aaaa1aaaaa1aaaa1aa.apps.googleusercontent.com"
google_oauth_secret: "ABCDEFGHIJKLMNOP"
```

[Optional] If you would like to contribute to developing CodeBuddy, complete these additional steps. Otherwise, you can skip these steps.

4. Install [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
5. Install Make. (Try [these instructions](https://stackoverflow.com/questions/66525016/how-to-run-make-command-in-gitbash-in-windows) for Windows.)

##### Running the front end

For most users, the preferred option is to run the front end within Docker. To do this, execute the `run_front_end` script at the terminal.

[Optional] If you want to contribute to developing CodeBuddy, it might be helpful to run CodeBuddy outside of Docker so that you do not need to rebuild the Docker image each time you make a change. To do so, follow these steps.

1. Use the `cd` command to change your current working directory to `front_end`.
2. Execute the following command: `make build-watch`. After waiting about 30 seconds, hit Ctrl-C to interrupt this command.
3. Execute the following command: `make dev`. This will rebuild the HTML pages and start the front-end server.

[Optional] When you modify files in the `front_end/templates` directory, you will need to re-run `make dev`. When you change any of the Python code, you will need to hit Ctrl-C to stop the development server and then re-execute `make dev`.

##### Running the middle layer

From the CodeBuddy directory, execute the *run_middle_layer* script. Example: `bash run_middle_layer`.

# Setting up a course

Here you will learn how to create a course in CodeBuddy. When you first run CodeBuddy, it will show a screen that allows you to specify settings for an initial course. We hope this page is self explanatory, but below is a short description of these settings.

* *Title* - The title of the course.
* *Introduction* - Indicate who developed the course and describe the concepts and skills that are taught in the course.
* *Visible to students* - An instructor can keep a course hidden from students until the instructor is ready to release it.
* *Allow students to download their code for this course?* - Students often wish to download code for the assignments and exercises that they have completed. This setting allows them to do that for the entire course (with some exceptions).
* *Passcode* - Optionally, you can specify a passcode that students must enter before they can register for the course.
* *Virtual Assistant configuration* - CodeBuddy provides support for integration with OpenAI's chat API. The goal is to automate the process of helping students when they are "stuck" on programming exercises. To enable this feature, you must specify configuration information and subsequently indicate whether this feature is enabled in the settings for each assignment.

After submitting this information, a course will be created, and you can create assignments and exercises. To simplify this process, we have created an example assignment that you can import, rather than specifying the assignment details by hand. To import the example assignment, do the following:

1. Download the example assignment file from [here](https://raw.githubusercontent.com/srp33/CodeBuddy/master/examples/Example_assignment.json).
2. On the page for the course that you just created, click on the "Import assignment" button.
3. Select the file that you just downloaded.
4. Click on Continue.

You should see the assignment. If you click on the assignment, you should see a variety of exercises that illustrate some of CodeBuddy's functionality.

# Backing up the database

CodeBuddy currently uses [SQLite](https://sqlite.org) as its database. At first glance, you might think that is a limitation. In some circumstances, it is. However, there are many advantages to using SQLite ([explained here](https://fly.io/blog/all-in-on-sqlite-litestream)). So far, it has been able to handle our needs (hundreds of students per school term). (We are open to pull requests if this is a limiting factor for you.)

A great way to back up you CodeBuddy database is to specify `db_journal_mode: "WAL"` in Settings.yaml. Then you can use [Litestream](https://litestream.io) to save the database at frequent intervals to a remote server. If you want to synchronize the database to multiple servers, that may be possible with a tool like [litesync](https://litesync.io), but we have not attempted this.
