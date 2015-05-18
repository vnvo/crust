(function (){
    'use strict';

    angular
        .module('crust', [
            'crust.config',
            'crust.routes',
            'crust.authentication',
            'crust.layout',
            'crust.utils',
            'crust.dashboard',
            'crust.servers.server_groups',
            'crust.servers.servers',
            'crust.supervisors'
        ]);

    angular
        .module('crust.routes', ['ngRoute']);

    angular
        .module('crust.config', []);

})();

angular
    .module('crust')
    .run(run);

run.$inject = ['$http'];

/**
 * @name run
 * @desc Update xsrf $http headers to align with Django's defaults
 */
function run($http) {
    $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    $http.defaults.xsrfCookieName = 'csrftoken';
}
