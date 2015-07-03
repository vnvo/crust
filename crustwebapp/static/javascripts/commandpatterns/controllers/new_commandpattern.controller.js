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
        vm.getCGSuggestion = getCGSuggestion;

        function getCGSuggestion($viewValue){
            return CommandGroups.getSuggestion($viewValue).then(
                getCGSuccess, getCGError
            );
            function getCGSuccess(data, status, headers, config){
                return data.data.results;
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
