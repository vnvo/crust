(function (){
    'use strict';

    angular
        .module('crust.commandpatterns.services')
        .factory('CommandPatterns', CommandPatterns);

    CommandPatterns.$inject = ['$http'];

    function CommandPatterns($http){
        var CommandPatterns = {
            all: getAllCommandPatterns,
            get: getCommandPattern,
            count: getCPCount,
            create: createCommandPattern,
            update: updateCommandPattern,
            delete: deleteCommandPattern
        };

        return CommandPatterns;

        function getAllCommandPatterns(page_size, page, searchFilter, ordering){
            return $http.get('/api/v1/commandpatterns/', {
                params: {page_size:page_size, page:page,
                         search_filter:searchFilter, ordering:ordering}
            });
        }

        function getCPSuggestion(hint){
            return $http.get('/api/v1/commandpatterns/', {
                params: {hint: hint}
            });
        }

        function getCommandPattern(commandpattern_id){
            return $http.get('/api/v1/commandpatterns/'+commandpattern_id+'/');
        }

        function getCPCount(){
            return $http.get('/api/v1/commandpatterns/count/');
        }

        function createCommandPattern(commandpattern_info){
            return $http.post('/api/v1/commandpatterns/', commandpattern_info);
        }

        function updateCommandPattern(commandpattern_id, commandpattern_info){
            return $http.put(
                '/api/v1/commandpatterns/'+commandpattern_id+'/',
                commandpattern_info
            );
        }

        function deleteCommandPattern(commandpattern_id){
            return $http.delete(
                '/api/v1/commandpatterns/'+commandpattern_id+'/'
            );
        }
    }
})();
