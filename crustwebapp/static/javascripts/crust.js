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
            'crust.servers.serveraccounts',
            'crust.supervisors',
            'crust.remoteusers',
            'crust.commandgroups',
            'crust.commandpatterns',
            'crust.remoteuseracls',
            'crust.supervisoracls'
        ]);

    angular
        .module('crust.routes', ['ngRoute']);

    angular
        .module('crust.config', []);

})();

angular
    .module('crust')
    .run(run);

run.$inject = ['$http', '$rootScope', '$location', 'Authentication'];

/**
 * @name run
 * @desc Update xsrf $http headers to align with Django's defaults
 */
function run($http, $rootScope, $location, Authentication) {
    $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    $http.defaults.xsrfCookieName = 'csrftoken';

    $rootScope.$on('$routeChangeStart', checkRouteChange);
    $rootScope.$on('$routeChangeSuccess', highlightMenuItem);

    function checkRouteChange(event){
        if(!Authentication.isAuthenticated()){
            console.log('is not authenticated');
            //event.preventDefault();
            console.log($location.url());
            if($location.url() != '/login'){
                event.preventDefault();
                $location.path('/login');
            }
        }
    }

    function highlightMenuItem(event){
        var src_element = $('.active');
        if(src_element)
            src_element.removeClass('active');

        var url = window.location;
        var dest_element = $('ul.nav a').filter(function() {
            return this.href == url || url.href.indexOf(this.href) == 0;
        }).addClass('active').parent().parent().addClass('in').parent();
        if (dest_element.is('li')) {
            dest_element.addClass('active');
        }
    }
}
