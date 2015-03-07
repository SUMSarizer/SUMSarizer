angular.module('myApp', [
	'ui.bootstrap'
])

.config(function($interpolateProvider){
 $interpolateProvider.startSymbol('{[{').endSymbol('}]}');
})

.controller('ModalInstanceCtrl', function ($scope, $modalInstance, $timeout, $window) {
	var vm = this;
	vm.submit = function () {
		
		vm.uploading = true;
		vm.complete = false;
		
		var elInput = document.getElementById('files');
		var files = Array.prototype.slice.call(elInput.files);
		var uploadJobs = files.map(function (file, index) {
			return function () {
				var formData = new FormData()
				formData.append('file', file);
				var request = new XMLHttpRequest();
				request.open("POST", "/upload", true);
				request.onload = function (e) {
								
					console.log('Uploaded');
					console.log(e);
					console.log(request.status);
					console.log(JSON.parse(request.response));
				
					nextJob();
				}
				request.send(formData);
			}
		});
	
		function nextJob () {
			
			$timeout(function () {
				vm.uploadCount = uploadJobs.length+1;
			});
						
			var job = uploadJobs.pop();
			if (job) {
				job();
			} else {
				vm.complete = true;
				vm.uploading = false;
			}
		}
	
		nextJob();
	};
	
  vm.cancel = function () {
		$window.location.reload();
    $modalInstance.dismiss('cancel');
  };
})

.controller('DashboardCtrl', function ($timeout, $modal) {
	var vm = this;
	vm.uploadCount = 0;
	
	vm.openModal = function () {
		var modalInstance = $modal.open({
			templateUrl: 'modal.html',
			controller: 'ModalInstanceCtrl',
			controllerAs: 'vm'
		});

		modalInstance.result.then(function () {

		}, function () {
			
		});
	};
	
})

.controller('NewStudyModalCtrl', function ($scope, $modalInstance, $timeout, $window) {
	var vm = this;
	vm.cancel = function () {
    $modalInstance.dismiss();
  };
})

.controller('StudyCtrl', function ($timeout, $modal) {
	var vm = this;
	vm.openModal = function () {
		var modalInstance = $modal.open({
			templateUrl: 'modal.html',
			controller: 'NewStudyModalCtrl',
			controllerAs: 'vm'
		});
	};
});

if (window.PLOTDATA) {
	$('#plot').highcharts({
	     chart: {
	         type: 'scatter',
	         zoomType: 'xy'
	     },
	     title: {
	         text: 'Stove temperature by time'
	     },
	     xAxis: {
	         title: {
	             enabled: true,
	             text: 'Time (s)'
	         },
	         startOnTick: true,
	         endOnTick: true,
	         showLastLabel: true
	     },
	     yAxis: {
	         title: {
	             text: 'Temp (C)'
	         }
	     },
	     plotOptions: {
	         scatter: {
	             marker: {
	                 radius: 5,
	                 states: {
	                     hover: {
	                         enabled: true,
	                         lineColor: 'rgb(100,100,100)'
	                     }
	                 }
	             },
	             states: {
	                 hover: {
	                     marker: {
	                         enabled: false
	                     }
	                 }
	             }
	         }
	     },
	     series: [{
	      color: 'rgba(223, 83, 83, .5)',
			 	data: PLOTDATA
	   	 }]
	 });

	
}

