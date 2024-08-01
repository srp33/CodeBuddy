// <copyright_statement>
//   CodeBuddy: A programming assignment management system for short-form exercises
//   Copyright (C) 2024 Stephen Piccolo
//   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
// </copyright_statement>

import bind from '@/utils/bind';
import {LitElement, html} from 'lit';
import { customElement, property, query, state } from 'lit/decorators.js';
import './SplitPane.scss';

const GUTTER_SIZE = 12;

@customElement('split-pane')
export default class SplitPane extends LitElement {
	@property()
	direction: 'vertical' | 'horizontal' = 'vertical';	

	@property()
	fixedSide: 'first' | 'second' = 'first';	

	@property({attribute: false})
	minSizes: [number, number] = [0, 0];	

	@property()
	cacheID?: string;

	@property()
	first?: any;

	@property()
	second?: any;

	@property({type: Number})
	defaultSplit: number = 0.5;

	resizeCallback?: () => void;

	@state()
	private _currentSplit: number = 0;

	get currentSplit(): number {
		return this._currentSplit;
	}

	set currentSplit(val: number) {
		this._currentSplit = val;
		if (this.cacheID) {
			window.localStorage.setItem(`split-${this.cacheID}`, val.toString());
		}
	}
	
	private resizeObserver = new ResizeObserver(this.onResize);

	
	@query('.split')
	private parent!: HTMLDivElement;
	@query('.split-first')
	private firstContainer!: HTMLDivElement;
	@query('.split-second')
	private secondContainer!: HTMLDivElement;
	

	firstUpdated(): void {
		let defaultSplit = this.defaultSplit;
		if (this.cacheID) {
			const cachedVal = window.localStorage.getItem(`split-${this.cacheID}`);
			if (cachedVal?.length) {
				const cachedNum = Number(cachedVal);
				if (cachedNum >= 0 && cachedNum <= 1) {
					defaultSplit = cachedNum;
				}
			}
		}
		this.currentSplit = defaultSplit;

		this.resizeObserver.observe(this.parent);
		this.setSizes();
	}

	disconnectedCallback(): void {
		this.resizeObserver.disconnect();
	}

	@bind
	private onResize() {
		const parentRect = this.parent.getBoundingClientRect();
		const fullSize = this.direction === 'horizontal' ? parentRect.height : parentRect.width;

		const property = this.direction === 'horizontal' ? 'height' : 'width';
		if (this.fixedSide === 'first') {
			const firstSize = Number(this.firstContainer.style[property].replace('px', ''));

			this.currentSplit = (firstSize + (GUTTER_SIZE / 2)) / fullSize;
		} else {
			const secondtSize = Number(this.secondContainer.style[property].replace('px', ''));

			this.currentSplit = 1 - ((secondtSize + (GUTTER_SIZE / 2)) / fullSize);

		}

		this.setSizes();
	}

	@bind
	private setSizes() {
		// const { minSizes, direction, onResize } = this.props;
		if (this.currentSplit < 0) {
			this.currentSplit = 0;
		} else if (this.currentSplit > 1) {
			this.currentSplit = 1;
		}
		const minTotalSize = this.minSizes[0] + this.minSizes[1] + GUTTER_SIZE;
		const property = this.direction === 'horizontal' ? 'height' : 'width';
		const parentRect = this.parent.getBoundingClientRect();
		const fullSize = this.direction === 'horizontal' ? parentRect.height : parentRect.width;

		let firstSize = (fullSize * this.currentSplit) - (GUTTER_SIZE / 2);
		let secondSize = (fullSize * (1 - this.currentSplit)) - (GUTTER_SIZE / 2);

		if (minTotalSize <= fullSize) {
			if (firstSize < this.minSizes[0]) {
				firstSize = this.minSizes[0];
				secondSize = fullSize - firstSize - GUTTER_SIZE;
			} else if (secondSize < this.minSizes[1]) {
				secondSize = this.minSizes[1];
				firstSize = fullSize - secondSize - GUTTER_SIZE;
			}
			this.currentSplit = (firstSize + (GUTTER_SIZE / 2)) / fullSize;
		} else {
			this.currentSplit = (this.minSizes[0] + (GUTTER_SIZE / 1)) / minTotalSize;
			firstSize = (fullSize * this.currentSplit) - (GUTTER_SIZE / 2);
			secondSize = (fullSize * (1 - this.currentSplit)) - (GUTTER_SIZE / 2);
		}


		this.firstContainer.style[property] = `${firstSize}px`;
		this.secondContainer.style[property] = `${secondSize}px`;

		if (this.resizeCallback) {
			this.resizeCallback();
		}
	}

	@bind
	private onDown() {
		document.body.style.cursor = this.direction === 'horizontal' ? 'row-resize' : 'col-resize';
		this.firstContainer.style.userSelect = 'none';
		this.firstContainer.style.pointerEvents = 'none';
		this.secondContainer.style.userSelect = 'none';
		this.secondContainer.style.pointerEvents = 'none';

		const handlePointerMove = (e: PointerEvent) => {
			const pos = this.direction === 'horizontal' ? e.clientY : e.clientX;
			const parentRect = this.parent.getBoundingClientRect();
			const fullSize = this.direction === 'horizontal' ? parentRect.height : parentRect.width;

			const relativeDistance = this.direction === 'horizontal' ?  pos - parentRect.top : pos - parentRect.left;

			this.currentSplit = (relativeDistance / fullSize);
			this.setSizes();
		};

		const handlePointerUp = () => {
			document.body.style.cursor = '';
			this.firstContainer.style.userSelect = '';
			this.firstContainer.style.pointerEvents = '';
			this.secondContainer.style.userSelect = '';
			this.secondContainer.style.pointerEvents = '';
			window.removeEventListener('pointermove', handlePointerMove);
			window.removeEventListener('pointerup', handlePointerUp);
		};

		window.addEventListener('pointermove', handlePointerMove, { passive: true });
		window.addEventListener('pointerup', handlePointerUp, { passive: true });
	}

	@bind
	private onDoubleClick() {
		if (this.currentSplit === this.defaultSplit) {
			this.currentSplit = 1 - this.defaultSplit;
		} else {
			this.currentSplit = this.defaultSplit;
		}
		this.setSizes();
	}


	protected render() {
		return html`
		  	<div  class="split ${this.direction}">
				<div class="split-first">
					${this.first}
				</div>
				<div class="gutter" @pointerdown=${this.onDown} @dblclick=${this.onDoubleClick}>
					<i class="fas fa-ellipsis-v"></i>
				</div>
				<div class="split-second">
					${this.second}
				</div>
			</div>
		`;
	}

}