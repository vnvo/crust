(function (){
    'use strict';

    angular
        .module('crust.remoteuseracls.controllers')
        .controller('NewRemoteUserACLController', NewRemoteUserACLController);

    NewRemoteUserACLController.$inject = [
        '$rootScope', '$scope', 'RemoteUserACLs',
        'Servers', 'ServerGroups', 'ServerAccounts',
        'RemoteUsers', 'CommandGroups', 'Snackbar'
    ];

    function NewRemoteUserACLController($rootScope, $scope, RemoteUserACLs,
                                        Servers, ServerGroups, ServerAccounts,
                                        RemoteUsers, CommandGroups, Snackbar){
        var vm = this;

        vm.match_type = 'server';
        vm.is_active = true;
        vm.acl_action = 'allow';

        vm.getRemoteUsersSuggestion = getRemoteUsersSuggestion;
        vm.getServerGroupsSuggestion = getServerGroupsSuggestion;
        vm.getServersSuggestion = getServersSuggestion;
        vm.getServerAccountsSuggestion = getServerAccountsSuggestion;
        vm.getCommandGroupsSuggestion = getCommandGroupsSuggestion;
        vm.submit = submit;

        function getServerGroupsSuggestion($viewValue){
            return ServerGroups.getSuggestion($viewValue).then(
                getSGSuggestionSuccess, getSGSuggestionError
            );
            function getSGSuggestionSuccess(data, status, headers, config){
                return data.data.results;
            }
            function getSGSuggestionError(data, status, headers, config){
                Snackbar.error('Can not get Server Groups data.');
            }
        }

        function getServersSuggestion($viewValue){
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

        function getServerAccountsSuggestion($viewValue){
            return ServerAccounts.getSuggestion($viewValue).then(
                getSASuggestionSuccess, getSASuggestionError
            );
            function getSASuggestionSuccess(data, status, headers, config){
                return data.data.results;
            }
            function getSASuggestionError(data, status, headers, config){
                Snackbar.error('Can not get Server Accounts data');
            }
        }

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

        function getCommandGroupsSuggestion($viewValue){
            return CommandGroups.getSuggestion($viewValue).then(
                getCGSuggestionSuccess, getCGSuggestionError
            );
            function getCGSuggestionSuccess(data, status, headers, config){
                return data.data.results;
            }
            function getCGSuggestionError(data, status, headers, config){
                Snackbar.error(
                    'Can not get Command Groups data.',
                    {errors: data.data}
                );
            }
        }


        function submit(){
            var new_acl_info = {
                remote_user: vm.remote_user,
                acl_action: vm.acl_action,
                is_active: vm.is_active,
                command_group: vm.command_group
            };
            switch(vm.match_type){
            case 'servergroup':
                new_acl_info.server_group = vm.server_group;
                break;
            case 'server':
                new_acl_info.server = vm.server;
                break;
            case 'serveraccount':
                new_acl_info.server_account = vm.server_account;
                break;
            default:
                Snackbar.error('Invalid Match By.');
                return;
            }

            RemoteUserACLs.create(new_acl_info).then(
                addRuACLSuccess, addRuACLError
            );
            function addRuACLSuccess(data, status, headers, config){
                $rootScope.$broadcast('remoteuseracl.created');
                $scope.closeThisDialog();
                Snackbar.show('Remote User ACL created successfuly.');
            }
            function addRuACLError(data, status, headers, config){
                Snackbar.error(
                    'Can not create new Remote User ACL',
                    {errors:data.data}
                );
            }
        }
    }

})();
