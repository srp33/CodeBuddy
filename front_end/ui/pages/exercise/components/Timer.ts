import { LitElement, html, TemplateResult } from 'lit';
import { customElement } from 'lit/decorators.js';
import './Timer.scss';

const { start_time, assignment_details } = window.templateData;

@customElement('exercise-timer')
export class Timer extends LitElement {
	private deadline?: Date;
	private intervalID: number = -1;

	constructor() {
		super();
		const isAdmin = window.templateData.is_administrator || window.templateData.is_instructor;
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
					<span>${hours}</span>
					<span>Hours</span>
				</span>
				<span class="time-group">
					<span>${minutes}</span>
					<span>Minutes</span>
				</span>
				<span class="time-group">
					<span>${seconds}</span>
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
			setTimeout(() => {
				window.location.reload();
			}, 1000);
		}

		return {
			total,
			hours,
			minutes,
			seconds
		};
	}

}
