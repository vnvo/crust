(function (){
    'use strict';

    angular
        .module('crust.authentication.controllers')
        .controller('LoginController', LoginController);

    LoginController.$inject = ['$location', '$scope', 'Authentication'];

    /**
     * @namespace LoginController
     */
    function LoginController($location, $scope, Authentication){
        var vm = this;

        vm.login = login;

        activate();


        /**
         * @name activate
         * @desc actions to be performed upon instantiating the controller
         * @memberOf crust.authentication.controllers.LoginController
         */
        function activate(){
            if (Authentication.isAuthenticated()){
                $location.url('/');
            }
        }

        function login(){
            Authentication.login(vm.username, vm.password);
        }
    }

})();
