// <copyright_statement>
//   CodeBuddy: A programming assignment management system for short-form exercises
//   Copyright (C) 2024 Stephen Piccolo
//   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
// </copyright_statement>

/* eslint-disable @typescript-eslint/no-non-null-assertion */
/* eslint-disable @typescript-eslint/ban-types */
export function bind<T extends Function>(target: object, propertyKey: string, descriptor: TypedPropertyDescriptor<T>): TypedPropertyDescriptor<T> | void {
	if(!descriptor || (typeof descriptor.value !== 'function')) {
		throw new TypeError(`Only methods can be decorated with @bind. <${propertyKey}> is not a method!`);
	}

	return {
		configurable: true,
		get(this: T): T {
			const bound: T = descriptor.value!.bind(this);
			// Credits to https://github.com/andreypopp/autobind-decorator for memoizing the result of bind against a symbol on the instance.
			Object.defineProperty(this, propertyKey, {
				value: bound,
				configurable: true,
				writable: true,
			});
			return bound;
		},
	};
}

export default bind;