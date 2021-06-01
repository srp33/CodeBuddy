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

// allow pasting images into markdown fields
$('div[contenteditable]').bind('paste', function(e) {
  if (e.originalEvent.clipboardData.items[0].kind != "string") {
  	var data = e.originalEvent.clipboardData.items[0].getAsFile()
  	var elem = this;
  	var fr = new FileReader;

  	fr.onloadend = function() {
  	  var img = new Image;
  	  img.src = fr.result;
  	  img.onload = function() {
  		  $(elem).append(img);
  	  };
  	};

  	fr.readAsDataURL(data);
  	e.preventDefault();
  }
});
