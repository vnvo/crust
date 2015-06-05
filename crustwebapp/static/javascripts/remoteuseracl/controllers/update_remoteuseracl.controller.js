(function (){
    'use strict';

    angular
        .module('crust.remoteuseracls.controllers')
        .controller('UpdateRemoteUserACLController', UpdateRemoteUserACLController);

    UpdateRemoteUserACLController.$inject = [
        '$rootScope', '$scope', 'RemoteUserACLs',
        'Servers', 'ServerGroups', 'ServerAccounts',
        'RemoteUsers', 'CommandGroups', 'Snackbar'
    ];

    function UpdateRemoteUserACLController($rootScope, $scope, RemoteUserACLs,
                                           Servers, ServerGroups, ServerAccounts,
                                           RemoteUsers, CommandGroups, Snackbar){
        var vm = this;

        vm.getRemoteUsersSuggestion = getRemoteUsersSuggestion;
        vm.getServerGroupsSuggestion = getServerGroupsSuggestion;
        vm.getServersSuggestion = getServersSuggestion;
        vm.getServerAccountsSuggestion = getServerAccountsSuggestion;
        vm.getCommandGroupsSuggestion = getCommandGroupsSuggestion;
        vm.update = update;
        getRuACLInfo();

        function getRuACLInfo(){
            RemoteUserACLs.get($scope.update_ru_acl_id).then(
                getRuACLInfoSuccess, getRuACLInfoError
            );
            function getRuACLInfoSuccess(data, status, headers, config){
                vm.remoteuseracl_id = data.data.id;
                vm.remote_user = data.data.remote_user;

                if(data.data.server_group){
                    vm.server_group = data.data.server_group;
                    vm.match_type = 'servergroup';
                }
                else if(data.data.server){
                    vm.server = data.data.server;
                    vm.match_type = 'server';
                }
                else if(data.data.server_account){
                    vm.server_account = data.data.server_account;
                    vm.match_type = 'serveraccount';
                }

                vm.command_group = data.data.command_group;
                vm.is_active = data.data.is_active;
                vm.acl_action = data.data.acl_action;
            }
            function getRuACLInfoError(data, status, headers, config){
                Snackbar.error(
                    'Can not get Remote User ACL Info.',
                    {errors: data.data}
                );
            }
        }

        function getServerGroupsSuggestion($viewValue){
            return ServerGroups.getSuggestion($viewValue).then(
                getSGSuggestionSuccess, getSGSuggestionError
            );
            function getSGSuggestionSuccess(data, status, headers, config){
                return data.data;
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
                return data.data;
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
                return data.data;
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
                return data.data;
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
                return data.data;
            }
            function getCGSuggestionError(data, status, headers, config){
                Snackbar.error(
                    'Can not get Command Groups data.',
                    {errors: data.data}
                );
            }
        }


        function update(){
            var update_acl_info = {
                remote_user: vm.remote_user,
                command_group: vm.command_group,
                acl_action: vm.acl_action,
                is_active: vm.is_active
            };

            switch(vm.match_type){
            case 'servergroup':
                update_acl_info.server_group = vm.server_group;
                break;
            case 'server':
                update_acl_info.server = vm.server;
                break;
            case 'serveraccount':
                update_acl_info.server_account = vm.server_account;
                break;
            default:
                Snackbar.error('Invalid Match By.');
                return;
            }

            RemoteUserACLs.update(
                vm.remoteuseracl_id, update_acl_info
            ).then(
                updateRuACLSuccess, updateRuACLError
            );

            function updateRuACLSuccess(data, status, headers, config){
                $rootScope.$broadcast('remoteuseracl.updated');
                $scope.closeThisDialog();
                Snackbar.show('Remote User ACL update successfuly');
            }
            function updateRuACLError(data, status, headers, config){
                Snackbar.error(
                    'Can not update Remote User ACL.',
                    {errors: data.data}
                );
            }

        }
    }
})();
