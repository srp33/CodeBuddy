// <copyright_statement>
//   CodeBuddy - A learning management system for computer programming
//   Copyright (C) 2023 Stephen Piccolo
//   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
// </copyright_statement>

import './CodeEditor.scss';
import bind from '@/utils/bind';
import {LitElement, html} from 'lit';
import {customElement} from 'lit/decorators.js';
import * as ace from 'ace-builds';
import 'ace-builds/src-noconflict/ext-language_tools';

ace.config.set('basePath', '/static/ace');

const { user_info, exercise_details } = window.templateData;
export const UndoManager: typeof ace.UndoManager = ace.require('ace/undomanager').UndoManager;

@customElement('code-editor')
export default class CodeEditor extends LitElement {
	private resizeObserver = new ResizeObserver(this.resize);
	public editor?: ace.Ace.Editor;
	
	protected firstUpdated(): void {
		this.editor = ace.edit(this.renderRoot.querySelector('.editor')!, {
			theme: `ace/theme/${user_info.ace_theme}`,
			fontSize: '12pt' as any,
			wrap: true,
		});

		if (user_info['enable_vim']) {
			this.editor.setKeyboardHandler("ace/keyboard/vim");
		}

		if (user_info["use_auto_complete"] && exercise_details["back_end"] != "not_code") {
			this.editor.setOptions({
				enableBasicAutocompletion: false,
				enableSnippets: true,
				enableLiveAutocompletion: true
			});
		}

		this.editor.commands.addCommands([
			{
				name : 'undo',
				bindKey: {win: "Ctrl-Z", mac: "Command-Z"},
				exec : function(editor){
					editor.session.getUndoManager().undo(editor.session);
				}
			},
			{
				name : 'redo1',
				bindKey: {win: "Ctrl-Shift-Z", mac: "Command-Shift-Z"},
				exec : function(editor){
					editor.session.getUndoManager().redo(editor.session);
				}
			},
			{
				name : 'redo2',
				bindKey: {win: "Ctrl-Y", mac: "Command-Y"},
				exec : function(editor){
					editor.session.getUndoManager().redo(editor.session);
				}
			},
		]);

		this.resizeObserver.observe(this);
		this.editor.focus();
	}

	disconnectedCallback(): void {
		this.resizeObserver.disconnect();
	}

	@bind
	private resize() {
		this.editor?.resize();
	}

	render() {
		return html`
			<div class="editor-container">
				<div class="editor"></div>
			</div>
		`;
	}

	public async setSession(session: ace.Ace.EditSession) {
		if (!this.editor) {
			await this.updateComplete;
		}
		if (exercise_details["back_end"] === "not_code") {
			session.setUseWrapMode(true);
		}
		this.editor?.setSession(session);
	}

	public async setReadOnly(readOnly: boolean) {
		if (!this.editor) {
		await this.updateComplete;
		}
		this.editor?.setReadOnly(readOnly);
	}
}
