(function (){
    'use strict';

    angular
        .module('crust.commandpatterns.controllers')
        .controller('NewCommandPatternController', NewCommandPatternController);

    NewCommandPatternController.$inject = [
        '$rootScope', '$scope', 'CommandGroups',
        'CommandPatterns', 'Snackbar'
    ];

    function NewCommandPatternController($rootScope, $scope,
                                         CommandGroups, CommandPatterns, Snackbar){
        var vm = this;

        vm.submit = submit;

        getCommandGroups();

        function getCommandGroups(){
            CommandGroups.all().then(
                getCGSuccess, getCGError
            );
            function getCGSuccess(data, status, headers, config){
                $scope.commandgroups_data = data.data;
            }
            function getCGError(data, status, headers, config){
                Snackbar.error('Can not get Command Groups data.');
            }
        }

        function submit(){
            CommandPatterns.create(
                {command_group: vm.command_group,
                 pattern: vm.pattern,
                 action: (vm.action==true ? 'allow':'deny')}
            ).then(createCPSuccess, createCPError);

            function createCPSuccess(data, status, headers, config){
                Snackbar.show('Command Pattern Created Successfuly.');
                $rootScope.$broadcast('commandpattern.created');
                $scope.closeThisDialog();
            }
            function createCPError(data, status, headers, config){
                Snackbar.error('Can not create Command Pattern, check input.');
            }
        }

    }
})();
