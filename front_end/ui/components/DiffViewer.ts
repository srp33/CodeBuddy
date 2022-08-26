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