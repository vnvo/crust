(function (){
    'use strict';

    angular
        .module('crust.commandgroups.controllers')
        .controller('UpdateCommandGroupController', UpdateCommandGroupController);

    UpdateCommandGroupController.$inject = [
        '$rootScope', '$scope', 'CommandGroups', 'Snackbar'
    ];

    function UpdateCommandGroupController($rootScope, $scope, CommandGroups, Snackbar){
        var vm = this;

        vm.update = update;
        getCommandGroupInfo();

        function getCommandGroupInfo(){
            CommandGroups.get($scope.update_commandgroup_id).then(
                getCGInfoSuccess, getCGInfoError
            );
            function getCGInfoSuccess(data, status, headers, config){
                var cg_data = data.data;
                vm.commandgroup_id = cg_data.id;
                vm.command_group_name = cg_data.command_group_name;
                vm.default_action = (cg_data.default_action=='allow'? true:false);
                vm.comment = cg_data.comment;
            }
            function getCGInfoError(data, status, headers, config){
                Snackbar.error('Can not get Command Group Info');
            }
        }

        function update(){
            CommandGroups.update(
                vm.commandgroup_id,
                {command_group_name: vm.command_group_name,
                 default_action: (vm.default_action==true ? 'allow':'deny'),
                 comment: vm.comment}
            ).then(updateCGSuccess, updateCGError);

            function updateCGSuccess(data, status, headers ,config){
                Snackbar.show('Command Group Updated Successfuly.');
                $rootScope.$broadcast('commandgroup.updated');
                $scope.closeThisDialog();
            }
            function updateCGError(data, status, headers, config){
                Snackbar.error('Can not update Command Group, check input.');
            }
        }

    }

})();
