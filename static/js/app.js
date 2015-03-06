$('#myform').on('submit', function (e) {
	e.preventDefault();
	
	// var formElement = document.getElementById("myform");
	// var formData = new FormData(formElement);
	// var request = new XMLHttpRequest();
	// request.open("POST", "/upload");
	// request.send(new FormData(formElement));
	
	$('input[type="file"]').each(function () {
		var file = this.files[0];
		var formData = new FormData()
		formData.append('file', file);
		var request = new XMLHttpRequest();
		request.open("POST", "/upload", true);
		request.onload = function (e) {
			console.log('uploaded');
			console.log(e);
			console.log(request.status);
			console.log(JSON.parse(request.response));
		}
		request.send(formData);
	})
	
	
	// var count = 0;
	// $('input[type="file"]').on('ajax', function(){
	//   var $this = $(this);
	//
	//   if (typeof this.files[count] === 'undefined') { return false; }
	//
	//   $.ajax({
	//     'type':'POST',
	// 		'url': '/upload',
	//     'data': (new FormData()).append('file', this.files[count]),
	//     'contentType': false,
	//     'processData': false,
	//     'xhr': function() {
	//       var xhr = $.ajaxSettings.xhr();
	//       if(xhr.upload){
	//         // xhr.upload.addEventListener('progress', progressbar, false);
	//       }
	//       return xhr;
	//      },
	//     'success': function(){
	//       count++;
	//         $this.trigger('ajax');
	//     },
	// 		'error': function (e) {
	//       count++;
	//       $this.trigger('ajax');
	// 			console.log(e);
	// 			console.log(e.statusText);
	// 		}
	//   });
	// }).trigger('ajax');

});