import './TestsPane.scss';
import {LitElement, html, TemplateResult} from 'lit';
import {customElement, property, state} from 'lit/decorators.js';
import { unsafeHTML } from 'lit/directives/unsafe-html.js';
import bind from '@/utils/bind';
import { runCode, RunCodeResponse, submitCode } from '@/utils/exercise-service';
import bulmaCollapsible from '@creativebulma/bulma-collapsible';


enum TestStatus {
	Unknown = 'Unknown',
	Running = 'Running',
	Passed = 'Passed',
	Failed = 'Failed',
}

interface Test {
	name: string;
	test_id: number
	after_code: string;
	before_code: string;
	can_see_code_output: boolean;
	can_see_expected_output: boolean;
	can_see_test_code: boolean;
	instructions: string;
	jpg_output: unknown
	txt_output: string;
	status: TestStatus;
}

@customElement('tests-pane')
export class TestsPane extends LitElement {
	@property()
	addSubmission?: (submission: Submission) => void;

	private getCode?: () => string;

	@state()
	tests: Test[];

	@state()
	testOutputs: {[key: string]: {
		txt_output: string;
		jpg_output: string;
	}} = {};

	@state()
	private errorMessage: string = '';

	constructor() {
		super();
		this.tests = [];
		const testMap = window.templateData.exercise_details.tests;
		for (const testName in testMap) {
			if (testMap.hasOwnProperty(testName)) {
				const test = testMap[testName];
				test.name = testName;
				test.status = TestStatus.Unknown;
				this.tests.push(test);
			}
		}
		this.tests.sort((a, b) => a.test_id - b.test_id);
	}

	render() {
		return html`
			<div class="tests-pane">
				<div class="tests-header">
					<p>Tests</p>
					<button class="button is-primary is-outlined" @click=${() => this.runCode()}>Run all tests</button>
					<button class="button is-dark" @click=${() => this.submitCode()}>Submit exercise</button>
				</div>
				${this.errorMessage?.length > 0 ? html`
					<article class="message is-danger">
						<div class="message-header">
							<p>An error occurred while your code was being processed.</p>
							<button class="delete" aria-label="delete" @click=${() => this.errorMessage = ''}></button>
						</div>
						<div class="message-body">
							${unsafeHTML(this.errorMessage)}
						</div>
					</article>
				` : null}
				<table class="table is-fullwidth is-hoverable" style="margin-bottom: 20px;">
					<thead>
						<tr>
							<th>Status</th>
							<th style="width: 100%;">Test</th>
							<th></th>
						</tr>
					</thead>
					<tbody>
						${this.tests.map((test) => html`
							<tr>
								<td class="test-status">${this.getStatusIcon(test.status)}</td>
								<td>${test.name}</td>
								<td>
									<test-results-modal
										.test=${test}
										.runTest=${this.runCode}
										.testStatus=${test.status}
										.expectedOutput=${test.txt_output}
										.userOutput=${this.testOutputs[test.name]?.txt_output ?? ''}
									></test-results-modal>
								</td>
							</tr>
						`)}
					</tbody>

				</table>
			</div>
		`;
	}

	private getStatusIcon(status: TestStatus): TemplateResult {
		switch (status) {
			case TestStatus.Passed:
				return html`<i class="fas fa-check passed has-tooltip-right" data-tooltip="Passed"></i>`;
			case TestStatus.Failed:
				return html`<i class="fas fa-times failed has-tooltip-right" data-tooltip="Failed"></i>`;
			case TestStatus.Running:
				return html`<i class="fas fa-spinner fa-spin running has-tooltip-right" data-tooltip="Running"></i>`;
			default:
				return html`<i class="fas fa-question unknown has-tooltip-right" data-tooltip="Run code to see result"></i>`;
		}
	}

	@bind
	private async runCode(testName?: string) {
		for (const test of this.tests) {
			if (!testName || testName === test.name) {
				test.status = TestStatus.Running;
			}
		}

		this.requestUpdate();
		
		const result = await runCode(window.templateData.course_basics.id, window.templateData.assignment_basics.id, window.templateData.exercise_basics.id, this.getCode!(), testName);
		this.processResult(result);
		this.requestUpdate();
	}

	@bind
	private async submitCode() {
		for (const test of this.tests) {
			test.status = TestStatus.Running;
		}

		this.requestUpdate();
		const code = this.getCode!();
		const result = await submitCode(window.templateData.course_basics.id, window.templateData.assignment_basics.id, window.templateData.exercise_basics.id, code);
		this.processResult(result);

		this.requestUpdate();
		if (result.submission_id) {
			this.addSubmission?.({
				id: result.submission_id,
				date: new Date(),
				code,
				passed: !!result.all_passed,
			});
		}
	}

	private processResult(result: RunCodeResponse) {
		if (result.message?.length > 0) {
			for (const test of this.tests) {
				test.status = TestStatus.Failed;
			}
			this.errorMessage = result.message;
		} else {	
			for (const test of this.tests) {
				if (result.test_outputs[test.name]) {
					test.status = result.test_outputs[test.name]?.passed ? TestStatus.Passed : TestStatus.Failed;
				}
			}
			Object.assign(this.testOutputs, result.test_outputs);
		}
	}
}

enum OutputTab {
	Plain = 'Plain Output',
	Diff = 'Diff Output',
}

@customElement('test-results-modal')
export class TestResultsModal extends LitElement {
	@state()
	open = false;

	@property()
	testStatus?: TestStatus;

	@property()
	test?: Test;

	@property()
	userOutput?: string;

	@property()
	expectedOutput?: string;

	@property()
	runTest?: (testName: string) => Promise<void>;

	
	@state()
	currentTab = OutputTab.Plain;
	
