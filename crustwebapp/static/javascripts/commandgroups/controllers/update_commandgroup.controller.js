(function (){
    'use strict';

    angular
        .module('crust.commandgroups.controllers')
        .controller('UpdateCommandGroupController', UpdateCommandGroupController);

    UpdateCommandGroupController.$inject = [
        '$rootScope', '$scope', 'CommandGroups', 'Supervisors',
        'Authentication', 'Snackbar'
    ];

    function UpdateCommandGroupController($rootScope, $scope, CommandGroups, Supervisors, Authentication, Snackbar){
        var vm = this;

        vm.update = update;
        getCommandGroupInfo();

        vm.getSupSuggestion = getSupSuggestion;

        if(Authentication.isAdmin()){
            Supervisors.all().then(
                function(data, status, headers, config){
                    $scope.supervisors = data.data.results;
                    //vm.selected_supervisor = null;
                },
                function(data, status, headers, config){
                    $scope.supervisors = null;
                    vm.selected_supervisor = null;
                }
            );
        }

        function getSupSuggestion($viewValue){
            return Supervisors.getSuggestion($viewValue).then(
                getSupSuggestionSuccess, getSupSuggestionError
            );
            function getSupSuggestionSuccess(data, status, headers, config){
                return data.data.results;
            }
            function getSupSuggestionError(data, status, headers, config){
                Snackbar.error('Can not get Supervisors data.');
            }
        }

        function getCommandGroupInfo(){
            CommandGroups.get($scope.update_commandgroup_id).then(
                getCGInfoSuccess, getCGInfoError
            );
            function getCGInfoSuccess(data, status, headers, config){
                var cg_data = data.data;
                vm.commandgroup_id = cg_data.id;
                vm.command_group_name = cg_data.command_group_name;
                vm.selected_supervisor = cg_data.supervisor;
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
                 supervisor: vm.selected_supervisor,
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
