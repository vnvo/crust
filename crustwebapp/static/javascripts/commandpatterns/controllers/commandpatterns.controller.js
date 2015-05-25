(function (){
    'use strict';

    angular
        .module('crust.commandpatterns.controllers')
        .controller('CommandPatternsController', CommandPatternsController);

    CommandPatternsController.$inject = [
        '$scope', 'CommandPatterns', 'Snackbar', 'ngDialog'
    ];

    function CommandPatternsController($scope, CommandPatterns, Snackbar, ngDialog){
        var vm = this;

        getCommandPatterns();
        $scope.deleteCommandPattern = deleteCommandPattern;
        $scope.startCPUpdateDialog = startCPUpdateDialog;

        function startCPUpdateDialog(event, grid_row){
            $scope.update_commandpattern_id = grid_row.entity.id;
            ngDialog.open({
                template: '/static/templates/commandpatterns/update_commandpattern.templ.html',
                controller: 'UpdateCommandPatternController as vm',
                scope: $scope
            });
            event.stopPropagation();
        }

        function deleteCommandPattern(event, grid_row){
            event.stopPropagation();
            if(!confirm('You are deleting a Command Pattern, Are you sure?'))
               return;

            CommandPatterns.delete(grid_row.entity.id).then(
                delCPSuccess, delCPError
            );
            function delCPSuccess(data, status, headers, config){
                Snackbar.show('Command Pattern Deleted Successfuly.');
                getCommandPatterns();
            }
            function delCPError(data, status, headers, config){
                Snackbar.error('Can not delete Command Group');
            }
        }


        function getCommandPatterns(){
            CommandPatterns.all().then(
                getAllCPSuccess, getAllCPError
            );
            function getAllCPSuccess(data, status, headers, config){
                $scope.commandpatterns_data = data.data;
            }
            function getAllCPError(data, status, headers, config){
                Snackbar.error('Can not get Command Patterns data');
            }
        }

        // listen for creation/update events
        $scope.$on(
            'commandpattern.created',
            function(){ getCommandPatterns(); }
        );
        $scope.$on(
            'commandpattern.updated',
            function(){ getCommandPatterns(); }
        );

        // Init/config ngGrid instance
        $scope.gridOptions = {
            data: 'commandpatterns_data',
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
                {field: 'command_group.command_group_name',
                 displayName: 'Command Group Name', width: 190},
                {field: 'pattern', displayName: 'Pattern', width: 230},
                {field: 'action', displayName: 'Match Action', width: 120},
                {field: '', displayName: 'Actions',
                 cellTemplate: '/static/templates/commandpatterns/grid_cell.actions.templ.html'
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
