(function (){
    'use strict';

    angular
        .module('crust.supervisoracls.services')
        .factory('SupervisorACLs', SupervisorACLs);

    SupervisorACLs.$inject = ['$http'];

    function SupervisorACLs($http){
        var SupervisorACLs = {
            all: getAllSupACLs,
            getSuggestion: getSupACLSuggestion,
            get: getSupACL,
            create: createSupACL,
            update: updateSupACL,
            delete: delSupACL
        };

        return SupervisorACLs;

        function getAllSupACLs(pageSize, page){
            return $http.get('/api/v1/supervisoracls/',{
                params: {page_size:pageSize, page:page}
            });
        }

        function getSupACLSuggestion(hint){
            return $http.get(
                '/api/v1/supervisoracls/', {
                    params: {hint: hint}
                }
            );
        }

        function getSupACL(sup_acl_id){
            return $http.get('/api/v1/supervisoracls/'+sup_acl_id+'/');
        }

        function createSupACL(sup_acl_info){
            return $http.post(
                '/api/v1/supervisoracls/',
                sup_acl_info
            );
        }

        function updateSupACL(sup_acl_id, sup_acl_info){
            return $http.put(
                '/api/v1/supervisoracls/'+sup_acl_id+'/',
                sup_acl_info
            );
        }

        function delSupACL(sup_acl_id){
            return $http.delete(
                '/api/v1/supervisoracls/'+sup_acl_id+'/'
            );
        }
    }

})();
