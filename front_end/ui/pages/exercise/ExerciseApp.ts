// <copyright_statement>
//   CodeBuddy: A programming assignment management system for short-form exercises
//   Copyright (C) 2023 Stephen Piccolo
//   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
// </copyright_statement>

import '@/components/CodeEditor';
import '@/components/DiffViewer';
import '@/components/SplitPane';
import './components/Timer';
import './components/TestsPane';

import {LitElement, html, TemplateResult} from 'lit';
import {customElement, property, state} from 'lit/decorators.js';
import { unsafeHTML } from 'lit/directives/unsafe-html.js';
import { ref } from 'lit/directives/ref.js';
import CodeEditor, { UndoManager } from '@/components/CodeEditor';
import bind from '@/utils/bind';
import { copyExercise, savePresubmission } from '@/utils/exercise-service';
import * as ace from 'ace-builds';
import { debounce } from '@/utils/debounce';
import { oneAtATime } from '@/utils/oneAtATime';

const { code_completion_path, submissions, exercise_details, presubmission } = window.templateData;

const courseID = window.templateData.course_basics.id;
const assignmentID = window.templateData.assignment_basics.id;
const exerciseID = window.templateData.exercise_basics.id;

const SAVE_DEBOUNCE_TIME = 2000;

interface File {
	name: string;
	type: 'user-code' | 'data-file'
}

@customElement('exercise-app')
export default class ExerciseApp extends LitElement {
	@state()
	private saved = true;

	@state()
	private files?: File[];

	@state()
	private selectedFile?: string;

	@state()
	private submissions: Submission[] = submissions?.map?.((s: any) => ({
		id: s.id,
		date: new Date(s.date),
		code: s.code,
		passed: !!s.passed,
		test_outputs: s.test_outputs,
	})) ?? [];

	private editor?: CodeEditor;
	private sessions: { [key: string]: ace.Ace.EditSession } = {};
	private userCodeFileName = 'code';

	render() {
		const activeSubmission = this.activeSubmission;
		return html`
			<div style="height: 100%;">
				<split-pane
					direction="vertical"
					cacheID="exercise-vertical"
					.defaultSplit=${0.3}
					.minSizes=${[200, 380]}
					.first=${html`
						<information-pane
							.files=${this.files}
							.submissions=${this.submissions}
							.selectedFile=${this.selectedFile}
							.onFileSelected=${this.onFileSelected}
						></information-pane>
					`}
					.second=${html`
						<split-pane
							direction="horizontal"
							cacheID="exercise-horizontal"
							.defaultSplit=${0.7}
							.minSizes=${[100, 100]}
							.fixedSide='second'
							.first=${html`
								<div class="edit-section">
									<code-editor ${ref(this.setEditor)}></code-editor>
									${activeSubmission ? html`
									<article class="message is-warning" style="margin-bottom: 0px;">
										<div class="message-header">
											<p>You are viewing submission ${activeSubmission.id + 1} from ${activeSubmission.date.toLocaleString()}</p>
											<span style="flex: 1;"></span>
											<button class="button is-small outlined" @click=${this.copySubmissionCode}>Restore this version</button>
											<button
												style="margin-left: 8px;"
												class="button is-small outlined"
												@click=${() => this.onFileSelected(this.userCodeFileName)}
											>Return to latest version</button>
										</div>
									</article>
									` : null}
									${this.selectedFile === this.userCodeFileName ? 
										html`
											<div class="save-indicator">
												${this.saved ? html`
													<i class="fas fa-check has-tooltip-left" data-tooltip="Saved"></i>
												` : html`
													<i class="fas fa-spinner fa-spin running has-tooltip-left" data-tooltip="Saving"></i>
												` }
											</div>
										`
									: null}
								</div>
							`}
							.second=${html`
								<tests-pane 
									.getCode=${this.getUserCode}
									.activeSubmission=${this.activeSubmission}
									.addSubmission=${this.addSubmission}
									.numSubmissions=${this.submissions.length}
									.hasPassingSubmission=${this.hasPassingSubmission}
									.selectPassingSubmission=${() => {
										for (let i = this.submissions.length - 1; i >= 0; i--) {
											const submission = this.submissions[i];
											if (submission.passed) {
												this.onFileSelected(`submission-${submission.id}`);
												break;
											}
										}
									}}
								></tests-pane>
							`}
						>
						</split-pane>
					`}
				></split-pane>
			</div>
		`;
	}

