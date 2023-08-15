---
title: 'CodeBuddy: A programming assignment management system for short-form exercises'
tags:
  - computing education
  - open source
  - automatic grader
  - pair programming
  - intelligent tutor
  - web application
authors:
  - name: Stephen R. Piccolo
    orcid: 0000-0003-2001-5640
    affiliation: 1
  - name: Emme Tufts
    affiliation: 1
  - name: PJ Tatlow
    affiliation: "1, 2"
  - name: Zach Eliason
    affiliation: 1
  - name: Ashley Stephenson
    affiliation: 1
affiliations:
  - name: Brigham Young University
    index: 1
  - name: Cockroach Labs
    index: 2
date: 15 August 2023
bibliography: paper.bib
---

# Summary

CodeBuddy is a Web-based system for managing and assessing computer-programming assignments. It has been used in university courses since 2019. For a given course, instructor(s) specify configuration settings and organize content according to assignments. Within each assignment, instructor(s) specify programming exercises. They may also deliver static content, including text and videos. For each programming exercise, the instructor provides a solution and may provide custom testing logic. CodeBuddy executes the instructor's solution to generate text- or graphics-based outputs that are used as an evaluation reference. To pass a given programming exercise, a student's code must produce outputs matching the instructor's, although their programming strategy may differ. CodeBuddy stores users' inputs, outputs, scores, configuration settings, and more in a relational database. Additionally, CodeBuddy provides features intended to enhance student learning, facilitate course management for instructors and teaching assistants, and support pedagogical research. CodeBuddy's source code is available at https://github.com/srp33/CodeBuddy.

# Statement of Need

Many computer systems have been created to manage programming-oriented assignments[@blanchardStopReinventingWheel2022]. Some are commercial applications that require students or institutions to pay fees[@CodeAutogradingPlatform; @CodeGradeVirtualAssistant; @CodioHandsOnPlatform; @CodingRoomsDeveloper]. Others are open source software[@paivaAutomatedAssessmentComputer2022], thus providing benefits of transparency and extensibility.

We created CodeBuddy based on needs and opportunities identified in university-level, programming-oriented courses in the biological sciences. Its functionality is also suitable for other disciplinary contexts, K-12 schools, and informal learning. CodeBuddy is designed for short-form programming exercises—typically, those that can be solved in one hundred of lines of code or fewer.

CodeBuddy provides features to support user management, logging, and the ability to import, export, edit, copy, move, and delete content (Figure \autoref{fig:course_admin}). After landing on the home page (Figure \autoref{fig:home}), users authenticate using a third-party service (currently, Google is supported). Instructors author instructions using Markdown syntax (Figure \autoref{fig:edit_exercise}). Students edit code (Figure \autoref{fig:exercise}) using the Ajax.org Cloud9 Editor (Ace)[@AceHighPerformance]. Ace provides basic code completion and formatting help. When a student's outputs do not match the expected outputs, they can see those differences side by side. Instructors can create timed assignments; this feature is commonly used for quizzes and exams; while a student is completing a timed assignment, instructors can restrict access to other assignments in the course. Instructors can view course- and assignment-level summaries that show the number of completed assignments per course and the number of completed exercises per assignment, respectively; average scores are also shown. Instructors may export scores as delimited text files. Instructors can review students' submissions and edit scores manually.

As a security measure, code is executed inside software containers with restricted permissions. Currently, the following scripting or compiled languages are supported: bash, C, C++, Java, Javascript, Julia, Python, R, and Rust. Additional languages can be added via the following steps. For each programming language, a Dockerfile specifies instructions for building a Linux-based, operating-system environment with software to compile (if necessary) and execute code in the respective language. A separate configuration file provides language-specific information, such as how much memory usage to allow, whether text- and/or graphics-based outputs are supported, and code examples. Additionally, bash script(s) are provided for compiling (if necessary) the code, executing the code, and tidying the outputs (e.g., removing common warning or informational messages).

Here we highlight additional features that may support students' learning.

* Instructors can configure exercises to support *pair programming*, an evidence-based teaching practice in which two students work together at a single computer[@hawlitschekEmpiricalResearchPair2022]. When either student submits code for a given exercise, the code (and resulting score) are stored under the both students' accounts.
* Instructors can view a table of "at-risk" students who have not made a submission in the past *x* number of hours (or days).
* Instructors can create tests with "hidden" inputs and/or outputs. For example, they can ask students to write a function that accepts certain arguments but not tell them what the values will be. This prevents students from circumventing test requirements.
* Instructors can write "verification" code to statically analyze students' code before it is executed. For example, they could verify that students do or do not use certain programming constructs.
* Instructors can provide starter code for students.
* Instructors can provide hints for students. Students can view the hints after clicking a button.
* Instructors can provide data file(s) to be used as inputs for a given exercise.
* Instructors can deliver video-based content. For example, they can embed a YouTube video and require that students post a code- or text-based response to that content.
* Instructors can configure assignments to allow students to access specific URLs. This feature can be used when timed assignments (typically, exams) are delivered on computers with restricted Internet access.
* Instructors can allow students to download all of their latest, passing code submissions. Students often use this feature at the conclusion of a course to keep a copy of their code.
* Instructors can assign users as teaching assistants (TAs). TAs can access the instructor's solutions and students' scores. They are *not* permitted to change some course settings.
* Instructors can configure an exercise so that students can click a button to copy their (last successful) solution from the previous exercise.
* When a user first creates an account, CodeBuddy randomly assigns them to either an "A" or "B" cohort. These groups can be used for A/B testing in a research context.

Finally, we note features that can be made available to A) no students, B) all students, C) students in the "A" cohort, or D) students in the "B" cohort.

* Students can see the instructor's solution or anonymized solutions from peers after they have solved a given exercise (Figure \autoref{fig:instructor_solution}). Instructors can configure the subsequent exercise so that students are asked to write a reflection about their solution and how it compares with the instructor's solution or anonymized solutions from peers.
* Instructors can provide access to a "Virtual Assistant." The Virtual Assistant connects to OpenAI's ChatCompletion API[@OpenAIPlatform]. When this feature is enabled, students can ask questions about their code and request help (Figure \autoref{fig:virtual_assistant}). The API is constrained to provide advice but not code. Instructors can limit the number of interactions per student per exercise. This feature requires a paid account with OpenAI.

### Limitations

CodeBuddy is designed for short-form exercises rather than projects that require authoring multiple files. WebCAT and Submitty are alternatives for project-oriented work[@edwards2008web; @pevelerSubmittyOpenSource2017].

CodeBuddy stores data in a SQLite database for simplicity reasons; SQLite is a serverless, embedded engine that stores all data in a single file, which can be backed up or restored easily. We are unsure of its ability to scale beyond hundreds of users per school term. Future work could adapt the software to use a client-server database management system.

# Figures

![Course settings page.\label{fig:course_admin}](screenshots/course_admin.png)

![Exercise settings page.\label{fig:edit_exercise}](screenshots/edit_exercise.png)

![Default version of exercise page.\label{fig:exercise}](screenshots/exercise.png)

![Home page.\label{fig:home}](screenshots/home.png)

![Ability to view instructor's solution after completing an exercise.\label{fig:instructor_solution}](screenshots/instructor_solution.png)

![Virtual Assistant enabled on exercise page.\label{fig:virtual_assistant}](screenshots/virtual_assistant.png)

# References