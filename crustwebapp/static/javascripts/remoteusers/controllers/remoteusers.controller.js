(function (){
    'use strict';

    angular
        .module('crust.remoteusers.controllers')
        .controller('RemoteUsersController', RemoteUsersController);

    RemoteUsersController.$inject = [
        '$scope', 'RemoteUsers', 'Snackbar', 'ngDialog'
    ];

    function RemoteUsersController($scope, RemoteUsers, Snackbar, ngDialog){
        var vm = this;

        //getRemoteUsers();
        $scope.deleteRemoteUser = deleteRemoteUser;
        $scope.startRUUpdateDialog = startRUUpdateDialog;
        $scope.toggleRUIsLocked = toggleRUIsLocked;

        /*function getRemoteUsers(){
            RemoteUsers.all().then(
                getAllRuSuccess, getAllRuError
            );
            function getAllRuSuccess(data, status, headers, config){
                $scope.remoteusers_data = data.data;
            }
            function getAllRuError(data, status, headers, config){
                Snackbar.error('Can not get Remote Users');
            }
        }*/

        function deleteRemoteUser(event, grid_row){
            event.stopPropagation();
            if(!confirm('You are deleting a Remote User, Are you sure?')){
                return;
            }

            RemoteUsers.delete(grid_row.entity.id).then(
                deleteRuSuccess, deleteRuError
            );
            function deleteRuSuccess(data, status, headers, config){
                Snackbar.show('Remote User Deleted Successfuly.');
                getRemoteUsers();
            }
            function deleteRuError(data, status, headers, config){
                Snackbar.error('Can no delete Remote User');
            }
        }

        function startRUUpdateDialog(event, grid_row){
            $scope.update_remoteuser_id = grid_row.entity.id;
            ngDialog.open({
                template: '/static/templates/remoteusers/update_remoteuser.templ.html',
                controller: 'UpdateRemoteUserController as vm',
                scope: $scope
            });
            event.stopPropagation();
        }

        function toggleRUIsLocked(event, grid_row){
            var ru_info = grid_row.entity;
            RemoteUsers.update(
                ru_info.id,
                {username:ru_info.username,
                 is_locked:!ru_info.is_locked}
            ).then(toggleRuLockSuccess, toggleRuLockError);

            event.stopPropagation();

            function toggleRuLockSuccess(data, status, header, config){
                Snackbar.show('Remote User Lock Changed Successfuly');
                console.log(data.data);
                getRemoteUsers();
            }
            function toggleRuLockError(data, status, header, config){
                Snackbar.error('Remote User Status Not Change');
                console.log(data);
            }
        }


        // listen for creation/update events
        $scope.$on(
            'remoteuser.created',
            function(){ getRemoteUsers(); }
        );
        $scope.$on(
            'remoteuser.updated',
            function(){ getRemoteUsers(); }
        );

        // Init/config ngGrid instance
        $scope.totalServerItems = 0;
        $scope.pagingOptions = {
            pageSizes: [5, 10, 20, 50],
            pageSize: 10,
            currentPage: 1
        };

        $scope.setPagingData = function(data, page, pageSize){
            var pagedData = data.results;
            $scope.remoteusers_data = pagedData;
            $scope.totalServerItems = data.count;
            if (!$scope.$$phase) {
                $scope.$apply();
            }
        };

        $scope.getPagedDataAsync = function (pageSize, page, searchText) {
            setTimeout(function () {
                var data;

                RemoteUsers.all(pageSize, page).then(
                    getAllRuSuccess, getAllRuError
                );
                function getAllRuSuccess(data, status, headers, config){
                    $scope.setPagingData(data.data, page, pageSize);
                }
                function getAllRuError(data, status, headers, config){
                    Snackbar.error('Can not get Remote Users data.',
                                   {errors:data.data});
                }
            }, 100);
        };

        $scope.$watch('pagingOptions', function (newVal, oldVal) {
            if (newVal !== oldVal && (newVal.currentPage !== oldVal.currentPage || newVal.pageSize !== oldVal.pageSize)) {
                $scope.getPagedDataAsync(
                    $scope.pagingOptions.pageSize,
                    $scope.pagingOptions.currentPage,
                    'test');
            }
        }, true);

        function getRemoteUsers(){
            $scope.getPagedDataAsync(
                $scope.pagingOptions.pageSize,
                $scope.pagingOptions.currentPage
            );
        }
        getRemoteUsers();

        $scope.gridOptions = {
            data: 'remoteusers_data',
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
                {field: 'email', displayName: 'Email', width: 160},
                {field: 'cell_phone', displayName: 'Cell Phone', width: 120},
                {field: 'is_locked', displayName: 'Is Locked', width: 80,
                 cellTemplate: '/static/templates/remoteusers/grid_cell.is_locked.templ.html'
                },
                {field: 'sshv2_public_key', displayName: 'SSHv2 Public Key', width: 220},
                {field: 'comment', displayName: 'Comment', width: 175},
                {field: '', displayName: 'Actions',
                 cellTemplate: '/static/templates/remoteusers/grid_cell.actions.templ.html'
                }
            ],
            plugins: [new ngGridCsvExportPlugin()],
            pagingOptions: $scope.pagingOptions
        };
    }
})();
