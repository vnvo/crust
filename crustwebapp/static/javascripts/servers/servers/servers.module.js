(function (){
    'use strict';

    angular
        .module('crust.servers.servers', [
            'crust.servers.servers.controllers',
            'crust.servers.servers.services'
        ]);

    angular
        .module('crust.servers.servers.controllers', ['ngGrid']);

    angular
        .module('crust.servers.servers.services', []);

})();
