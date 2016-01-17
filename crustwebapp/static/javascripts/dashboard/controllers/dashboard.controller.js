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
        'ServerGroups', 'Servers', 'CrustSessions',
        'ServerAccounts', 'RemoteUsers'
    ];

    /**
     * @namespace DashboardController
     */
    function DashboardController($scope, $interval, Snackbar,
                                 ServerGroups, Servers, CrustSessions,
                                 ServerAccounts, RemoteUsers){
        var vm = this;

        $scope.sg_server_counts = [];
        $scope.serverCountChartConfig = {
            options:{
                chart:{
                    type:'pie'
                },
                tooltip: {
                    style: {padding:10, fontWeight:'bold'}
                },
                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        dataLabels: {
                            enabled: true,
                            format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                        }
                    }
                }
            },
            title:{text:'Server Groups, Server Count'},
            series:[{
                colorByPoint: true,
                'name':'Server Count',
                'data':$scope.sg_server_counts

                //[ ['ali',4],['gholi',17] ]
            }]
        };


        vm.servergroup_count = 'n/a';
        vm.server_count = 'n/a';
        vm.serveraccount_count = 'n/a';
        vm.remoteuser_count = 'n/a';
        vm.active_remote_session_count = 'n/a';

        //only for fast chaning kpi
        vm.getFastSystemStats = getFastSystemStats;
        //only for slow changing kpi
        vm.getSystemStats = getNormalSystemStats;

        vm.stopTimers = stopTimers;

        getNormalSystemStats();
        getFastSystemStats();
        createServerGroupChart();
        vm.killSession = killSession;

        var timer = $interval(getNormalSystemStats, 120000);
        var fast_timer = $interval(getFastSystemStats, 10000);

        $scope.$on('$destroy', function(){
            // Make sure that the interval is destroyed too
            vm.stopTimers();
        });

        /**
         * @name stopTimers
         * @desc cancel the timer for fetching dashboard general data
         */
        function stopTimers(){
            if(angular.isDefined(timer)){
                $interval.cancel(timer);
                timer = undefined;
            }
            if(angular.isDefined(fast_timer)){
                $interval.cancel(fast_timer);
                fast_timer = undefined;
            }
        }


        function getFastSystemStats(){
            //Snackbar.show('Fetching System Status ... ');
            getActiveSessions();
        }


        function getActiveSessions(){
            // Active Sessions
            CrustSessions.allActive().then(
                getActiveCountSucccess, getActiveCountError
            );
            function getActiveCountSucccess(data, status, headers, config){
                vm.active_sessions = data.data.results;
                //console.log(vm.active_sessions);
            }
            function getActiveCountError(data, status, headers, config){
                Snackbar.error('Can not get Active Sessions Count.');
            }
        }

        /**
         * @name getSystemStats
         * @desc Get current system statistics and general states for dashboard
         * @memberof crust.dashboard.controllers.DashboardController
         */
        function getNormalSystemStats(){
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
        }

        function createServerGroupChart(){
            ServerGroups.getServerCount().then(
                getSGServerCountSuccess, getSGServerCountError
            );
            function getSGServerCountSuccess(data, status, headers, config){
                console.log(data.data.server_counts);
                $scope.serverCountChartConfig.series[0].data = data.data.server_counts;
                $scope.$broadcast('highchartsng.reflow');
            }

            function getSGServerCountError(data, status, headers, config){
                console.log(data);
            };

        }

        function killSession(id){
            if(!confirm('You are killing an Active Session, Are you sure?'))
                return;

            CrustSessions.kill(id).then(
                killSuccess, killError
            );
            function killSuccess(data, status, headers, config){
                Snackbar.show('Session Killed Successfuly.');
                getActiveSessions();
            }
            function killError(data, status, headers, config){
                Snackbar.error(
                    'Can not Kill Active Session',
                    {errors: data.data}
                );
            }

        }

    }

})();
