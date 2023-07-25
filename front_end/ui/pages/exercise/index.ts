// <copyright_statement>
//   CodeBuddy - A learning management system for computer programming
//   Copyright (C) 2023 Stephen Piccolo
//   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
// </copyright_statement>

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
