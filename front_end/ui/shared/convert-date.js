// <copyright_statement>
//   CodeBuddy: A programming assignment management system for short-form exercises
//   Copyright (C) 2023 Stephen Piccolo
//   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
// </copyright_statement>

//displaying start and due dates on the course table
function convertDate(d) {
	var days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
	var hours = d.getHours();
	var minutes = d.getMinutes() < 10 ? "0" + d.getMinutes():d.getMinutes();
	var suffix = hours >= 12 ? "PM":"AM";
	var time = ((hours + 11) % 12 + 1) + ":" + minutes + " " + suffix;
  
	var start_date = days[d.getDay()] + " " + (d.getMonth() + 1) + "/" + d.getDate() + "/" + d.getFullYear().toString().substr(-2) +
	" " + time;
	return start_date;
}
window.convertDate = convertDate;
