// <copyright_statement>
//   CodeBuddy - A learning management system for computer programming
//   Copyright (C) 2023 Stephen Piccolo
//   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
// </copyright_statement>

export async function postFormData<T>(url: string, data: any, parseResponse = true): Promise<T> {
	const formData = new FormData();
	for (const key in data) {
		formData.append(key, data[key]);
	}
	const response = await fetch(url, {
		method: "POST",
		body: formData,
	});
	if (!parseResponse) {
		return null as any;
	}
	try {
		return await response.json();
	} catch (e) {
		console.error(e);
		return null as any;
	}
}

export async function get<T>(url: string): Promise<T> {
	const response = await fetch(url, {
		method: "GET",
	});
	try {
		return await response.json();
	} catch (e) {
		console.error(e);
		return null as any;
	}
}