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
                '/login',{
                    controller: 'LoginController',
                    controllerAs: 'vm',
                    templateUrl: '/static/templates/login.html'}
            ).when(
                '/dashboard',{
                    controller: 'DashboardController',
                    controllerAs: 'vm',
                    templateUrl: '/static/templates/dashboard.html'}
            ).when(
                '/servergroups',{
                    contoller: 'ServerGroupsController',
                    controllerAs: 'vm',
                    templateUrl: 'static/templates/servers/server_groups/servergroups.html'
                }
            ).otherwise('/');
    }
})();