	@bind
	private setEditor(editor?: Element) {
		if (editor instanceof CodeEditor) {
			const firstTime = !this.editor;
			this.editor = editor;

			// set the editor's initial value by creating a new session
			if (firstTime) {
				let value: string = '';
				if (presubmission) {
					value = presubmission
				} else if (submissions?.length > 0) {
					value = submissions[submissions.length - 1].code;
				} else if (exercise_details?.starter_code) {
					value = exercise_details.starter_code;
				}
				
				const session = new ace.EditSession(value);
				session.setUndoManager(new UndoManager());
				session.setMode(code_completion_path);
				// setup the auto save
				const saveCode = debounce(oneAtATime(async () => {
					await savePresubmission(courseID, assignmentID, exerciseID, session.getValue());
					this.saved = true;
				}), SAVE_DEBOUNCE_TIME);
				session.on('change', () => {
					this.saved = false;
					saveCode();
				});

				this.editor.setSession(session);
				
				switch (exercise_details.back_end) {
					case 'python_script':
						this.userCodeFileName = 'code.py';
						break;
				}
				this.sessions[this.userCodeFileName] = session;
				const files: File[] = [{name: this.userCodeFileName, type: 'user-code'}];
					
				for (const fileName in exercise_details.data_files) {
					const fileContents = exercise_details.data_files[fileName];
					const session = new ace.EditSession(fileContents);
					session.setUndoManager(new UndoManager());
					const match = fileName.match(/.*\.(.*)$/);
					if (match && match[1]) {
						const ext = match[1];
						switch (ext) {
							case 'py':
								session.setMode('ace/mode/python');
								break;
						}
					}
					this.sessions[fileName] = session;
					files.push({name: fileName, type: 'data-file'});
				}
				for (const submission of this.submissions) {
					const session = new ace.EditSession(submission.code);
					session.setMode(code_completion_path);
					this.sessions[`submission-${submission.id}`] = session;
				}
				this.files = files;
				this.selectedFile = this.userCodeFileName;
			}
		}
	}

	@bind
	private getUserCode(): string {
		return this.sessions[this.userCodeFileName]?.getValue();
	}

	@bind
	private onFileSelected(name: string) {
		const session = this.sessions[name];
		if (session) {
			this.editor?.setSession(session);
			this.editor?.setReadOnly(name !== this.userCodeFileName);
			this.selectedFile = name;
		}
	}

	@bind
	private addSubmission(submission: Submission) {
		this.submissions = [...this.submissions, submission];
		const session = new ace.EditSession(submission.code);
		session.setMode(code_completion_path);
		this.sessions[`submission-${submission.id}`] = session;
	}

	@bind
	private copySubmissionCode() {
		if (!confirm("Do you want to overwrite your existing code?")) {
			return;
		};
		const oldSession = this.sessions[this.selectedFile!];
		const newSession = this.sessions[this.userCodeFileName];
		newSession.setValue(oldSession.getValue());
		this.onFileSelected(this.userCodeFileName);
	}


	get hasPassingSubmission(): boolean {
		return !!this.submissions?.find((submission) => !!submission.passed);
	}

	get activeSubmission(): Submission | undefined {
		if (this.selectedFile?.startsWith('submission-')) {
			const id = Number(this.selectedFile.replace('submission-', ''));
			return this.submissions.find((s) => s.id === id);
		}
		return undefined;
	}
}

enum Tab {
	Information = 'Information',
	Code = 'Code',
	Submissions = 'Submissions',
}

@customElement('information-pane')
class InformationPane extends LitElement {
	@property()
	private submissions?: Submission[];

	@property()
	private onFileSelected?: (name: string) => void;

	@property()
	private selectedFile?: string;

	@property()
	private files?: File[];

	@state()
	private showHint = false;

	@state()
	private copyModalOpen = false;

	@state()
	private deleteModalOpen = false;

	@state()
	private selectedTab: Tab = window.localStorage.getItem(`selected-tab-${exerciseID}`) as Tab ?? Tab.Information;

