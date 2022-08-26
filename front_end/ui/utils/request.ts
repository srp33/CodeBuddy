export async function postFormData<T>(url: string, data: any): Promise<T> {
	const formData = new FormData();
	for (const key in data) {
		formData.append(key, data[key]);
	}
	const response = await fetch(url, {
		method: "POST",
		body: formData,
	});
	if (Number(response.headers.get('Content-Length')) > 0) {
		return await response.json();
	}
	return null as any;
}