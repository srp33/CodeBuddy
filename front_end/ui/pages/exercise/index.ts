import './excercise.scss';
import '../../css/bulma-tooltip.scss';
import '../../css/styles.css';
import '../../css/spa.scss';
import ExerciseApp from './ExerciseApp';
import {LitElement} from 'lit';

// disable shadow DOM 😢
(LitElement.prototype as any).createRenderRoot = function() {
	return this;
}

let initialized = false;
async function init() {
	if (initialized) return;
	const container = document.getElementById('app');
	if (container) {
		initialized = true;

		const app = new ExerciseApp();
		container.appendChild(app);
	}

}

if (document.readyState === 'complete') {
	init();
} else {
	document.addEventListener('readystatechange', () => {
		if (document.readyState === 'interactive' || document.readyState === 'complete') {
			init();
		}
	});
}
