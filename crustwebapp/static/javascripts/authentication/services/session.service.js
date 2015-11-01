(function (){
    'use strict';

    angular
        .module('crust.authentication.services')
        .factory('SessionInterceptor', SessionInterceptor);

    SessionInterceptor.$inject = ['$q', '$window', '$location', '$cookies'];


    function SessionInterceptor($q, $window, $location, $cookies){

        return {
            /* Revoke client authentication if 401/403 is received */
            responseError: function (rejection) {
                console.log('HEREEEEEEE .....');
                console.log(rejection);
                console.log(rejection.status in [401, 403]);
                //console.log("TokenInterceptor: responseError", $window.sessionStorage.token);
                if (rejection != null && (rejection.status ===401 || rejection.status === 403)) {
                    console.log('logging out by interceptor ...');
                    //Authentication.unauthenticate();
                    delete $cookies.authenticatedAccount;
                    delete $cookies.accountLoginTime;
                    $location.path("/login");
                }
                return $q.reject(rejection);
            }
        };
    }

})();
