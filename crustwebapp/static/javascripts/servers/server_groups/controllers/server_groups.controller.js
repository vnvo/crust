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
        'ServerGroups', 'Snackbar'
    ];

    /**
     * @namespace ServerGroupsController
     */
    function ServerGroupsController($location, $scope,
                                    $routeParams, ServerGroups, Snackbar){
        var vm = this;

        ServerGroups.all().then(getAllSuccessFn, getAllErrorFn);
        function getAllSuccessFn(data, status, header, config){
            $scope.data = data.data;
            Snackbar.show('Success on geting data!');
        }

        function getAllErrorFn(data, status, header, config){
            Snackbar.error('There was an error fetching Server Groups');
        }

        $scope.gridOptions = {
            data: 'data',
            rowHeight: 30,
            enablePaging: true,
            useExternalSorting: true,
            showFooter: true,
            showHeader: true,
            columnDefs:[
                {field: 'id', displayName: 'ID', width:'40px'},
                {field: 'group_name', displayName: 'Server Group Name', width: '300px'},
                {field: 'server_set', displayName: 'Servers', width: 20}
            ],
            plugins: [new ngGridCsvExportPlugin()],
            pagingOptions: {
                // pageSizes: list of available page sizes.
                pageSizes: [10, 20, 50],
                //pageSize: currently selected page size.
                pageSize: 10,
                //totalServerItems: Total items are on the server.
                totalServerItems: 0,
                //currentPage: the uhm... current page.
                currentPage: 1
            }
        };
    }

})();
