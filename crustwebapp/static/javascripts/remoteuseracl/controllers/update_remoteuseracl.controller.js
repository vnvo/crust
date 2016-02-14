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

        vm.limit_days_data = {
            5:false, 6:false, 0:true,
            1:false, 2:false, 3:false, 4:false};
        vm.getRemoteUsersSuggestion = getRemoteUsersSuggestion;
        vm.getServerGroupsSuggestion = getServerGroupsSuggestion;
        vm.getServersSuggestion = getServersSuggestion;
        vm.getServerAccountsSuggestion = getServerAccountsSuggestion;
        vm.getCommandGroupsSuggestion = getCommandGroupsSuggestion;
        vm.update = update;
        getRuACLInfo();

        function prepLimitDays(){
            if(vm.limit_days==null)
                vm.limit_days = '';
            angular.forEach(
                vm.limit_days.split(','),
                function(val, index){
                    vm.limit_days_data[parseInt(val)] = true;
                }
            );
        }
        function getLimitDays(){
            var limit_days = [];
            angular.forEach(
                vm.limit_days_data,
                function(val, key){
                    if(val==true)
                        limit_days.push(key);
                });
            return limit_days.join(',');
        }

        function getRuACLInfo(){
            RemoteUserACLs.get($scope.update_ru_acl_id).then(
                getRuACLInfoSuccess, getRuACLInfoError
            );
            function getRuACLInfoSuccess(data, status, headers, config){
                var info = data.data;
                vm.remoteuseracl_id = info.id;
                vm.remote_user = info.remote_user;
                vm.limit_hours_start = (info.limit_hours_start==null?-1:info.limit_hours_start);
                vm.limit_hours_end = (info.limit_hours_end==null?-1:info.limit_hours_end);
                vm.limit_days = info.limit_days;
                prepLimitDays();

                if(info.server_group){
                    vm.server_group = info.server_group;
                    vm.match_type = 'servergroup';
                }
                else if(info.server){
                    vm.server = info.server;
                    vm.match_type = 'server';
                }
                else if(info.server_account){
                    vm.server_account = info.server_account;
                    vm.match_type = 'serveraccount';
                }

                vm.command_group = info.command_group;
                vm.is_active = info.is_active;
                vm.acl_action = info.acl_action;
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


        function update(){
            var update_acl_info = {
                limit_hours_start: vm.limit_hours_start,
                limit_hours_end: vm.limit_hours_end,
                limit_days: getLimitDays(),
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
