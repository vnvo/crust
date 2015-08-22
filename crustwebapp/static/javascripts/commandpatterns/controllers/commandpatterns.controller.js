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
            fields: ['pattern'],
            directions: ['asc']
        };

        $scope.setPagingData = function(data, page, pageSize){
            var pagedData = data.results;
            $scope.commandpatterns_data = pagedData;
            $scope.totalServerItems = data.count;
            if (!$scope.$$phase) {
                $scope.$apply();
            }
        };

        $scope.getPagedDataAsync = function (pageSize, page, searchText, ordering) {
            setTimeout(function () {
                var data;

                CommandPatterns.all(pageSize, page, searchText, ordering).then(
                    getAllCPSuccess, getAllCPError
                );
                function getAllCPSuccess(data, status, headers, config){
                    $scope.setPagingData(data.data, page, pageSize);
                }
                function getAllCPError(data, status, headers, config){
                    Snackbar.error('Can not get Command Patterns data.',
                                   {errors:data.data});
                }
            }, 100);
        };

        $scope.$watch('pagingOptions', function (newVal, oldVal) {
            if (newVal !== oldVal && (newVal.currentPage !== oldVal.currentPage
                                      || newVal.pageSize !== oldVal.pageSize)) {
                getCommandPatterns();
            }
        }, true);


        $scope.$watch('gridOptions.$gridScope.filterText', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                getCommandPatterns();
            }
        }, true);


        $scope.$watch('sortOptions', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                $scope.ordering = $scope.sortOptions.directions[0] === 'desc'? '-':'';
                $scope.ordering = $scope.ordering + $scope.sortOptions.fields[0].toLowerCase().replace('.', '__');
                getCommandPatterns();
            }
        }, true);


        $scope.gridOptions = {
            data: 'commandpatterns_data',
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
                {field: 'command_group.command_group_name',
                 displayName: 'Command Group Name', width: 190},
                {field: 'pattern', displayName: 'Pattern', width: 230},
                {field: 'action', displayName: 'Match Action', width: 120},
                {field: '', displayName: 'Actions',
                 cellTemplate: '/static/templates/commandpatterns/grid_cell.actions.templ.html'
                }
            ],
            pagingOptions: $scope.pagingOptions,
            filterOptions: $scope.filterOptions
        };

        function getCommandPatterns(){
            $scope.getPagedDataAsync(
                $scope.pagingOptions.pageSize,
                $scope.pagingOptions.currentPage,
                $scope.gridOptions.$gridScope.filterText,
                $scope.ordering
            );
        }
    }

})();
