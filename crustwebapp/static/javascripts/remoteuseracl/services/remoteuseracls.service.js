(function (){
    'use strict';

    angular
        .module('crust.remoteuseracls.services')
        .factory('RemoteUserACLs', RemoteUserACLs);

    RemoteUserACLs.$inject = ['$http'];

    function RemoteUserACLs($http){
        var RemoteUserACLs = {
            all: getAllRuACLs,
            get: getRuACL,
            count: getRuACLsCount,
            create: createRuACL,
            update: updateRuACL,
            delete: deleteRuACL
        };

        return RemoteUserACLs;


        function getAllRuACLs(){
            return $http.get('/api/v1/remoteuseracls/');
        }

        function getRuACL(ru_acl_id){
            return $http.get('/api/v1/remoteuseracls/'+ru_acl_id+'/');
        }

        function getRuACLsCount(){
            return $http.get('/api/v1/remoteuseracls/count/');
        }

        function createRuACL(ru_acl_info){
            return $http.post('/api/v1/remoteuseracls/', ru_acl_info);
        }

        function updateRuACL(ru_acl_id, ru_acl_info){
            return $http.put(
                '/api/v1/remoteuseracls/'+ru_acl_id+'/',
                ru_acl_info);
        }

        function deleteRuACL(ru_acl_id){
            return $http.delete('/api/v1/remoteuseracls/'+ru_acl_id+'/');
        }
    }

})();
