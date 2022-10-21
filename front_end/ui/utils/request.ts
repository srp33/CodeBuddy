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