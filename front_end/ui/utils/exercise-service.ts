// <copyright_statement>
//   CodeBuddy: A programming assignment management system for short-form exercises
//   Copyright (C) 2024 Stephen Piccolo
//   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
// </copyright_statement>

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
	await postFormData(url, {"user_code": userCode}, false);
}

export async function getPartnerID(courseID: number, name: string): Promise<string> {
	return await get<string>(`/get_partner_id/${courseID}/${encodeURIComponent(name)}`);
}

export async function isTakingRestrictedAssignment(userID: string, assignmentID: number): Promise<boolean> {
	return await get<boolean>(`/is_taking_restricted_assignment/${userID}/${assignmentID}`);
}