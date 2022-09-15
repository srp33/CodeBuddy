import './CodeEditor.scss';
import bind from '@/utils/bind';
import {LitElement, html} from 'lit';
import {customElement} from 'lit/decorators.js';
import * as ace from 'ace-builds/';

ace.config.set('basePath', '/static/ace');

const { user_info } = window.templateData;
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
	this.editor?.setSession(session);
  }

  public async setReadOnly(readOnly: boolean) {
	if (!this.editor) {
	  await this.updateComplete;
	}
	this.editor?.setReadOnly(readOnly);
  }
}
