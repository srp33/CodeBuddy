interface Submission {
	id: number;
	date: Date;
	code: string;
	passed: boolean;
}

interface RunCodeResponse {
	all_passed: boolean;
	message: string;
	test_outputs: {[testName: string]: {
		passed: boolean;
		txt_output: string;
		jpg_output: string;
		diff_output: string;
		txt_output_formatted: string;
	}};
}

interface SubmitCodeResponse extends RunCodeResponse {
	submission_id: number;
}
