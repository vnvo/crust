(function (){
    'use strict';

    angular
        .module('crust.commandgroups.controllers')
        .controller('CommandGroupsController', CommandGroupsController);

    CommandGroupsController.$inject = [
        '$scope', 'CommandGroups', 'Snackbar', 'ngDialog'
    ];

    function CommandGroupsController($scope, CommandGroups, Snackbar, ngDialog){
        var vm = this;

        $scope.deleteCommandGroup = deleteCommandGroup;
        $scope.startCGUpdateDialog = startCGUpdateDialog;

        function startCGUpdateDialog(event, grid_row){
            $scope.update_commandgroup_id = grid_row.entity.id;
            ngDialog.open({
                template: '/static/templates/commandgroups/update_commandgroup.templ.html',
                controller: 'UpdateCommandGroupController as vm',
                scope: $scope
            });
            event.stopPropagation();
        }

        function deleteCommandGroup(event, grid_row){
            event.stopPropagation();
            if(!confirm('You are deleting a command group, Are you sure?'))
                return false;


            CommandGroups.delete(grid_row.entity.id).then(
                delCGSuccess, delCGError
            );
            function delCGSuccess(data, status, headers, config){
                Snackbar.show('Command Group Deleted Successfuly.');
                getCommandGroups();
            }
            function delCGError(data, status, headers, config){
                Snackbar.error('Can not delete Command Group');
            }
        }


        // listen for creation/update events
        $scope.$on(
            'commandgroup.created',
            function(){ getCommandGroups(); }
        );
        $scope.$on(
            'commandgroup.updated',
            function(){ getCommandGroups(); }
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
            $scope.commandgroups_data = pagedData;
            $scope.totalServerItems = data.count;
            if (!$scope.$$phase) {
                $scope.$apply();
            }
        };

        $scope.getPagedDataAsync = function (pageSize, page, searchText, ordering) {
            setTimeout(function () {
                var data;

                CommandGroups.all(pageSize, page, searchText, ordering).then(
                    getAllCGSuccess, getAllCGError
                );
                function getAllCGSuccess(data, status, headers, config){
                    $scope.setPagingData(data.data, page, pageSize);
                }
                function getAllCGError(data, status, headers, config){
                    Snackbar.error('Can not get Command Groups data.',
                                   {errors:data.data});
                }
            }, 100);
        };

        $scope.$watch('pagingOptions', function (newVal, oldVal) {
            if (newVal !== oldVal && (newVal.currentPage !== oldVal.currentPage
                                      || newVal.pageSize !== oldVal.pageSize)) {
                getCommandGroups();
            }
        }, true);

        $scope.$watch('gridOptions.$gridScope.filterText', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                getCommandGroups();
            }
        }, true);


        $scope.$watch('sortOptions', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                $scope.ordering = $scope.sortOptions.directions[0] === 'desc'? '-':'';
                $scope.ordering = $scope.ordering + $scope.sortOptions.fields[0].toLowerCase().replace('.', '__');
                getCommandGroups();
            }
        }, true);


        $scope.gridOptions = {
            data: 'commandgroups_data',
            rowHeight: 35,
            enablePaging: true,
            showHeader: true,
            showFooter: true,
            showGroupPanel: true,
            showFilter: true,
            multiSelect: false,
            useExternalSorting: true,
            sortInfo: $scope.sortOptions,
            totalServerItems: "totalServeritems",
            columnDefs: [
                {displayName:'#', width: 30,
                 cellTemplate: '<div class="ngCellText" data-ng-class="col.colIndex()"><span>{{row.rowIndex + 1}}</span></div>'
                },
                {field: 'id', displayName: 'ID', width: 35},
                {field: 'command_group_name', displayName: 'Command Group Name', width: 170},
                {field: 'supervisor.username', displayName: 'Supervisor', width: 110},
                {field: 'default_action', displayName: 'Default Action', width: 120},
                {field: 'pattern_count', displayName: 'Patterns #', width: 90},
                {field: 'comment', displayName: 'Comment', width: 250},
                {field: '', displayName: 'Actions',
                 cellTemplate: '/static/templates/commandgroups/grid_cell.actions.templ.html'
                }
            ],
            pagingOptions: $scope.pagingOptions,
            filterOptions: $scope.filterOptions
        };

        function getCommandGroups(){
            $scope.getPagedDataAsync(
                $scope.pagingOptions.pageSize,
                $scope.pagingOptions.currentPage,
                $scope.gridOptions.$gridScope.filterText,
                $scope.ordering
            );
        };
    }
})();
