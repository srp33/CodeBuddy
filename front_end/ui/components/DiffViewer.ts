// <copyright_statement>
//   CodeBuddy: A programming assignment management system for short-form exercises
//   Copyright (C) 2024 Stephen Piccolo
//   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
// </copyright_statement>

import {LitElement, html, css, PropertyValueMap} from 'lit';
import {customElement, property} from 'lit/decorators.js';
import bind from '@/utils/bind';
import { getMonaco, DiffEditor } from '@/utils/monaco';


@customElement('diff-viewer')
export default class DiffViewer extends LitElement {
	private resizeObserver = new ResizeObserver(this.resize);

	@property()
	public left?: string;

	@property()
	public right?: string;

	private editor?: DiffEditor;

	constructor() {
		super();
	}

	render() {
		return html`<div></div>`;
	}

	async firstUpdated() {
		const monaco = await getMonaco();
		const left = monaco.editor.createModel(this.left ?? '', 'text/plain');
		const right = monaco.editor.createModel(this.right ?? '', 'text/plain');
		
		this.editor = monaco.editor.createDiffEditor(this.renderRoot.querySelector('div')!, {
			fontSize: 14,
			domReadOnly: true,
			readOnly: true,
			minimap: { enabled: false },
			scrollbar: {
				alwaysConsumeMouseWheel: true,
			},
			scrollBeyondLastLine: false,
			ignoreTrimWhitespace: false,
			renderWhitespace: 'all',
			// renderSideBySide: false,
		});
		this.editor.setModel({
			original: left,
			modified: right,
		});

		this.resizeObserver.observe(this);
		// this.editor.getOriginalEditor().onDidAttemptReadOnlyEdit()
	}

	@bind
	resize() {
		this.editor?.layout();
	}

}