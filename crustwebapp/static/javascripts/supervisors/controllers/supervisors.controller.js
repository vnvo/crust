/**
* SupervisorController
* @namespace crust.supervisors.controllers
*/
(function (){
    'use strict';

    angular
        .module('crust.supervisors.controllers')
        .controller('SupervisorsController', SupervisorsController);

    SupervisorsController.$inject = [
        'Supervisors', '$scope', '$routeParams', 'Snackbar',
        'ngDialog'
    ];

    /**
     * @namespace crust.supervisors.controllers.SupervisorsController
     */
    function SupervisorsController(Supervisors, $scope, $routeParams, Snackbar, ngDialog){
        var vm = this;

        $scope.supervisors_data = [];
        $scope.toggleIsActive = toggleIsActive;
        $scope.deleteSupervisor = deleteSupervisor;
        $scope.startUpdateDialog = startUpdateDialog;

        /**
         * @name startUpdateDialog
         * @desc initiate a ng-dialog instance for showing update tempalte
         * @param {object} event, event fired from ng-grid
         * @param {object} grid_row, corresponding grid row to be edited
         * @memberOf crust.supervisors.controllers.SupervisorsController
         */
        function startUpdateDialog(event, grid_row){
            $scope.update_supervisor_id = grid_row.entity.id;
            ngDialog.open({
                template: '/static/templates/supervisors/update_supervisor.templ.html',
                controller: 'UpdateSupervisorController as vm',
                scope: $scope
            });

            event.stopPropagation();
        }

        /**
         * @name toggleIsActive
         * @desc toggle is_active for Supervisor
         * @param event {object} ngGrid Event fierd by ng-click
         * @param grid_row {object} corresponding ngGrid row with Supervisor info
         * @memberOf crust.supervisors.controllers.SupervisorsController
         */
        function toggleIsActive(event, grid_row){
            var sup_info = grid_row.entity;
            Supervisors.update(
                sup_info.id,
                {username:sup_info.username, is_active:!sup_info.is_active}
            ).then(toggleActiveSuccess, toggleActiveError);

            event.stopPropagation();

            function toggleActiveSuccess(data, status, header, config){
                Snackbar.show('Active status for Supervisor changed successfuly');
                console.log(data.data);
                //$scope.supervisors_data.splice(grid_row.rowIndex, 1, data.data);
                getSupervisors();
            }

            function toggleActiveError(data, status, header, config){
                Snackbar.error('Error: Active status not change');
                console.log(data);
            }
        }

        /**
         * @name deleteSupervisor
         * @desc delete the selected supervisor. stop event propagation
         * @param {object} event, emitted by nggrid
         * @param {object} grid_row, corresponding row in the grid
         * @memberOf crust.supervisors.controllers.SupervisorsController
         */
        function deleteSupervisor(event, grid_row){
            event.stopPropagation();
            if(!confirm('You are deleting a Supervisor, are you sure?')){
                return;
            }

            Supervisors.delete(
                grid_row.entity.id
            ).then(deleteSupSuccess, deleteSupError);

            function deleteSupSuccess(data, status, headers, config){
                Snackbar.show('Supervisor Deleted Successfuly.');
                getSupervisors();
            }

            function deleteSupError(data, status, headers, config){
                Snackbar.error('Error: can not delete Supervisor.');
            }
        }

        // listen for creation/update events
        $scope.$on('supervisor.created',
                   function(){ getSupervisors(); }
                  );
        $scope.$on('supervisor.updated',
                   function(){ getSupervisors(); }
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
            $scope.supervisors_data = pagedData;
            $scope.totalServerItems = data.count;
            if (!$scope.$$phase) {
                $scope.$apply();
            }
        };

        $scope.getPagedDataAsync = function (pageSize, page, searchText, ordering) {
            setTimeout(function () {
                var data;

                Supervisors.all(pageSize, page, searchText, ordering).then(
                    getAllSupSuccess, getAllSupError
                );
                function getAllSupSuccess(data, status, headers, config){
                    $scope.setPagingData(data.data, page, pageSize);
                }
                function getAllSupError(data, status, headers, config){
                    Snackbar.error('Can not get Supervisors data.',
                                   {errors:data.data});
                }
            }, 100);
        };

        $scope.$watch('pagingOptions', function (newVal, oldVal) {
            if (newVal !== oldVal && (newVal.currentPage !== oldVal.currentPage
                                      || newVal.pageSize !== oldVal.pageSize)) {
                getSupervisors();
            }
        }, true);


        $scope.$watch('gridOptions.$gridScope.filterText', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                getSupervisors();
            }
        }, true);


        $scope.$watch('sortOptions', function (newVal, oldVal) {
            if (newVal !== oldVal) {
                $scope.ordering = $scope.sortOptions.directions[0] === 'desc'? '-':'';
                $scope.ordering = $scope.ordering + $scope.sortOptions.fields[0].toLowerCase().replace('.', '__');
                getSupervisors();
            }
        }, true);

        $scope.gridOptions = {
            data: 'supervisors_data',
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
                {field: 'username', displayName: 'Username', width: 110},
                {field: 'email', displayName: 'Email', width: 200},
                {field: 'is_active', displayName: 'Is Active', width: 70,
                 cellTemplate: '/static/templates/supervisors/grid_cell.active.templ.html'
                },
                {field: 'is_admin', displayName: 'Is Admin', width: 70},
                {field: 'last_login', displayName: 'Last Login', width: 150},
                {field: '', displayName: 'Actions',
                 cellTemplate: '/static/templates/supervisors/grid_cell.actions.templ.html'
                }
            ],
            pagingOptions: $scope.pagingOptions,
            filterOptions: $scope.filterOptions
        };

        function getSupervisors(){
            $scope.getPagedDataAsync(
                $scope.pagingOptions.pageSize,
                $scope.pagingOptions.currentPage,
                $scope.gridOptions.$gridScope.filterText,
                $scope.ordering
            );
        };
    }
})();