	private tabPanels: {[key in Tab]: () => TemplateResult} = {
		[Tab.Information]: () => html`
			<div class="content is-medium">
				<h6>${unsafeHTML(window.templateData.exercise_basics.title)}</h6>
				${exercise_details.enable_pair_programming ? html`
					<div style="margin-bottom: 16px;">
						<i class="fab fa-product-hunt"></i>
						<em>Pair programming is enabled for this exercise.</em>
					</div>
				` : null}
				${unsafeHTML(window.templateData.exercise_details.instructions)}
			</div>
			${exercise_details.hint ? html`
				<div>
					<button class="button is-warning" @click=${() => this.showHint = !this.showHint}>
						${this.showHint ? 'Hide hint' : 'Show hint'}
					</button>
				</div>
				${this.showHint ? html`
					<div class="content is-medium" style="margin-top: 8px;">
						${unsafeHTML(exercise_details.hint)}
					</div>
				` : null}
			` : null}
		`,
		[Tab.Code]: () => html`
			<div class="file-list content is-medium">
				<h6>Files</h6>
				<strong>User code:</strong>
				${this.files?.filter((file) => file.type === 'user-code').map(file => html`
					<span
						class="file-list-item${this.selectedFile === file.name ? ' active' : ''}"
						@click=${() => this.onFileSelected?.(file.name)}
					>${file.name}</span>
				`)}
				${this.hasDataFiles ? html`
					<strong class="file-header">Data files:</strong>
					${this.files?.filter((file) => file.type === 'data-file').map(file => html`
						<span
							class="file-list-item${this.selectedFile === file.name ? ' active' : ''}"
							@click=${() => this.onFileSelected?.(file.name)}
						>${file.name}</span>
					`)}
				` : null}
			</div>
		`,
		[Tab.Submissions]: () => html`
			<div class="submission-list content is-medium">
				<h6>Submissions</h6>
				${this.submissions?.map((submission, i) => html`
					<span
						class="submission ${submission.passed ? 'passed' : 'failed'}${this.selectedFile === `submission-${submission.id}` ? ' selected' : ''}"
						@click=${() => this.onFileSelected?.(`submission-${submission.id}`)}
					>
						${i + 1}. ${submission.date.toLocaleString()}
					</span>
				`)}
			</div>
		`,
	}

	private tabIcons: {[key in Tab]: string} = {
		[Tab.Information]: 'fas fa-info-circle',
		[Tab.Code]: 'fas fa-folder',
		[Tab.Submissions]: 'fas fa-history',
	}

	private tabTitles: {[key in Tab]: string} = {
		[Tab.Information]: 'Instructions',
		[Tab.Code]: 'Files',
		[Tab.Submissions]: 'Submissions',
	}

	panelOrder: Tab[] = [Tab.Information, Tab.Code, Tab.Submissions];

	render() {
		return html`
			<div class="left-panel">
				<div class="tab-bar">
					${this.panelOrder.map((tab) => html`
						<button
							class="icon-button${this.selectedTab === tab ? ' active' : ''} has-tooltip-right"
							data-tooltip="${this.tabTitles[tab]}"
							@click=${() => this.selectTab(tab)}
						>
							<i class="${this.tabIcons[tab]}"></i>
						</button>
					`)}

					${window.templateData.is_administrator || window.templateData.is_instructor || window.templateData.is_assistant ? html`

						<span class="spacer"></span>
						<button class="icon-button">
							<a href="/edit_exercise/${courseID}/${assignmentID}/${exerciseID}">
								<i class="fas fa-cog"></i>
							</a>
						</button>

						${this.copyModalOpen ? html`<copy-exercise-modal .onClose=${() => this.copyModalOpen = false}></copy-exercise-modal>` : null}
						<!-- TODO: create the delete modal -->

					` : null}
				</div>
				<div class="info-panel">
					<exercise-timer></exercise-timer>
					${this.tabPanels[this.selectedTab]?.()}
				</div>
			</div>
		`;
	}

	@bind
	selectTab(tab: Tab) {
		this.selectedTab = tab;
		localStorage.setItem(`selected-tab-${exerciseID}`, tab);
	}

	get hasDataFiles(): boolean {
		return this.files?.filter((file) => file.type === 'data-file')?.length as number > 0;
	}
}

@customElement('copy-exercise-modal')
class CopyExerciseModal extends LitElement {

	@property({type: Boolean})
	onClose?: () => void;

	@state()
	errorMessage = '';


	render() {
		const title = window.templateData.exercise_basics.title;
		return html`
			<div class="modal is-active">
				<div class="modal-background" @click=${this.onClose}></div>
				<div class="modal-card">
					<header class="modal-card-head">
						<p class="modal-card-title">Copy exercise within the same assignment:</p>
						<button class="delete" aria-label="close" @click=${this.onClose}></button>
					</header>
					<section class="modal-card-body">
						<div class="field">
							<label class="label">New title</label>
							<input class="input is-medium is-primary" type="text" id="new_title" name="new_title" placeholder=${title} value=${title}>
							${this.errorMessage ? html`<p class="help is-danger">${this.errorMessage}</p>` : null}
						</div>
					</section>
					<footer class="modal-card-foot">
						<button class="button is-primary" @click=${this.onSave}>Save changes</button>
					</footer>
				</div>
			</div>
		`;
	}

	@bind
	async onSave() {
		const input: HTMLInputElement = this.renderRoot.querySelector('#new_title')!;
		if (!input.value) {
			this.errorMessage = 'New title is required';
			return;
		}
		if (input.value === window.templateData.exercise_basics.title) {
			this.errorMessage = 'New title is the same as the old title';
			return;
		}
		const error = await copyExercise(courseID, assignmentID, exerciseID, input.value);
		if (error) {
			this.errorMessage = error;
		}
	}
}
