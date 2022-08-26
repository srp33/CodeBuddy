/* eslint-disable @typescript-eslint/no-explicit-any */

export function oneAtATime<F extends ((...args: any) => any)>(func: F) {
	let currentPromise: Promise<ReturnType<F>> | null = null;
	return (async (...args: Parameters<F>) => {
		while (currentPromise !== null) {
			try {
				await currentPromise;
			} finally {
				// don't care if an old one it fails
				// it'll be caught by whoever is awaiting it
			}
		}
		try {
			currentPromise = func(...args);
			return await currentPromise;
		} finally {
			currentPromise = null;
		}
	});
}
