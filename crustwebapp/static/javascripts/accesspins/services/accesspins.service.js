(function (){
    'use strict';

    angular
        .module('crust.accesspins.services')
        .factory('AccessPins', AccessPins);

    AccessPins.$inject = ['$http'];

    function AccessPins($http){
        var AccessPins = {
            all: getAllAccessPins,
            get: getAccessPin,
            create: createAccessPin,
            update: updateAccessPin,
            delete: delAccessPin
        };

        return AccessPins;

        function getAllAccessPins(page_size, page, search_filter, ordering){
            return $http.get('/api/v1/accesspins/', {
                params: {page_size: page_size, page:page,
                         search_filter:search_filter, ordering:ordering}
            });
        }

        function getAccessPin(accesspin_id){
            return $http.get('/api/v1/accesspins/'+accesspin_id+'/');
        }

        function createAccessPin(accesspin_info){
            return $http.post('/api/v1/accesspins/', accesspin_info);
        }

        function updateAccessPin(accesspin_id, accesspin_info){
            return $http.put(
                '/api/v1/accesspins/'+accesspin_id+'/', accesspin_info
            );
        }

        function delAccessPin(accesspin_id){
            return $http.delete('/api/v1/accesspins/'+accesspin_id+'/');
        }
    }

})();
