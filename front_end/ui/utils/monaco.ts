// <copyright_statement>
//   CodeBuddy - A learning management system for computer programming
//   Copyright (C) 2023 Stephen Piccolo
//   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
// </copyright_statement>

import type * as monaco from 'monaco-editor';
export type DiffEditor = monaco.editor.IStandaloneDiffEditor;


let monacoPromise: Promise<typeof monaco>;

// Returns a promise that resolves to the monaco object.
// Will only load the script once, calling it again will resolve to the same promise.
export async function getMonaco(): Promise<typeof monaco> {
	if (!monacoPromise) {
		monacoPromise = new Promise((resolve) => {
			const script = document.createElement('script');
			script.src = `/static/monaco/min/vs/loader.js`;
			script.onload = () => {
				// eslint-disable-next-line @typescript-eslint/no-explicit-any
				const w: any = window;
				w.require.config({ paths: { 'vs': `/static/monaco/min/vs` } });
				// window.MonacoEnvironment = {
				// 	getWorkerUrl: () => proxy,
				// 	getWorker: function (workerId: string, label: string) {
				// 		const getWorkerModule = (moduleUrl: string, label: string) => {
				// 			return new Worker(`/static/monaco/min/vs/${moduleUrl}`, {
				// 				name: label,
				// 				type: 'module'
				// 			});
				// 		};
				
				// 		switch (label) {
				// 			case 'json':
				// 				return getWorkerModule('language/json/jsonWorker.js', label);
				// 			case 'css':
				// 			case 'scss':
				// 			case 'less':
				// 				return getWorkerModule('language/css/cssWorker.js', label);
				// 			case 'html':
				// 			case 'handlebars':
				// 			case 'razor':
				// 				return getWorkerModule('language/html/htmlWorker.js', label);
				// 			case 'typescript':
				// 			case 'javascript':
				// 				return getWorkerModule('language/typescript/tsWorker.js', label);
				// 			default:
				// 				return getWorkerModule('base/worker/workerMain.js', label);
				// 		}
				// 	}					
				// };
				// const proxy = URL.createObjectURL(new Blob([`
				// self.MonacoEnvironment = {
				// 	baseUrl: '/static/monaco/min/vs'
				// };
				// `]));
				w.require(['vs/editor/editor.main'], function () {
					resolve(window.monaco);
				});
			};

			document.head.appendChild(script);
		});
	}
	return monacoPromise;
}


// import * as m from 'monaco-editor';

// export const monaco = m;

// export type DiffEditor = m.editor.IStandaloneDiffEditor;

// self.MonacoEnvironment = {
// 	baseUrl: '/static/monaco',
// 	getWorkerUrl: function (moduleId, label) {
// 		switch (label) {
// 			case 'json':
// 				return '/static/monaco/language/json/jsonWorker.js';
// 			case 'css':
// 			case 'scss':
// 			case 'less':
// 				return '/static/monaco/language/css/cssWorker.js';
// 			case 'html':
// 			case 'handlebars':
// 			case 'razor':
// 				return '/static/monaco/language/html/htmlWorker.js';
// 			case 'typescript':
// 			case 'javascript':
// 				return '/static/monaco/language/typescript/tsWorker.js';
// 			default:
// 				return '/static/monaco/base/worker/workerMain.js';
// 		}
// 	},

// 	// getWorker: function (workerId: string, label) {
// 	// 	const getWorkerModule = (moduleUrl: string, label: string) => {
// 	// 		return new Worker(self.MonacoEnvironment!.getWorkerUrl!(moduleUrl, label), {
// 	// 			name: label,
// 	// 			type: 'module'
// 	// 		});
// 	// 	};

// 	// 	switch (label) {
// 	// 		case 'json':
// 	// 			return getWorkerModule('/monaco-editor/esm/vs/language/json/json.worker?worker', label);
// 	// 		case 'css':
// 	// 		case 'scss':
// 	// 		case 'less':
// 	// 			return getWorkerModule('/monaco-editor/esm/vs/language/css/css.worker?worker', label);
// 	// 		case 'html':
// 	// 		case 'handlebars':
// 	// 		case 'razor':
// 	// 			return getWorkerModule('/monaco-editor/esm/vs/language/html/html.worker?worker', label);
// 	// 		case 'typescript':
// 	// 		case 'javascript':
// 	// 			return getWorkerModule('/monaco-editor/esm/vs/language/typescript/ts.worker?worker', label);
// 	// 		default:
// 	// 			return getWorkerModule('/monaco-editor/esm/vs/editor/editor.worker?worker', label);
// 	// 	}
// 	// }
// };