	tabs = [OutputTab.Plain, OutputTab.Diff];
	tabOutputs = {
		[OutputTab.Plain]: () => html`
			<div class="plain-output-section">
				<div>
					<h3>Your output:</h3>
					<pre>${this.userOutput}</pre>
				</div>
				<div>
					<h3>Correct output:</h3>
					<pre>${this.expectedOutput}</pre>
				</div>
			</div>
		`,
		[OutputTab.Diff]: () => html`
			<div class="diff-section">
				<div class="diff-section-header">
					<span style="flex: 1;">Correct output:</span>
					<span style="flex: 1;">Your output:</span>
				</div>
				<diff-viewer .left=${this.expectedOutput} .right=${this.userOutput}></diff-viewer>
			</div>
		`,
	}

	render() {
		return html`
			<button class="button is-small" ?disabled=${this.testStatus === TestStatus.Running} @click=${() => this.runTest?.(this.test!.name)}>${this.getRunButtonText()}</button>
			<button class="button is-small" @click=${this.openModal}>View details</button>
			${this.open ? html`
				<div class="modal is-active">
					<div class="modal-background" @click=${this.closeModal}></div>
					<div class="modal-card">
						<header class="modal-card-head">
							<p class="modal-card-title">Test results: ${this.test?.name}</p>
							<button class="delete" aria-label="close" @click=${this.closeModal}></button>
						</header>
						<section class="modal-card-body">

							<div id="accordion">
								${this.test?.instructions ? html`
									<article class="message">
										<div class="message-header">
											<a href="#instruction-section" data-action="collapse">Instructions</a>
										</div>
										<div id="instruction-section" class="message-body is-collapsible" data-parent="accordion">
											<div class="message-body-content">
												${unsafeHTML(this.test?.instructions)}
											</div>
										</div>
									</article>
								` : null}
								
								${this.test?.can_see_test_code ? html`
								<article class="message">
									<div class="message-header">
										<a href="#test-code-section" data-action="collapse">Test code</a>
									</div>
									<div id="test-code-section" class="message-body is-collapsible" data-parent="accordion">
										<div class="message-body-content">
											${this.test?.before_code ? html`
												<p>Code run before your code:</p>
												<pre>${this.test?.before_code}</pre>
											` : null}
											${this.test?.after_code ? html`
												<p>Code run after your code:</p>
												<pre>${this.test?.after_code}</pre>
												` : null}
											${!!this.test?.before_code && !!this.test?.after_code ? html`
												<p>No additional code is run before or after your code.</p>
											` : null}
										</div>
									</div>
								</article>
								` : html`
									<article class="message">
										<div class="message-header">
											<p disabled>Test code is hidden for this test</p>
										</div>
									</article>
								`}
								${this.test?.can_see_expected_output || this.test?.can_see_code_output ? html`
									<article class="message grow">
										<div class="message-header">
											<a href="#output-section" data-action="collapse">Code output</a>
										</div>
										<div id="output-section" class="message-body is-collapsible" data-parent="accordion">
											<div class="message-body-content">
												${this.getTestOutput()}
											</div>
										</div>
									</article>
								` : html`
									<article class="message">
										<div class="message-header">
											<p disabled>You cannot see any output from this test.</p>
										</div>
									</article>
								`}
							</div>
						</section>
					</div>
				</div>		
			` : null}
		`;
	}

	@bind
	async openModal() {
		this.open = true;
		await this.updateComplete;
		const collapsibles = bulmaCollapsible.attach('.is-collapsible');
		for (const collapsible of collapsibles) {
			collapsible.open();
		}
	}

	@bind
	closeModal() {
		this.open = false;
	}

	@bind
	private getRunButtonText(): string | TemplateResult {
		switch (this.testStatus) {
			case TestStatus.Running:
				return html`Run test <i class="fas fa-spinner fa-spin running"></i>`;
			case TestStatus.Passed:
			case TestStatus.Failed:
			case TestStatus.Unknown:
				return html`Run test <i class="fas fa-play"></i>`;
			default:
				return '';
		}
	}

	@bind
	private getTestOutput(): TemplateResult {
		switch (this.testStatus) {
			case TestStatus.Passed:
				return html`
					<div class="plain-output-section">
						<div>
							<h3>Your output:</h3>
							<pre>${this.userOutput}</pre>
						</div>
						<h2>Test passed 🎉!!!</h2>
					</div>
				`;
			case TestStatus.Failed:
				if (this.test?.can_see_code_output && this.test?.can_see_expected_output) {
					return html`
						<div>
							<div class="tabs">
								<ul>
									${this.tabs.map(tab => html`
										<li class=${tab === this.currentTab ? 'is-active' : ''} @click=${() => this.currentTab = tab}><a>${tab}</a></li>
									`)}
								</ul>
							</div>
						</div>
						${this.tabOutputs[this.currentTab]()}				
					`;
				} else if (this.test?.can_see_code_output) {
					return html`
					<div class="plain-output-section">
						<div>
							<h3>Your output:</h3>
							<pre>${this.userOutput}</pre>
						</div>
						<div>
							<h3>You cannot see the expected output for this test.</h3>
						</div>
					</div>
				`
				} else if (this.test?.can_see_expected_output) {
					return html`
					<div class="plain-output-section">
						<div>
							<h3>You cannot see your output for this test.</h3>
						</div>
						<div>
							<h3>Correct output:</h3>
							<pre>${this.expectedOutput}</pre>
						</div>
					</div>
					`
				}
				// should be unreachable
				return html``;
			default:
				return html`
					<div class="no-output-section">
						This test has not been run yet.
					</div>
				`;
		}
	}


}
