/**
 * DashboardController
 * @namespace crust.dashboard.controllers
*/
(function(){
    'use strict';

    angular
        .module('crust.dashboard.controllers')
        .controller('DashboardController', DashboardController);

    DashboardController.$inject = [
        '$scope', '$interval', 'Snackbar',
        'ServerGroups', 'Servers', 'ServerAccounts',
        'RemoteUsers'
    ];

    /**
     * @namespace DashboardController
     */
    function DashboardController($scope, $interval, Snackbar,
                                 ServerGroups, Servers,
                                 ServerAccounts, RemoteUsers){
        var vm = this;

        vm.servergroup_count = 'n/a';
        vm.server_count = 'n/a';
        vm.serveraccount_count = 'n/a';
        vm.remoteuser_count = 'n/a';
        vm.active_remote_session_count = 'n/a';

        vm.getSystemStats = getSystemStats;
        vm.stopTimer = stopTimer;

        getSystemStats();
        var timer = $interval(getSystemStats, 120000);
        $scope.$on('$destroy', function() {
            // Make sure that the interval is destroyed too
            vm.stopTimer();
        });

        /**
         * @name stopTimer
         * @desc cancel the timer for fetching dashboard general data
         */
        function stopTimer(){
            if(angular.isDefined(timer)){
                $interval.cancel(timer);
                timer = undefined;
            }
        }

        /**
         * @name getSystemStats
         * @desc Get current system statistics and general states for dashboard
         * @memberof crust.dashboard.controllers.DashboardController
         */
        function getSystemStats(){
            Snackbar.show('Fetching System Status ... ');
            // Server Groups
            ServerGroups.getCount().then(getSGCountSuccess, getSGCountError);
            function getSGCountSuccess(data, header, status, config){
                vm.servergroup_count = data.data.servergroup_count;
            }
            function getSGCountError(data, header, status, config){
                Snackbar.error('Error while fetching Server Group Count');
                vm.servergroup_count = 'n/a';
            }

            // Servers
            Servers.count().then(
                getServerCountSuccess, getServerCountError);
            function getServerCountSuccess(data, status, headers, config){
                vm.server_count = data.data.server_count;
            }
            function getServerCountError(data, status, headers, config){
                Snackbar.error('Error getting Servers Count.');
                vm.server_count = 'n/a';
            }

            // Server Accounts
            ServerAccounts.count().then(
                getSACountSuccess, getSACountError
            );
            function getSACountSuccess(data, status, headers, config){
                vm.serveraccount_count = data.data.serveraccount_count;
            }
            function getSACountError(data, status, headers, config){
                Snackbar.error('Error getting Server Account count');
            }

            //Remote Users
            RemoteUsers.count().then(
                getRuCountSuccess, getRuCountError
            );
            function getRuCountSuccess(data, status ,headers, config){
                vm.remoteuser_count = data.data.remoteuser_count;
            }
            function getRuCountError(data, status, headers, config){
                Snackbar.error('Can not get Remote Users count.');
            }

            vm.active_remote_session_count = 7;
        }

    }

})();
