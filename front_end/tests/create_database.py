    settings_dict = load_yaml_dict(read_file("Settings.yaml"))

    content = Content(settings_dict)

    database_version = content.get_database_version()
    code_version = int(read_file("VERSION").rstrip())

    for v in range(database_version, code_version):
        migration = f"{v}_to_{v + 1}"

        if os.path.isfile(f"migration_scripts/{migration}.py"):
            command = f"python3 migration_scripts/{migration}.py"
        else:
            command = f"python3 migration_scripts/migrate.py {migration} {v}"

        result = run_command(command)

        print(f"Database successfully migrated to version {v+1}")
        content.update_database_version(v + 1)

    content.add_user("test_admin", user_dict = {'name': f'Test Admin', 'given_name': "Test", 'family_name': 'Admin', 'locale': 'en', 'email_address': f'test_admin@nospam.edu'})
    content.add_admin_permissions("test_admin")

    course_basics = content.get_course_basics(None)
    course_basics["title"] =  "Test Course"

    course_details = content.get_course_details(None)
    course_details["introduction"] = "Course introduction"
    course_details["date_created"] = datetime.datetime.now(timezone.utc)
    course_details["date_updated"] = datetime.datetime.now(timezone.utc)

    course_id = content.save_course(course_basics, course_details)
    course_basics = content.get_course_basics(course_id)

    assignment_basics = content.get_assignment_basics(course_basics, None)
    assignment_basics["title"] = "Test Assignment"

    assignment_details = content.get_assignment_details(course_basics, None)
    assignment_details["introduction"] = "Assignment introduction"
    assignment_details["date_created"] = datetime.datetime.now(timezone.utc)
    assignment_details["date_updated"] = datetime.datetime.now(timezone.utc)

    assignment_id = content.save_assignment(assignment_basics, assignment_details)
    assignment_basics = content.get_assignment_basics(course_basics, assignment_id)

    exercise_basics = content.get_exercise_basics(course_basics, assignment_basics, None)
    exercise_basics["title"] = "Test Exercise"

    exercise_details = content.get_exercise_details(course_basics, assignment_basics, None)
    exercise_details["instructions"] = "Exercise instructions"
    exercise_details["solution_code"] = "print('Hello, world!')"
    exercise_details["date_created"] = datetime.datetime.now(timezone.utc)
    exercise_details["date_updated"] = datetime.datetime.now(timezone.utc)
    exercise_details["what_students_see_after_success"] = 3
    exercise_details["tests"] = {"Test 1": {"test_id": 1, "before_code": "", "after_code": "", "instructions": "", "can_see_test_code": True, "can_see_expected_output": True, "can_see_code_output": True, "txt_output": "Hello, world!", "jpg_output": ""}}

    exercise_id = content.save_exercise(exercise_basics, exercise_details)
    exercise_basics = content.get_exercise_basics(course_basics, assignment_basics, exercise_id)

    mc_exercise_basics = content.get_exercise_basics(course_basics, assignment_basics, None)
    mc_exercise_basics["title"] = "Test MC Exercise"

    mc_exercise_details = content.get_exercise_details(course_basics, assignment_basics, None)
    mc_exercise_details["instructions"] = "Exercise instructions"
    mc_exercise_details["back_end"] = "multiple_choice"
    mc_exercise_details["solution_code"] = '{"A": false, "B": false, "C": true}'
    mc_exercise_details["date_created"] = datetime.datetime.now(timezone.utc)
    mc_exercise_details["date_updated"] = datetime.datetime.now(timezone.utc)
    mc_exercise_details["tests"] = {}

    mc_exercise_id = content.save_exercise(mc_exercise_basics, mc_exercise_details)
    mc_exercise_basics = content.get_exercise_basics(course_basics, assignment_basics, mc_exercise_id)

    content.add_user("test_student", user_dict = {'name': f'Test User', 'given_name': "Test", 'family_name': 'User', 'locale': 'en', 'email_address': f'test_student@nospam.edu'})
    content.register_user_for_course(course_id, "test_student")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(content.save_submission(course_id, assignment_id, exercise_id, "test_student", "print('Hello, world!')", True, datetime.datetime.now(timezone.utc), exercise_details, {'Test 1': {'txt_output': 'Hello, world!', 'jpg_output': '', 'txt_output_formatted': 'Hello, world!', 'diff_output': '', 'passed': True}}, 100, None))
    #loop.close()

    secrets_dict = load_yaml_dict(read_file("secrets/front_end.yaml"))
