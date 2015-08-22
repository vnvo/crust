(function (){
    'use strict';

    angular
        .module('crust.commandgroups.controllers')
        .controller('NewCommandGroupController', NewCommandGroupController);

    NewCommandGroupController.$inject = [
        '$rootScope', '$scope', 'CommandGroups',
        'Supervisors', 'Authentication', 'Snackbar'
    ];

    function NewCommandGroupController($rootScope, $scope, CommandGroups, Supervisors, Authentication, Snackbar){
        var vm = this;

        vm.submit = submit;
        vm.getSupSuggestion = getSupSuggestion;

        if(Authentication.isAdmin()){
            Supervisors.all().then(
                function(data, status, headers, config){
                    $scope.supervisors = data.data.results;
                    vm.selected_supervisor = null;
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

        function submit(){
            CommandGroups.create(
                {command_group_name: vm.command_group_name,
                 default_action: (vm.default_action==true ? 'allow' : 'deny'),
                 comment: vm.comment, supervisor: vm.selected_supervisor}
            ).then(createCGSuccess, createCGError);

            function createCGSuccess(data, status, headers, config){
                Snackbar.show('Command Groups Created Successfuly.');
                $rootScope.$broadcast('commandgroup.created');
                $scope.closeThisDialog();
            }
            function createCGError(data, status, headers, config){
                Snackbar.error('Can not create Command Group, Check Input.');
            }
        }
    }

})();
