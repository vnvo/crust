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
        '$scope', '$interval', 'Snackbar', 'ServerGroups'
    ];

    /**
     * @namespace DashboardController
     */
    function DashboardController($scope, $interval, Snackbar, ServerGroups){
        var vm = this;

        vm.servergroup_count = 'n/a';
        vm.server_count = 'n/a';
        vm.remote_user_count = 'n/a';
        vm.active_remote_session_count = 'n/a';

        vm.getSystemStats = getSystemStats;
        vm.stopTimer = stopTimer;

        getSystemStats();
        var timer = $interval(getSystemStats, 60000);
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
            ServerGroups.getCount().then(getSGCountSuccess, getSGCountError);
            function getSGCountSuccess(data, header, status, config){
                vm.servergroup_count = data.data.servergroup_count;
            }
            function getSGCountError(data, header, status, config){
                Snackbar.error('Error while fetching Server Group Count');
                vm.servergroup_count = 'n/a';
            }

            //vm.servergroup_count = 15;
            vm.server_count = 48;
            vm.remote_user_count = 23;
            vm.active_remote_session_count = 7;
        }

    }

})();
