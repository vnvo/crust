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
            'crust.supervisoracls',
            'crust.crustsessions',
            'crust.remote_connections'
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

// register filters
angular
    .module('crust')
    .filter('htmlAllow', htmlAllow)
    .filter('nl2br', nl2br)
    .filter('space2nbsp', space2nbsp);

htmlAllow.$inject = ['$sce'];
function htmlAllow($sce){
    return function(htmlCode){
        return $sce.trustAsHtml(htmlCode);
    };
};

function nl2br(){
    return function(text){
        console.log(text);
        return text ? text.toString().replace(/\n/g, '<br>') : '';
    };
};

function space2nbsp(){
    return function(text){
        return text ? text.replace(/ /g, '\u00a0') : '';
    };
};


/// register directives
angular
    .module('crust')
    .directive('csvReader', function() {
        return {
            scope: {
                csvReader:"="
            },
            link: function(scope, element) {
                $(element).on('change', function(changeEvent) {
                    var files = changeEvent.target.files;
                    if (files.length) {
                        var r = new FileReader();
                        r.onload = function(e) {
                            var contents = e.target.result;
                            scope.$apply(function () {
                                scope.csvReader = contents;
                            });
                        };
                        r.readAsText(files[0]);
                    }
                });
            }
        };
    });

angular
    .module('crust')
    .directive('passwordStrength', [
        function() {
            return {
                require: 'ngModel',
                restrict: 'E',
                scope: {
                    password: '=ngModel'
                },
                link: function(scope, elem, attrs, ctrl) {
                    scope.$watch('password', function(newVal) {
                        scope.strength = isSatisfied(newVal && newVal.length >= 8) +
                            isSatisfied(newVal && /[A-z]/.test(newVal)) +
                            isSatisfied(newVal && /(?=.*\W)/.test(newVal)) +
                            isSatisfied(newVal && /\d/.test(newVal));
                        function isSatisfied(criteria) {
                            return criteria ? 1 : 0;
                        }
                    }, true);
                },
                template: '<div class="progress" style="margin-bottom:0px;">' +
                    '<div class="progress-bar progress-bar-danger" style="width: {{strength >= 1 ? 25 : 0}}%"></div>' +
                    '<div class="progress-bar progress-bar-warning" style="width: {{strength >= 2 ? 25 : 0}}%"></div>' +
                    '<div class="progress-bar progress-bar-warning" style="width: {{strength >= 3 ? 25 : 0}}%"></div>' +
                    '<div class="progress-bar progress-bar-success" style="width: {{strength >= 4 ? 25 : 0}}%"></div>' +
                    '</div>'
            };
        }
    ]);
