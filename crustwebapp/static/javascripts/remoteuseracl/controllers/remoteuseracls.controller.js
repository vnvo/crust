(function (){
    'use strict';

    angular
        .module('crust.remoteuseracls.controllers')
        .controller('RemoteUserACLsController', RemoteUserACLsController);

    RemoteUserACLsController.$inject = [
        '$scope', 'RemoteUserACLs', 'Snackbar', 'ngDialog'
    ];

    function RemoteUserACLsController($scope, RemoteUserACLs, Snackbar, ngDialog){
        var vm = this;

        //getRuACLs();
        $scope.deleteRuACL = deleteRuACL;
        $scope.toggleRuACLActive = toggleRuACLActive;
        $scope.toggleRuACLAction = toggleRuACLAction;
        $scope.startRuACLUpdateDialog = startRuACLUpdateDialog;

        function startRuACLUpdateDialog(event, grid_row){
            $scope.update_ru_acl_id = grid_row.entity.id;
            ngDialog.open({
                template: '/static/templates/remoteuseracls/update_remoteuseracl.templ.html',
                controller: 'UpdateRemoteUserACLController as vm',
                scope: $scope
            });
            event.stopPropagation();
        }

        function deleteRuACL(event, grid_row){
            event.stopPropagation();
            if(!confirm('You are deleting a Remote User ACL, Are you sure?'))
                return;

            RemoteUserACLs.delete(grid_row.entity.id).then(
                delRuACLSuccess, delRuACLError
            );
            function delRuACLSuccess(data, status, headers, config){
                Snackbar.show('Remote User ACL deleted successfuly.');
                getRuACLs();
            }
            function delRuACLError(data, status, headers, config){
                Snackbar.error(
                    'Can not delete Remote User ACL',
                    {errors: data.data}
                );
            }
        }

        function toggleRuACLActive(event, grid_row){
            var ru_acl_info = grid_row.entity;
            ru_acl_info.is_active = !ru_acl_info.is_active;
            RemoteUserACLs.update(
                ru_acl_info.id,
                ru_acl_info
            ).then(toggleRuACLActiveSuccess, toggleRuACLActiveError);

            event.stopPropagation();

            function toggleRuACLActiveSuccess(data, status, header, config){
                Snackbar.show('Remote User ACL Active Status Changed Successfuly');
                console.log(data.data);
                getRuACLs();
            }
            function toggleRuACLActiveError(data, status, header, config){
                Snackbar.error('Can not update Remote User ACL.',
                               {errors: data.data});
                console.log(data);
            }
        }

        function toggleRuACLAction(event, grid_row){
            var ru_acl_info = grid_row.entity;
            ru_acl_info.acl_action = (ru_acl_info.acl_action=='allow' ? 'deny':'allow');
            RemoteUserACLs.update(
                ru_acl_info.id,
                ru_acl_info
            ).then(toggleRuACLActionSuccess, toggleRuACLActionError);
            event.stopPropagation();

            function toggleRuACLActionSuccess(data, status, header, config){
                Snackbar.show('Remote User ACL Action Status Changed Successfuly');
                console.log(data.data);
                getRuACLs();
            }
            function toggleRuACLActionError(data, status, header, config){
                Snackbar.error('Can not update Remote User ACL.',
                               {errors: data.data});
                console.log(data);
            }
        }

        // listen for creation/update events
        $scope.$on(
            'remoteuseracl.created',
            function(){ getRuACLs(); }
        );
        $scope.$on(
            'remoteuseracl.updated',
            function(){ getRuACLs(); }
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
            var pagedData = data.results;//.slice((page - 1) * pageSize, page * pageSize);
            $scope.remoteuseracls_data = pagedData;
            $scope.totalServerItems = data.count;
            if (!$scope.$$phase) {
                $scope.$apply();
            }
        };

        $scope.getPagedDataAsync = function (pageSize, page, searchText, ordering) {
            setTimeout(function () {
                var data;

                RemoteUserACLs.all(pageSize, page, searchText, ordering).then(
                    getAllRuACLsSuccess, getAllRuACLsError
                );
                function getAllRuACLsSuccess(data, status, headers, config){
                    //$scope.remoteuseracls_data = data.data;
                    $scope.setPagingData(data.data, page, pageSize);

                }
                function getAllRuACLsError(data, status, headers, config){
                    Snackbar.error('Can not get Remote User ACLs data.',
                                   {errors:data.data});
                }
            }, 100);
        };

        $scope.$watch('pagingOptions', function (newVal, oldVal) {
            if (newVal !== oldVal && (newVal.currentPage !== oldVal.currentPage
                                      || newVal.pageSize !== oldVal.pageSize)) {
                getRuACLs();
            }
        }, true);



        $scope.$watch('gridOptions.$gridScope.filterText', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                getRuACLs();
            }
        }, true);


        $scope.$watch('sortOptions', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                $scope.ordering = $scope.sortOptions.directions[0] === 'desc'? '-':'';
                $scope.ordering = $scope.ordering + $scope.sortOptions.fields[0].toLowerCase().replace('.', '__');
                getRuACLs();
            }
        }, true);


        $scope.gridOptions = {
            data: 'remoteuseracls_data',
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
                {field: 'remote_user.username', displayName: 'Remote User', width: 110},
                {field: 'server_group.group_name', displayName: 'Server Group', width: 120},
                {field: 'server.server_name', displayName: 'Server', width: 120},
                {field: 'server_account.server_account_repr', displayName: 'Server Account', width:200},
                {field: 'command_group.command_group_name', displayName: 'Command Group', width: 130},
                {field: 'is_active', displayName: 'Is Active', width: 69,
                 cellTemplate: '/static/templates/remoteuseracls/grid_cell.is_active.templ.html'
                },
                {field: 'acl_action', displayName: 'ACL Action', width: 88,
                 cellTemplate: '/static/templates/remoteuseracls/grid_cell.acl_action.templ.html'
                },
                {field: '', displayName: 'Actions', width:50,
                 cellTemplate: '/static/templates/remoteuseracls/grid_cell.actions.templ.html'
                }
            ],
            pagingOptions: $scope.pagingOptions,
            filterOptions: $scope.filterOptions
        };

        function getRuACLs(){
            $scope.getPagedDataAsync(
                $scope.pagingOptions.pageSize,
                $scope.pagingOptions.currentPage,
                $scope.gridOptions.$gridScope.filterText,
                $scope.ordering
            );
        }

    }

})();
