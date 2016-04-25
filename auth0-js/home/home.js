angular.module( 'sample.home', [
'auth0'
])
.controller( 'HomeCtrl', function HomeController( $scope, auth, $http, $location, store ) {

  $scope.auth = auth;

  $scope.callApi = function() {
    // Just call the API as you'd do using $http
    $http({
      url: 'https://endpoints-bookstore-node.appspot.com/shelves/1',
      method: 'GET'
    }).then(function(response) {
      alert('Response: ' + JSON.stringify(response.data));
    }, function(response) {
      if (response.status == -1) {
        alert('Failure: ' + response.statusText);
      }
      else {
        alert('Failure: ' + response.data);
      }
    });
  }

  $scope.logout = function() {
    auth.signout();
    store.remove('profile');
    store.remove('token');
    $location.path('/login');
  }

});
