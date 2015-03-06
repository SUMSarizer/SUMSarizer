angular.module('myApp', [])

.config(function($interpolateProvider){
 $interpolateProvider.startSymbol('{[{').endSymbol('}]}');
})

.controller('DashboardCtrl', function ($scope) {
  $scope.uploadCount = 4;
});


$('#myform').on('submit', function (e) {
	e.preventDefault();
	
	var elInput = document.getElementById('files');
	var files = Array.prototype.slice.call(elInput.files);
	var uploadJobs = files.map(function (file, index) {
		return function () {
			var formData = new FormData()
			formData.append('file', file);
			var request = new XMLHttpRequest();
			request.open("POST", "/upload", true);
			request.onload = function (e) {
				
				// show message in UI
				
				console.log('uploaded');
				console.log(e);
				console.log(request.status);
				console.log(JSON.parse(request.response));
				
				nextJob();
			}
			request.send(formData);
		}
	});
	
	function nextJob () {
		var job = uploadJobs.pop();
		if (job) job();
	}
	
	nextJob();
});