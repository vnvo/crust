(function (){
    'use strict';

    angular
        .module('crust.commandpatterns.controllers')
        .controller('UpdateCommandPatternController', UpdateCommandPatternController);

    UpdateCommandPatternController.$inject = [
        '$rootScope', '$scope', 'CommandGroups',
        'CommandPatterns', 'Snackbar'
    ];

    function UpdateCommandPatternController($rootScope, $scope, CommandGroups,
                                            CommandPatterns, Snackbar){
        var vm = this;

        vm.update = update;

        getCommandGroups();
        getCommandPattern();

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

        function getCommandPattern(){
            CommandPatterns.get($scope.update_commandpattern_id).then(
                getCPSuccess, getCPError
            );
            function getCPSuccess(data, status, headers, config){
                var cp_data = data.data;
                vm.commandpattern_id = cp_data.id;
                vm.command_group = cp_data.command_group;
                vm.pattern = cp_data.pattern;
                vm.action = (cp_data.action=='allow' ? true:false);
            }
            function getCPError(data, status, headers, config){
                Snackbar.error('Can not get Command Pattern Info.');
            }
        }

        function update(){
            CommandPatterns.update(
                vm.commandpattern_id,
                {command_group: vm.command_group,
                 pattern: vm.pattern,
                 action: (vm.action==true ? 'allow':'deny')}
            ).then(updateCPSuccess, updateCPError);

            function updateCPSuccess(data, status, headers, config){
                Snackbar.show('Command Pattern Updated Successfuly.');
                $rootScope.$broadcast('commandpattern.updated');
                $scope.closeThisDialog();
            }
            function updateCPError(data, status, headers, config){
                Snackbar.error('Can not update Command Pattern, check Input');
            }
        }
    }

})();
