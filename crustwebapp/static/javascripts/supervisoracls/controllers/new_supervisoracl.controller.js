(function (){
    'use strict';

    angular
        .module('crust.supervisoracls.controllers')
        .controller('NewSupervisorACLController', NewSupervisorACLController);

    NewSupervisorACLController.$inject = [
        '$rootScope', '$scope', 'SupervisorACLs',
        'Servers', 'ServerGroups', 'Supervisors',
        'RemoteUsers', 'CommandGroups', 'Snackbar'
    ];

    function NewSupervisorACLController($rootScope, $scope, SupervisorACLs,
                                        Servers, ServerGroups, Supervisors,
                                        RemoteUsers, CommandGroups, Snackbar){
        var vm = this;

        vm.match_type = 'server';
        vm.is_active = true;
        vm.acl_action = 'allow';

        vm.getRemoteUsersSuggestion = getRemoteUsersSuggestion;
        vm.getServerGroupsSuggestion = getServerGroupsSuggestion;
        vm.getServersSuggestion = getServersSuggestion;
        vm.getSupervisorsSuggestion = getSupervisorsSuggestion;
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

        function getSupervisorsSuggestion($viewValue){
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
                supervisor: vm.supervisor,
                acl_action: vm.acl_action,
                is_active: vm.is_active
            };
            switch(vm.match_type){
            case 'servergroup':
                new_acl_info.server_group = vm.server_group;
                break;
            case 'server':
                new_acl_info.server = vm.server;
                break;
            case 'remoteuser':
                new_acl_info.remote_user = vm.remote_user;
                break;
            case 'commandgroup':
                new_acl_info.command_group = vm.command_group;
            default:
                Snackbar.error('Invalid Match By.');
                return;
            }
            SupervisorACLs.create(new_acl_info).then(
                addSupACLSuccess, addSupACLError
            );
            function addSupACLSuccess(data, status, headers, config){
                $rootScope.$broadcast('supervisoracl.created');
                $scope.closeThisDialog();
                Snackbar.show('Supervisor ACL created successfuly.');
            }
            function addSupACLError(data, status, headers, config){
                Snackbar.error(
                    'Can not create new Supervisor ACL',
                    {errors:data.data}
                );
            }
        }
    }
})();
