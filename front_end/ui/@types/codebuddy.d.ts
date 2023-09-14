// <copyright_statement>
//   CodeBuddy: A programming assignment management system for short-form exercises
//   Copyright (C) 2023 Stephen Piccolo
//   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
// </copyright_statement>

interface Submission {
	id: number;
	date: Date;
	code: string;
	passed: boolean;
	test_outputs: TestOutputs;
}


interface RunCodeResponse {
	all_passed: boolean;
	message: string;
	test_outputs: TestOutputs;
}

type TestOutputs = {[testName: string]: {
	passed: boolean;
	txt_output: string;
	jpg_output: string;
	diff_output: string;
	txt_output_formatted: string;
}};

interface SubmitCodeResponse extends RunCodeResponse {
	submission_id: number;
}
