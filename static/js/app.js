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

    var elAction = document.getElementById('action');
    var action = elAction.getAttribute('value');

    var elInput = document.getElementById('files');
    var files = Array.prototype.slice.call(elInput.files);
    var uploadJobs = files.map(function (file, index) {
      return function () {
        var formData = new FormData()
        formData.append('file', file);
        var request = new XMLHttpRequest();
        request.open("POST", action, true);
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
        $window.location.reload()
        vm.cancel();
      }
    }

    nextJob();
  };

  vm.cancel = function () {
    $modalInstance.dismiss('cancel');
  };
})

.controller('DeleteModalInstanceCtrl', function ($scope, $modalInstance, $timeout, $window) {
  var vm = this;

  vm.submit = function () {

    vm.deleting = true;

    var elAction = document.getElementById('action');
    var action = elAction.getAttribute('value');
    $window.location.href = action
  };

    vm.cancel = function () {
      $modalInstance.dismiss('cancel');
  };
})

.controller('TipModalInstanceCtrl', function ($modalInstance) {
  var vm = this;
  vm.cancel = function () {
    $modalInstance.dismiss('cancel');
  };
})

.controller('ResetModalInstanceCtrl', function ($scope, $modalInstance, $timeout, $window) {
  var vm = this;

  vm.submit = function () {

    vm.resetting = true;

    $timeout(function () {
        vm.resetting = true;
    });
    var elAction = document.getElementById('action');
    var action = elAction.getAttribute('value');
    var request = new XMLHttpRequest();
    request.open("GET", action, false);
    request.send();
      $window.location.reload()
  };

    vm.cancel = function () {
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


  vm.deleteModal = function () {
    var modalInstance = $modal.open({
      templateUrl: 'modal_delete.html',
      controller: 'DeleteModalInstanceCtrl',
      controllerAs: 'vm'
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
})


.controller('DatasetCtrl', function ($timeout, $modal) {
  var vm = this;
  vm.uploadCount = 0;

  vm.resetModal = function () {
    var modalInstance = $modal.open({
      templateUrl: 'modal_reset.html',
      controller: 'ResetModalInstanceCtrl',
      controllerAs: 'vm'
    });

    modalInstance.result.then(function () {

    }, function () {

    });
  };

  console.log("initing");

  vm.tipsModal = function () {
    console.log("showing")
    var modalInstance = $modal.open({
      templateUrl: 'modal_tips.html',
      controller: 'TipModalInstanceCtrl',
      controllerAs: 'vm'
    });
  };

  console.log("inited");


});
