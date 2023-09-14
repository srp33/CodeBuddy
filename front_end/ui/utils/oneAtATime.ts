// <copyright_statement>
//   CodeBuddy: A programming assignment management system for short-form exercises
//   Copyright (C) 2023 Stephen Piccolo
//   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
// </copyright_statement>

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
