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

        getServerAccounts();
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

        function getServerAccounts(){
            ServerAccounts.all().then(
                getAllSASuccess, getAllSAError
            );
            function getAllSASuccess(data, status, headers, config){
                $scope.serveraccounts_data = data.data;
            }
            function getAllSAError(data, status, headers, config){
                Snackbar.error('Can not get Server Accounts.');
            }
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
        $scope.gridOptions = {
            data: 'serveraccounts_data',
            rowHeight: 35,
            enablePaging: true,
            showHeader: true,
            showFooter: true,
            showGroupPanel: true,
            showFilter: true,
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
            plugins: [new ngGridCsvExportPlugin()],
            pagingOptions:{
                pageSizes: [5, 20, 50],
                pageSize: 5,
                currentPage: 1
            }
        };

    }
})();
