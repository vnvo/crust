/**
 * ServerGroupsController
 * @namespace crust.servers.server_groups.controllers
 */
(function (){
    'use strict';

    angular
        .module('crust.servers.server_groups.controllers')
        .controller('ServerGroupsController', ServerGroupsController);

    ServerGroupsController.$inject = [
        '$location', '$scope', '$routeParams',
        'ServerGroups', 'Snackbar', 'ngDialog'
    ];

    /**
     * @namespace ServerGroupsController
     */
    function ServerGroupsController($location, $scope, $routeParams, ServerGroups, Snackbar, ngDialog){
        var vm = this;

        $scope.deleteServerGroup = deleteServerGroup;
        $scope.startSGUpdateDialog = startSGUpdateDialog;

        function startSGUpdateDialog(event, grid_row){
            $scope.update_sg_id = grid_row.entity.id;
            ngDialog.open({
                template: '/static/templates/servers/server_groups/update_servergroup.templ.html',
                controller: 'UpdateServerGroupController as vm',
                scope: $scope
            });
            event.stopPropagation();
        }

        function deleteServerGroup(event, grid_row){
            event.stopPropagation();
            if(!confirm(
                'Warning:You are deleting a Server Group with all Child Objects, Are You Sure?')
              ){
                  return;
            }

            ServerGroups.delete(
                grid_row.entity.id
            ).then(deleteSGSuccess, deleteSGError);

            function deleteSGSuccess(data, status, headers, config){
                Snackbar.show('Server Group Deleted Successfuly.');
                getServerGroups();
            }
            function deleteSGError(data, status, headers, config){
                Snackbar.error('Could not delete the Server Group.');
            }
        }

        // listen for creation/update events
        $scope.$on(
            'servergroup.created',
            function(){ getServerGroups(); }
        );
        $scope.$on(
            'servergroup.updated',
            function(){ getServerGroups(); }
        );

        // Init/config ngGrid instance
        $scope.totalServerItems = 0;
        $scope.pagingOptions = {
            pageSizes: [5, 10, 20, 50],
            pageSize: 10,
            currentPage: 1,
            totalServerItems: 7
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
            $scope.servergroups_data = pagedData;
            $scope.totalServerItems = data.count;
            if (!$scope.$$phase) {
                $scope.$apply();
            }
        };

        $scope.getPagedDataAsync = function (pageSize, page, searchText, ordering) {
            setTimeout(function () {
                var data;

                ServerGroups.all(pageSize, page, searchText, ordering).then(
                    getAllSGSuccess, getAllSGError
                );
                function getAllSGSuccess(data, status, headers, config){
                    $scope.setPagingData(data.data, page, pageSize);
                }
                function getAllSGError(data, status, headers, config){
                    Snackbar.error('Can not get Servers data.',
                                   {errors:data.data});
                }
            }, 100);
        };

        $scope.$watch('pagingOptions', function (newVal, oldVal) {
            if (newVal !== oldVal && (newVal.currentPage !== oldVal.currentPage
                                      || newVal.pageSize !== oldVal.pageSize)) {
                getServerGroups();
            }
        }, true);

        $scope.$watch('gridOptions.$gridScope.filterText', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                getServerGroups();
            }
        }, true);


        $scope.$watch('sortOptions', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                console.log($scope.sortOptions.fields);
                console.log($scope.sortOptions.directions);
                $scope.ordering = $scope.sortOptions.directions[0] === 'desc'? '-':'';
                $scope.ordering = $scope.ordering + $scope.sortOptions.fields[0].toLowerCase().replace('.', '__');

                getServerGroups();
            }
        }, true);


        //getServerGroups();
        $scope.gridOptions = {
            data: 'servergroups_data',
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
            columnDefs:[
                {displayName:'#', width: 30,
                 cellTemplate: '<div class="ngCellText" data-ng-class="col.colIndex()"><span>{{row.rowIndex + 1}}</span></div>'
                },
                {field: 'id', displayName: 'ID', width:'40px'},
                {field: 'group_name', displayName: 'Server Group Name', width: '250px'},
                {field: 'supervisor.username', displayName: 'Supervisor', width: 120},
                {field: 'server_count', displayName: 'Servers', width: 80},
                {field: 'serveraccount_count', displayName: 'Server Accounts', width: 125},
                {field: '', displayName: 'Actions',
                 cellTemplate: '/static/templates/servers/server_groups/grid_cell.actions.templ.html'
                }
            ],
            //plugins: [new ngGridCsvExportPlugin()],
            pagingOptions: $scope.pagingOptions,
            filterOptions: $scope.filterOptions
        };

        function getServerGroups(){
            $scope.getPagedDataAsync(
                $scope.pagingOptions.pageSize,
                $scope.pagingOptions.currentPage,
                $scope.gridOptions.$gridScope.filterText,
                $scope.ordering
            );
        };

        //getServerGroups();
    }

})();
