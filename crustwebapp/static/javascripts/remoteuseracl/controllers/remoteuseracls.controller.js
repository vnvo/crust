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

        getRuACLs();
        $scope.deleteRuACL = deleteRuACL;
        $scope.toggleRuACLActive = toggleRuACLActive;
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

        }

        function getRuACLs(){
            RemoteUserACLs.all().then(
                getAllRuACLsSuccess, getAllRuACLsError
            );
            function getAllRuACLsSuccess(data, status, headers, config){
                $scope.remoteuseracls_data = data.data;
            }
            function getAllRuACLsError(data, status, headers, config){
                Snackbar.error('Can not get Remote User ACLs data.',
                               {errors:data.data});
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
        $scope.gridOptions = {
            data: 'remoteuseracls_data',
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
                {field: 'remote_user.username', displayName: 'Remote User', width: 110},
                {field: 'server_group.group_name', displayName: 'Server Group', width: 120},
                {field: 'server.server_name', displayName: 'Server', width: 120},
                {field: 'server_account.server_account_repr', displayName: 'Server Account', width:200},
                {field: 'command_group.command_group_name', displayName: 'Command Group', width: 130},
                {field: 'is_active', displayName: 'Is Active', width: 69},
                {field: 'acl_action', displayName: 'ACL Action', width: 88},
                {field: '', displayName: 'Actions', width:50,
                 cellTemplate: '/static/templates/remoteuseracls/grid_cell.actions.templ.html'
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
