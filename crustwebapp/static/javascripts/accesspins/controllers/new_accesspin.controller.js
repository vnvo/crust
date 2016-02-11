(function (){
    'use strict';

    angular
        .module('crust.accesspins.controllers')
        .controller('NewAccessPinController', NewAccessPinController);

    NewAccessPinController.$inject = [
        '$rootScope', '$scope', 'RemoteUsers',
        'Servers', 'ServerAccounts', 'Snackbar'
    ];

    function NewAccessPinController($rootScope, $scope, RemoteUsers,
                                    Servers, ServerAccounts, Snackbar){

        var vm = this;

        vm.validation_options = ['one-time','time after first use',
                                 'time after creation'];
        vm.validation_mode = 'one-time';
        vm.getRemoteUsersSuggestion = getRemoteUsersSuggestion;
        vm.remote_user = null;
        vm.getServerSuggestion = getServerSuggestion;
        vm.server = null;
        vm.getServerAccountsSuggestion = getServerAccountsSuggestion;
        vm.server_account = null;

        function getRemoteUsersSuggestion($viewValue){
            return RemoteUsers.getSuggestion($viewValue).then(
                getRUSuggestionSuccess, getRUSuggestionError
            );
            function getRUSuggestionSuccess(data, status, headers, config){
                return data.data.results;
            }
            function getRUSuggestionError(data, status, headers, config){
                Snackbar.error('Can not get Remote Users data.');
            }
        }

        function getServerAccountsSuggestion(){
            return ServerAccounts.getAllAccountsForServer(vm.server).then(
                getSASuccess, getSAError
            );
            function getSASuccess(data, status, headers, config){
                vm.available_accounts = data.data.results;
            }
            function getSAError(data, status, headers, config){
                Snackbar.error('Can not get Servers data.');
            }

        }

        function getServerSuggestion($viewValue){
            return Servers.getSuggestion($viewValue).then(
                getServerSuggestionSuccess, getServerSuggestionError
            );
            function getServerSuggestionSuccess(data, status, headers, config){
                return data.data.results;
            }
            function getServerSuggestionError(data, status, headers, config){
                Snackbar.error('Can not get Servers data.');
            }
        }

        function submit(){
            var new_pin_info = {
                remote_user:vm.remote_user, server:vm.server,
                server_account:vm.server_account, validation_mode:vm.validation_mode,
                exp_after_creation:vm.exp_after_creation_seconds,
                exp_after_first_login:vm.exp_after_first_login_seconds,
                exp_on_date:vm.exp_on_date, comment:vm.comment
            };
        }

    }


})();
