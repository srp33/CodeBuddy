import { LitElement, html, TemplateResult } from 'lit';
import { customElement } from 'lit/decorators.js';
import './Timer.scss';

const { start_time, assignment_details, course_basics, assignment_basics } = window.templateData;

@customElement('exercise-timer')
export class Timer extends LitElement {
	private deadline?: Date;
	private intervalID: number = -1;

	constructor() {
		super();
		const isAdmin = window.templateData.is_administrator || window.templateData.is_instructor || window.templateData.is_assistant;
		if (!isAdmin && assignment_details.has_timer) {
			const start_time_js = new Date(start_time);
			start_time_js.setMinutes(start_time_js.getMinutes() - start_time_js.getTimezoneOffset());
			
			this.deadline = start_time_js;
			this.deadline.setHours(this.deadline.getHours() + assignment_details.hour_timer);
			this.deadline.setMinutes(this.deadline.getMinutes() + assignment_details.minute_timer);

			this.intervalID = setInterval(() => {
				this.requestUpdate();
			}, 1000);
		}
	}

	protected render(): TemplateResult {
		if (!this.deadline) {
			return html``;
		}
		const { hours, minutes, seconds } = this.remainingTime;
		return html`
			<h4>Time remaining</h4>
			<div class="timer-container">
				<span class="time-group">
					<span>${hours >= 0 ? hours : 0}</span>
					<span>Hours</span>
				</span>
				<span class="time-group">
					<span>${minutes >= 0 ? minutes : 0}</span>
					<span>Minutes</span>
				</span>
				<span class="time-group">
					<span>${seconds >= 0 ? seconds : 0}</span>
					<span>Seconds</span>
				</span>
			</div>
		`;
	}

	private get remainingTime() {
		const total = this.deadline!.getTime() - Date.now();
		const seconds = Math.floor( (total/1000) % 60 );
		const minutes = Math.floor( (total/1000/60) % 60 );
		const hours = Math.floor( (total/(1000*60*60)) % 24 );

		if (hours <= 0 && minutes <= 0 && seconds <= 0) {
			clearInterval(this.intervalID);
			let redirect = true;
			if (assignment_details.due_date) {
				const due_date = new Date(assignment_details.due_date);
				if (due_date.getTime() < Date.now()) {
					redirect = false;
				}
			}
			if (redirect) {
				setTimeout(() => {
					window.location.replace(`/assignment/${course_basics['id']}/${assignment_basics['id']}`);
				}, 1000);
			}
		}

		return {
			total,
			hours,
			minutes,
			seconds
		};
	}

}
