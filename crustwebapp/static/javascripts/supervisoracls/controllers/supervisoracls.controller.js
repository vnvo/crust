(function (){
    'use strict';

    angular
        .module('crust.supervisoracls.controllers')
        .controller('SupervisorACLsController', SupervisorACLsController);

    SupervisorACLsController.$inject = [
        '$scope', 'SupervisorACLs', 'Snackbar', 'ngDialog'
    ];

    function SupervisorACLsController($scope, SupervisorACLs, Snackbar, ngDialog){
        var vm = this;

        //getSupACLs();
        $scope.deleteSupACL = deleteSupACL;
        $scope.toggleSupACLActive = toggleSupACLActive;
        $scope.toggleSupACLAction = toggleSupACLAction;
        $scope.startSupACLUpdateDialog = startSupACLUpdateDialog;

        function startSupACLUpdateDialog(event, grid_row){
            $scope.update_sup_acl_id = grid_row.entity.id;
            ngDialog.open({
                template: '/static/templates/supervisoracls/update_supervisoracl.templ.html',
                controller: 'UpdateSupervisorACLController as vm',
                scope: $scope
            });
            event.stopPropagation();
        }

        function deleteSupACL(event, grid_row){
            event.stopPropagation();
            if(!confirm('You are deleting a Supervisor ACL, Are you sure?'))
                return;

            SupervisorACLs.delete(grid_row.entity.id).then(
                delSupACLSuccess, delSupACLError
            );
            function delSupACLSuccess(data, status, headers, config){
                Snackbar.show('Supervisor ACL deleted successfuly.');
                getSupACLs();
            }
            function delSupACLError(data, status, headers, config){
                Snackbar.error(
                    'Can not delete Supervisor ACL',
                    {errors: data.data}
                );
            }
        }

        function toggleSupACLActive(event, grid_row){
            var sup_acl_info = grid_row.entity;
            sup_acl_info.is_active = !sup_acl_info.is_active;
            SupervisorACLs.update(
                sup_acl_info.id,
                sup_acl_info
            ).then(toggleSupACLActiveSuccess, toggleSupACLActiveError);

            event.stopPropagation();

            function toggleSupACLActiveSuccess(data, status, header, config){
                Snackbar.show('Supervisor ACL Active Status Changed Successfuly');
                console.log(data.data);
                getSupACLs();
            }
            function toggleSupACLActiveError(data, status, header, config){
                Snackbar.error('Can not update Supervisor ACL.',
                               {errors: data.data});
                console.log(data);
            }
        }

        function toggleSupACLAction(event, grid_row){
            var sup_acl_info = grid_row.entity;
            sup_acl_info.acl_action = (sup_acl_info.acl_action=='allow' ? 'deny':'allow');
            SupervisorACLs.update(
                sup_acl_info.id,
                sup_acl_info
            ).then(toggleSupACLActiveSuccess, toggleSupACLActiveError);

            event.stopPropagation();

            function toggleSupACLActiveSuccess(data, status, header, config){
                Snackbar.show('Supervisor ACL Active Status Changed Successfuly');
                console.log(data.data);
                getSupACLs();
            }
            function toggleSupACLActiveError(data, status, header, config){
                Snackbar.error('Can not update Supervisor ACL.',
                               {errors: data.data});
                console.log(data);
            }
        }

        /*function getSupACLs(){
            SupervisorACLs.all().then(
                getAllSupACLsSuccess, getAllSupACLsError
            );
            function getAllSupACLsSuccess(data, status, headers, config){
                $scope.supervisoracls_data = data.data;
            }
            function getAllSupACLsError(data, status, headers, config){
                Snackbar.error('Can not get Supervisor ACLs data.',
                               {errors:data.data});
            }
        }*/

        // listen for creation/update events
        $scope.$on(
            'supervisoracl.created',
            function(){ getSupACLs(); }
        );
        $scope.$on(
            'supervisoracl.updated',
            function(){ getSupACLs(); }
        );

        // Init/config ngGrid instance
        $scope.totalServerItems = 0;
        $scope.pagingOptions = {
            pageSizes: [5, 10, 20, 50],
            pageSize: 10,
            currentPage: 1
        };

        $scope.setPagingData = function(data, page, pageSize){
            var pagedData = data.results;//.slice((page - 1) * pageSize, page * pageSize);
            $scope.supervisoracls_data = pagedData;
            $scope.totalServerItems = data.count;
            if (!$scope.$$phase) {
                $scope.$apply();
            }
        };

        $scope.getPagedDataAsync = function (pageSize, page, searchText) {
            setTimeout(function () {
                var data;

                SupervisorACLs.all(pageSize, page).then(
                    getAllRuACLsSuccess, getAllRuACLsError
                );
                function getAllRuACLsSuccess(data, status, headers, config){
                    $scope.setPagingData(data.data, page, pageSize);
                }
                function getAllRuACLsError(data, status, headers, config){
                    Snackbar.error('Can not get Supervisor ACLs data.',
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

        function getSupACLs(){
            $scope.getPagedDataAsync(
                $scope.pagingOptions.pageSize,
                $scope.pagingOptions.currentPage
            );
        }

        getSupACLs();

        $scope.gridOptions = {
            data: 'supervisoracls_data',
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
                {field: 'supervisor.username', displayName: 'Supervisor', width: 110},
                {field: 'remote_user.username', displayName: 'Remote User', width: 110},
                {field: 'server_group.group_name', displayName: 'Server Group', width: 120},
                {field: 'server.server_name', displayName: 'Server', width: 120},
                {field: 'command_group.command_group_name', displayName: 'Command Group', width: 130},
                {field: 'is_active', displayName: 'Is Active', width: 69,
                 cellTemplate: '/static/templates/supervisoracls/grid_cell.is_active.templ.html'
                },
                {field: 'acl_action', displayName: 'ACL Action', width: 88,
                 cellTemplate: '/static/templates/supervisoracls/grid_cell.acl_action.templ.html'
                },
                {field: '', displayName: 'Actions', width:50,
                 cellTemplate: '/static/templates/supervisoracls/grid_cell.actions.templ.html'
                }
            ],
            plugins: [new ngGridCsvExportPlugin()],
            pagingOptions: $scope.pagingOptions
        };
    }
})();
