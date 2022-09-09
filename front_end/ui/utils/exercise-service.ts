import { get, postFormData } from "./request";

export async function copyExercise(courseID: number, assignmentID: number, exerciseID: number, newTitle: string): Promise<string | undefined> {	
	const response = await postFormData<any>(`/copy_exercise/${courseID}/${assignmentID}/${exerciseID}`, {"new_title": newTitle});
	if (response.result != "") {
		return response.result;
	}
	else {
		location.reload();
		return;
	}
}

export async function runCode(courseID: number, assignmentID: number, exerciseID: number, userCode: string, test?: string): Promise<RunCodeResponse> {
	let url = `/run_code/${courseID}/${assignmentID}/${exerciseID}`;
	if (test) {
		url += `?test=${encodeURIComponent(test)}`;
	}
	return await postFormData<RunCodeResponse>(url, {"user_code": userCode});
}

export async function submitCode(courseID: number, assignmentID: number, exerciseID: number, userCode: string, partnerID: string = ''): Promise<SubmitCodeResponse> {
	let url = `/submit/${courseID}/${assignmentID}/${exerciseID}`;
    const data = { "code": userCode, "date": (new Date()).toLocaleString("en-US", {timeZone: "UTC"}), partner_id: partnerID };
	return await postFormData<SubmitCodeResponse>(url, data);
}

export async function savePresubmission(courseID: number, assignmentID: number, exerciseID: number, userCode: string): Promise<void> {
	let url = `/save_presubmission/${courseID}/${assignmentID}/${exerciseID}`;
	await postFormData(url, {"user_code": userCode});
}

export async function getPartnerID(courseID: number, name: string): Promise<string> {
	return await get<string>(`/get_partner_id/${courseID}/${encodeURIComponent(name)}`);
}