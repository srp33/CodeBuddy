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
