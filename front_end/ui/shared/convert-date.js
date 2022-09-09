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
