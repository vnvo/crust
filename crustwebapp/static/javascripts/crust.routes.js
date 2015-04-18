(function(){
    'use strict';

    angular
        .module('crust.routes')
        .config(config);

    config.$inject = ['$routeProvider'];

    /**
     * @name config
     * @desc Define Crust Web App routes
     */
    function config($routeProvider){
        $routeProvider
            .when(
                '/login',
                {controller: 'LoginController',
                 controllerAs: 'vm',
                 templateUrl: '/static/templates/login.html'
                }
            ).otherwise('/');
    }
})();
