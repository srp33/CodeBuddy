import { LitElement, html, TemplateResult } from 'lit';
import { customElement } from 'lit/decorators.js';
import './Timer.scss';
import { isTakingRestrictedAssignment } from '@/utils/exercise-service';

const { user_id, timer_deadline, assignment_details, course_basics, assignment_basics, check_for_restrict_other_assignments } = window.templateData;

@customElement('exercise-timer')
export class Timer extends LitElement {
	private is_admin: boolean = false;
	private has_shown_timer_warning: boolean = false;

	constructor() {
		super();
		this.is_admin = window.templateData.is_administrator || window.templateData.is_instructor || window.templateData.is_assistant;
	}

	// This method is invoked after render() has completed.
	updated(changedProperties) {
		super.updated(changedProperties);

		if (!this.is_admin) {
			if (assignment_details.has_timer || assignment_details.due_date) {
				this.checkEverySecond();
				setInterval(this.checkEverySecond, 1000);
			}

			if (check_for_restrict_other_assignments) {
				this.checkEveryMinute();
				setInterval(this.checkEveryMinute, 60000);
			}
		}
	}

	protected render(): TemplateResult {
		if (!assignment_details.has_timer || this.is_admin) {
			return html``;
		}

		return html`<a id="timer_button" class="button is-medium is-hidden is-warning mb-4" style="cursor: auto;"></a>`;
	}

	private async checkEverySecond() {
		var reload = false;

		if (assignment_details.has_timer) {
			let deadline = new Date(timer_deadline);
			// deadline.setMinutes(deadline.getMinutes() - deadline.getTimezoneOffset());

			const total = deadline!.getTime() - Date.now();
			const hours = Math.floor( (total/(1000*60*60)) % 24 );
			const minutes = Math.floor( (total/1000/60) % 60 );
			const seconds = Math.floor( (total/1000) % 60 );

			if (total < 120000 && !this.has_shown_timer_warning) {
				alert("Less than 2 minutes remaining.");
				this.has_shown_timer_warning = true;
			}

			if (hours <= 0 && minutes <= 0 && seconds <= 0) {
				reload = true;
			}
			else {
				let timer_button = document.getElementById("timer_button");

				if (timer_button) {
					timer_button.classList.remove("is-hidden");
					timer_button.innerHTML = `<strong>Time remaining: ${hours}h ${minutes}m ${seconds}s</strong>`;
				}
			}
		}

		if (!reload && assignment_details.due_date && !assignment_details.allow_late && !assignment_details.view_answer_late) {
			let due_date = new Date(assignment_details.due_date);
			// due_date.setMinutes(due_date.getMinutes() - due_date.getTimezoneOffset());

			if (Date.now() > due_date.getTime()) {
				reload = true;
			}
		}

		if (reload) {
			setTimeout(() => {
				window.location.replace(`/assignment/${course_basics['id']}/${assignment_basics['id']}`);
			}, 1000);
		}
	}

	private async checkEveryMinute() {
		if (check_for_restrict_other_assignments) {
			if (await isTakingRestrictedAssignment(user_id, assignment_basics.id)) {
				setTimeout(() => {
					window.location.replace(`/assignment/${course_basics['id']}/${assignment_basics['id']}`);
				}, 1000);
			}
		}
	}
}
