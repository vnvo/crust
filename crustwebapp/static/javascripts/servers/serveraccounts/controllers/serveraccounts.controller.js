/*
 * @namespace ServerAccountsController
 */
(function (){
    'use strict';

    angular
        .module('crust.servers.serveraccounts')
        .controller('ServerAccountsController', ServerAccountsController);

    ServerAccountsController.$inject = [
        '$scope', 'ServerAccounts', 'Snackbar', 'ngDialog'
    ];

    function ServerAccountsController($scope, ServerAccounts, Snackbar, ngDialog){
        var vm = this;

        //getServerAccounts();
        $scope.deleteServerAccount = deleteServerAccount;
        $scope.startSAUpdateDialog = startSAUpdateDialog;
        $scope.toggleIsLocked = toggleIsLocked;

        function toggleIsLocked(event, grid_row){
            var sa_info = grid_row.entity;
            ServerAccounts.update(
                sa_info.id,
                {username:sa_info.username,
                 server: sa_info.server,
                 protocol: sa_info.protocol,
                 is_locked:!sa_info.is_locked}
            ).then(toggleLockSuccess, toggleLockError);

            event.stopPropagation();

            function toggleLockSuccess(data, status, header, config){
                Snackbar.show('Server Account Lock Changed Successfuly');
                console.log(data.data);
                getServerAccounts();
            }
            function toggleLockError(data, status, header, config){
                Snackbar.error('Server Account Status Not Change');
                console.log(data);
            }
        }

        function deleteServerAccount(event, grid_row){
            event.stopPropagation();
            if(!confirm('You are deleting a Server Account, are you sure?')){
                return;
            }

            ServerAccounts.delete(
                grid_row.entity.id
            ).then(deleteSASuccess, deleteSAError);

            function deleteSASuccess(data, status, headers, config){
                Snackbar.show('Server Account Deleted Successfuly.');
                getServerAccounts();
            }
            function deleteSAError(data, status, headers, config){
                Snackbar.error('Could not delete the Server Account.');
            }
        }

        function startSAUpdateDialog(event, grid_row){
            $scope.update_serveraccount_id = grid_row.entity.id;
            ngDialog.open({
                template: '/static/templates/servers/serveraccounts/update_serveraccount.templ.html',
                controller: 'UpdateServerAccountController as vm',
                scope: $scope
            });
            event.stopPropagation();
        }

        // listen for creation/update events
        $scope.$on(
            'serveraccount.created',
            function(){ getServerAccounts(); }
        );
        $scope.$on(
            'serveraccount.updated',
            function(){ getServerAccounts(); }
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
            $scope.serveraccounts_data = pagedData;
            $scope.totalServerItems = data.count;
            if (!$scope.$$phase) {
                $scope.$apply();
            }
        };

        $scope.getPagedDataAsync = function (pageSize, page, searchText, ordering) {
            setTimeout(function () {
                var data;

                ServerAccounts.all(pageSize, page, searchText, ordering).then(
                    getAllSASuccess, getAllSAError
                );
                function getAllSASuccess(data, status, headers, config){
                    $scope.setPagingData(data.data, page, pageSize);
                }
                function getAllSAError(data, status, headers, config){
                    Snackbar.error('Can not get Server Accounts data..',
                                   {errors:data.data});
                }
            }, 100);
        };

        $scope.$watch('pagingOptions', function (newVal, oldVal) {
            if (newVal !== oldVal && (newVal.currentPage !== oldVal.currentPage
                                      || newVal.pageSize !== oldVal.pageSize)) {
                getServerAccounts();
            }
        }, true);

        $scope.$watch('gridOptions.$gridScope.filterText', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                getServerAccounts();
            }
        }, true);


        $scope.$watch('sortOptions', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                $scope.ordering = $scope.sortOptions.directions[0] === 'desc'? '-':'';
                $scope.ordering = $scope.ordering + $scope.sortOptions.fields[0].toLowerCase().replace('.', '__');
                getServerAccounts();
            }
        }, true);

        $scope.gridOptions = {
            data: 'serveraccounts_data',
            rowHeight: 35,
            enablePaging: true,
            showHeader: true,
            showFooter: true,
            showGroupPanel: true,
            showFilter: true,
            multiSelect: true,
            useExternalSorting: true,
            sortInfo: $scope.sortOptions,
            totalServerItems: "totalServerItems",
            columnDefs: [
                {displayName:'#', width: 30,
                 cellTemplate: '<div class="ngCellText" data-ng-class="col.colIndex()"><span>{{row.rowIndex + 1}}</span></div>'
                },
                {field: 'id', displayName: 'ID', width: 35},
                {field: 'username', displayName: 'Username', width: 100},
                {field: 'protocol', displayName: 'Protocol', width: 100},
                {field: 'server.server_name', displayName: 'Server', width: 150},
                {field: 'sshv2_private_key', displayName: 'SSHv2 P-Key', width: 250},
                {field: 'is_locked', displayName: 'Is Locked', width: 80,
                 cellTemplate: '/static/templates/servers/serveraccounts/grid_cell.is_locked.templ.html'
                },
                {field: 'comment', displayName: 'Comment', width: 175},
                {field: '', displayName: 'Actions',
                 cellTemplate: '/static/templates/servers/serveraccounts/grid_cell.actions.templ.html'
                }
            ],
            pagingOptions: $scope.pagingOptions,
            filterOptions: $scope.filterOptions
        };

        function getServerAccounts(){
            $scope.getPagedDataAsync(
                $scope.pagingOptions.pageSize,
                $scope.pagingOptions.currentPage,
                $scope.gridOptions.$gridScope.filterText,
                $scope.ordering
            );
        }
    }
})();
