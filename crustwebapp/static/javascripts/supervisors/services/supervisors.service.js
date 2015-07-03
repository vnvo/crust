/**
 * @namespace crust.supervisors.services
 */
(function(){
    'use strict';

    angular
        .module('crust.supervisors.services')
        .factory('Supervisors', Supervisors);

    Supervisors.$inject = ['$http'];

    /**
     * @namespace Supervisors
     * @returns {Factory}
     */
    function Supervisors($http){
        var Supervisors = {
            all: getAllSupervisors,
            getSuggestion: getSupSuggestion,
            create: createSupervisor,
            get: getSupervisor,
            update: updateSupervisor,
            delete: deleteSupervisor
        };

        return Supervisors;

        /**
         * @name getAllSupervisors
         * @desc fetch all Supervisors from backend
         * @returns {Promise}
         * @memberOf crust.supervisors.services.Supervisors
         */
        function getAllSupervisors(page_size, page){
            return $http.get('/api/v1/supervisors/', {
                params: {page_size: page_size, page: page}
            });
        }

        function getSupSuggestion(hint){
            return $http.get(
                '/api/v1/supervisors/',{
                    params: {hint: hint}
                }
            );
        }

        /**
         * @name createSupervisor
         * @desc create new Supervisor
         * @param username {string} unique username for new supervisor
         * @param password {string} password entered by user
         * @param email {string} email address for supervisor
         * @param is_admin {boolean} new supervisor has admin privilages or not
         * @returns {Promise}
         * @memberOf crust.supervisors.services.Supervisors
         */
        function createSupervisor(username, password, email, is_admin, is_active){
            return $http.post('/api/v1/supervisors/',{
                username: username,
                password: password,
                email: email,
                is_admin: is_admin,
                is_active: is_active
            });
        }

        /**
         * @name getSupervisor
         * @desc fetch information of the specified Supervisor by id
         * @param supervisor_id {integer} unique of the Supervisor
         * @returns {Promise}
         * @memberOf crust.supervisors.services.Supervisors
         */
        function getSupervisor(supervisor_id){
            return $http.get('/api/v1/supervisors/'+supervisor_id+'/');
        }

        /**
         * @name updateSupervisor
         * @desc update a Supervisor
         * @param supervisor_id {integer} unique id of Supervisor
         * @param supervisors_info {object} items to be updated on Supervisor
         * @returns {Promise}
         * @memberOf crust.supervisors.services.Supervisors
         */
        function updateSupervisor(supervisor_id, supervisor_info){
            return $http.put(
                '/api/v1/supervisors/'+supervisor_id+'/',
                supervisor_info
            );
        }

        /**
         * @name deleteSupervisor
         * @desc destroy specified Supervisor
         * @param supervisor_id {integer} unique id of Supervisor
         * @returns {Promise}
         * @memberOf crust.supervisors.services.Supervisors
        */
        function deleteSupervisor(supervisor_id){
            return $http.delete('/api/v1/supervisors/'+supervisor_id+'/');
        }
    }

})();
