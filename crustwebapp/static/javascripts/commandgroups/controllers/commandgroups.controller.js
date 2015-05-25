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

        getCommandGroups();

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
            if(!confirm('You are deleting a command group, Are you sure?')){
                return false;
            }

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

        function getCommandGroups(){
            CommandGroups.all().then(
                getAllCGSuccess, getAllCGError
            );

            function getAllCGSuccess(data, status, headers, config){
                $scope.commandgroups_data = data.data;
            }
            function getAllCGError(data, status, headers, config){
                Snackbar.error('Can not get Command Groups Data.');
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
        $scope.gridOptions = {
            data: 'commandgroups_data',
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
                {field: 'command_group_name', displayName: 'Command Group Name', width: 170},
                {field: 'default_action', displayName: 'Default Action', width: 120},
                {field: 'pattern_count', displayName: 'Patterns #', width: 90},
                {field: 'comment', displayName: 'Comment', width: 250},
                {field: '', displayName: 'Actions',
                 cellTemplate: '/static/templates/commandgroups/grid_cell.actions.templ.html'
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
