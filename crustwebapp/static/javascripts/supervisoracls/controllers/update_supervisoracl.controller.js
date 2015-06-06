(function (){
    'use strict';

    angular
        .module('crust.supervisoracls.controllers')
        .controller('UpdateSupervisorACLController', UpdateSupervisorACLController);

    UpdateSupervisorACLController.$inject = [
        '$rootScope', '$scope', 'SupervisorACLs',
        'Servers', 'ServerGroups', 'Supervisors',
        'RemoteUsers', 'CommandGroups', 'Snackbar'
    ];

    function UpdateSupervisorACLController($rootScope, $scope, SupervisorACLs,
                                           Servers, ServerGroups, Supervisors,
                                           RemoteUsers, CommandGroups, Snackbar){
        var vm = this;

        vm.getRemoteUsersSuggestion = getRemoteUsersSuggestion;
        vm.getServerGroupsSuggestion = getServerGroupsSuggestion;
        vm.getServersSuggestion = getServersSuggestion;
        vm.getSupSuggestion = getSupSuggestion;
        vm.getCommandGroupsSuggestion = getCommandGroupsSuggestion;
        vm.update = update;
        getSupACLInfo();

        function getSupACLInfo(){
            SupervisorACLs.get($scope.update_sup_acl_id).then(
                getSupACLInfoSuccess, getSupACLInfoError
            );
            function getSupACLInfoSuccess(data, status, headers, config){
                vm.supervisoracl_id = data.data.id;
                vm.supervisor = data.data.supervisor;

                if(data.data.server_group){
                    vm.server_group = data.data.server_group;
                    vm.match_type = 'servergroup';
                }
                else if(data.data.server){
                    vm.server = data.data.server;
                    vm.match_type = 'server';
                }
                else if(data.data.remote_user){
                    vm.remote_user = data.data.remote_user;
                    vm.match_type = 'remoteuser';
                }
                else if(data.data.command_group){
                    vm.command_group = data.data.command_group;
                    vm.match_type = 'commandgroup';
                }

                vm.is_active = data.data.is_active;
                vm.acl_action = data.data.acl_action;
            }
            function getSupACLInfoError(data, status, headers, config){
                Snackbar.error(
                    'Can not get Supervisor ACL Info.',
                    {errors: data.data}
                );
            }
        }

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

        function getSupSuggestion($viewValue){
            return Supervisors.getSuggestion($viewValue).then(
                getSupSuggestionSuccess, getSupSuggestionError
            );
            function getSupSuggestionSuccess(data, status, headers, config){
                return data.data.results;
            }
            function getSupSuggestionError(data, status, headers, config){
                Snackbar.error('Can not get Supervisors data');
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


        function update(){
            var update_acl_info = {
                supervisor: vm.supervisor,
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
            case 'remoteuser':
                update_acl_info.remote_user = vm.remote_user;
                break;
            case 'commandgroup':
                update_acl_info.command_group = vm.command_group;
                break;
            default:
                Snackbar.error('Invalid Match By.');
                return;
            }

            SupervisorACLs.update(
                vm.supervisoracl_id, update_acl_info
            ).then(
                updateSupACLSuccess, updateSupACLError
            );

            function updateSupACLSuccess(data, status, headers, config){
                $rootScope.$broadcast('supervisoracl.updated');
                $scope.closeThisDialog();
                Snackbar.show('Supervisor ACL update successfuly');
            }
            function updateSupACLError(data, status, headers, config){
                Snackbar.error(
                    'Can not update Supervisor ACL.',
                    {errors: data.data}
                );
            }
        }
    }
})();
