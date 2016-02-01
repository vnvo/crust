(function (){
    'use strict';

    angular
        .module('crust.crustsessions.controllers')
        .controller('CrustActiveSessionsController', CrustSessionsController);

    CrustSessionsController.$inject = [
        '$scope', '$interval', 'CrustSessions', 'Snackbar', 'ngDialog',
        '$timeout', 'Servers', 'ServerAccounts', 'RemoteUsers'
    ];

    function CrustSessionsController($scope, $interval, CrustSessions, Snackbar,
                                     ngDialog, $timeout,Servers, ServerAccounts,
                                     RemoteUsers){
        var vm = this;

        $scope.dateOptions = {};
        vm.start_from_open = false;
        vm.start_to_open = false;
        vm.toggleStartFrom = function(){
            $timeout(function(){
                vm.start_from_open = !vm.start_from_open;
            });
        };
        vm.toggleStartTo = function(){
            $timeout(function(){
                vm.start_to_open = !vm.start_to_open;
            });
        };

        vm.start_from = null;
        vm.start_to = null;
        vm.command = null;
        vm.remote_user = null;
        vm.server = null;
        vm.server_account = null;

        vm.getCrustSessions = getCrustSessions;
        vm.getRemoteUsersSuggestion = getRemoteUsersSuggestion;
        vm.getServersSuggestion = getServersSuggestion;
        vm.getServerAccountsSuggestion = getServerAccountsSuggestion;

        function getServersSuggestion($viewValue){
            return Servers.getSuggestion($viewValue).then(
                getServerSuggestionSuccess, getServerSuggestionError
            );
            function getServerSuggestionSuccess(data, status, headers, config){
                return data.data.results;
            }
            function getServerSuggestionError(data, status, headers, config){
                Snackbar.error('Can not get Servers data.');
            }
        }
        function getServerAccountsSuggestion($viewValue){
            return ServerAccounts.getSuggestion($viewValue).then(
                getSASuggestionSuccess, getSASuggestionError
            );
            function getSASuggestionSuccess(data, status, headers, config){
                return data.data.results;
            }
            function getSASuggestionError(data, status, headers, config){
                Snackbar.error('Can not get Server Accounts data');
            }
        }
        function getRemoteUsersSuggestion($viewValue){
            return RemoteUsers.getSuggestion($viewValue).then(
                getRUSuggestionSuccess, getRUSuggestionError
            );
            function getRUSuggestionSuccess(data, status, headers, config){
                return data.data.results;
            }
            function getRUSuggestionError(data, status, headers, config){
                Snackbar.error('Can not get Remote Users data.');
            }
        }

        vm.stopTimer = stopTimer;
        var timer = $interval(getCrustSessions, 7000);
        $scope.$on('$destroy', function(){
            vm.stopTimer();
        });

        //getRuACLs();
        $scope.killSession = function(event, grid_row){
            //alert('kill session called');
            event.stopPropagation();
            if(!confirm('You are killing an Active Session, Are you sure?'))
                return;

            CrustSessions.kill(grid_row.entity.id).then(
                killSuccess, killError
            );
            function killSuccess(data, status, headers, config){
                Snackbar.show('Session Killed Successfuly.');
                getCrustSessions();
            }
            function killError(data, status, headers, config){
                Snackbar.error(
                    'Can not Kill Active Session',
                    {errors: data.data}
                );
            }
        };

        function stopTimer(){
            if(angular.isDefined(timer)){
                $interval.cancel(timer);
                timer = undefined;
            }
        }

        // Init/config ngGrid instance

        $scope.totalServerItems = 0;
        $scope.pagingOptions = {
            pageSizes: [5, 10, 20, 50],
            pageSize: 10,
            currentPage: 1
        };

        $scope.filterText = null;
        $scope.filterOptions = {
            filterText: $scope.filterText,
            useExternalFilter: true
        };

        $scope.sortOptions = {
            fields: ['created_at'],
            directions: ['desc']
        };

        $scope.setPagingData = function(data, page, pageSize){
            var pagedData = data.results;//.slice((page - 1) * pageSize, page * pageSize);
            $scope.crustsessions_data = pagedData;
            $scope.totalServerItems = data.count;
            if (!$scope.$$phase) {
                $scope.$apply();
            }
        };

        $scope.getPagedDataAsync = function (pageSize, page, searchText, ordering) {
            setTimeout(function () {
                var data;

                CrustSessions.allActive(
                    pageSize, page, searchText, vm.start_from, vm.start_to,
                    vm.command, (vm.remote_user==null ? null:vm.remote_user['username']),
                    (vm.server_account==null ? null:vm.server_account['server_account_repr']),
                    (vm.server==null ? null:vm.server['server_name']),
                    ordering
                ).then(
                    getAllSessionsSuccess, getAllSessionsError
                );
                function getAllSessionsSuccess(data, status, headers, config){
                    $scope.setPagingData(data.data, page, pageSize);
                }
                function getAllSessionsError(data, status, headers, config){
                    Snackbar.error('Can not get Sessions data.',
                                   {errors:data.data});
                }
            }, 100);
        };

        $scope.$watch('pagingOptions', function (newVal, oldVal) {
            if (newVal !== oldVal && (newVal.currentPage !== oldVal.currentPage
                                      || newVal.pageSize !== oldVal.pageSize)) {
                getCrustSessions();
            }
        }, true);



        $scope.$watch('gridOptions.$gridScope.filterText', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                getCrustSessions();
            }
        }, true);


        $scope.$watch('sortOptions', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                $scope.ordering = $scope.sortOptions.directions[0] === 'desc'? '-':'';
                $scope.ordering = $scope.ordering + $scope.sortOptions.fields[0].toLowerCase().replace('.', '__');
                getCrustSessions();
            }
        }, true);


        $scope.gridOptions = {
            data: 'crustsessions_data',
            rowHeight: 35,
            enablePaging: true,
            showHeader: true,
            showFooter: true,
            showGroupPanel: true,
            showFilter: true,
            multiSelect: false,
            useExternalSorting: true,
            sortInfo: $scope.sortOptions,
            totalServerItems: "totalServerItems",
            columnDefs: [
                {displayName:'#', width: 30,
                 cellTemplate: '<div class="ngCellText" data-ng-class="col.colIndex()"><span>{{row.rowIndex + 1}}</span></div>'
                },
                //{field: 'session_id', displayName: 'Session ID', width: 35},
                {field: 'created_at', displayName: 'Start Time', width: 145},
                {field: 'remoteuser', displayName: 'Remote User', width: 100},
                {field: 'serveraccount', displayName: 'Server Account', width: 160},
                {field: 'server', displayName: 'Server', width: 160},
                {field: 'client_ip', displayName: 'Client IP', width: 120},
                {field: 'status', displayName: 'Status', width: 85,
                 cellTemplate: '/static/templates/crustsessions/grid_cell.status.templ.html'
                },
                //{field: 'terminated_at', displayName: 'Stop Time', width: 145},
                {field: 'termination_cause', displayName: 'Termination Cause', width: 120},
                {field: '', displayName: 'Actions', width:50,
                 cellTemplate: '/static/templates/crustsessions/grid_cell.actions.templ.html'
                }
            ],
            pagingOptions: $scope.pagingOptions,
            filterOptions: $scope.filterOptions
        };

        function getCrustSessions(){
            $scope.getPagedDataAsync(
                $scope.pagingOptions.pageSize,
                $scope.pagingOptions.currentPage,
                $scope.gridOptions.$gridScope.filterText,
                $scope.ordering
            );
        }
    }

})();
