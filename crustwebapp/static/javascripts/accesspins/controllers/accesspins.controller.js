(function (){
    'use strict';

    angular
        .module('crust.accesspins.controllers')
        .controller('AccessPinsController', AccessPinsController);

    AccessPinsController.$inject = [
        '$scope', 'AccessPins', 'RemoteUsers', 'Servers',
        'ServerAccounts', 'Snackbar', 'ngDialog'
    ];

    function AccessPinsController($scope, AccessPins, RemoteUsers, Servers,
                                  ServerAccounts, Snackbar, ngDialog){
        var vm = this;

        vm.deleteAccessPin = deleteAccessPin;
        vm.startAPUpdateDialog = startAPUpdateDialog;

        function deleteAccessPin(event, grid_row){
        }

        function startAPUpdateDialog(event, grid_row){
        }


        // listen for creation/update events
        $scope.$on(
            'accesspin.created',
            function(){ getAccessPins(); }
        );
        $scope.$on(
            'accesspin.updated',
            function(){ getAccessPins(); }
        );

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
            fields: ['id'],
            directions: ['desc']
        };

        $scope.setPagingData = function(data, page, pageSize){
            var pagedData = data.results;
            $scope.remoteusers_data = pagedData;
            $scope.totalServerItems = data.count;
            if (!$scope.$$phase) {
                $scope.$apply();
            }
        };

        $scope.getPagedDataAsync = function (pageSize, page, searchText, ordering) {
            setTimeout(function () {
                var data;

                AccessPins.all(pageSize, page, searchText, ordering).then(
                    getAllAPSuccess, getAllAPError
                );
                function getAllAPSuccess(data, status, headers, config){
                    $scope.setPagingData(data.data, page, pageSize);
                }
                function getAllAPError(data, status, headers, config){
                    Snackbar.error('Can not get Access Pins data.',
                                   {errors:data.data});
                }
            }, 100);
        };

        $scope.$watch('pagingOptions', function (newVal, oldVal) {
            if (newVal !== oldVal && (newVal.currentPage !== oldVal.currentPage
                                      || newVal.pageSize !== oldVal.pageSize)) {
                getAccessPins();
            }
        }, true);

        $scope.$watch('gridOptions.$gridScope.filterText', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                getAccessPins();
            }
        }, true);


        $scope.$watch('sortOptions', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                $scope.ordering = $scope.sortOptions.directions[0] === 'desc'? '-':'';
                $scope.ordering = $scope.ordering + $scope.sortOptions.fields[0].toLowerCase().replace('.', '__');
                getAccessPins();
            }
        }, true);


        $scope.gridOptions = {
            data: 'accesspins_data',
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
                {field: 'id', displayName: 'ID', width: 35},
                {field: 'pin', displayName: 'PIN', width: 90},
                {field: 'supervisor_username', displayName: 'Supervisor', width: 110},
                {field: 'remote_user_username', displayName: 'Remote User', width: 110},
                {field: 'server_name', displayName: 'Server', width: 130},
                {field: 'server_account_username', displayName: 'Server Account', width: 120},
                {field: 'validation_mode', displayName: 'Validation', width: 90},
                {field: 'created_at', displayName: 'Created', width: 110},
                {field: 'first_used_at', displayName: 'First Use', width: 110},
                {field: 'comment', displayName: 'Comment', width: 175},
                {field: '', displayName: 'Actions',
                 cellTemplate: '/static/templates/accesspins/grid_cell.actions.templ.html'
                }
            ],
            pagingOptions: $scope.pagingOptions,
            filterOptions: $scope.filterOptions
        };

        function getAccessPins(){
            $scope.getPagedDataAsync(
                $scope.pagingOptions.pageSize,
                $scope.pagingOptions.currentPage,
                $scope.gridOptions.$gridScope.filterText,
                $scope.ordering
            );
        }


    }


})();
