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
                '/supervisors',{
                    controller: 'SupervisorsController',
                    controllerAs: 'vm',
                    templateUrl: '/static/templates/supervisors.html'}
            ).when(
                '/servergroups',{
                    contoller: 'ServerGroupsController',
                    controllerAs: 'vm',
                    templateUrl: 'static/templates/servers/server_groups/servergroups.html'
                }
            ).when(
                '/servers',{
                    controller: 'ServersController',
                    controllerAs: 'vm',
                    templateUrl: '/static/templates/servers/servers/servers.html'
                }
            ).when(
                '/serveraccounts',{
                    controller: 'ServerAccountsController',
                    controllerAs: 'vm',
                    templateUrl: '/static/templates/servers/serveraccounts/serveraccounts.html'
                }
            ).when(
                '/remoteusers', {
                    controller: 'RemoteUsersController',
                    controllerAs: 'vm',
                    templateUrl: '/static/templates/remoteusers/remoteusers.html'
                }
            ).when(
                '/commandgroups', {
                    controller: 'CommandGroupsController',
                    controllerAs: 'vm',
                    templateUrl: '/static/templates/commandgroups/commandgroups.html'
                }
            ).otherwise('/dashboard');
    }
})();
