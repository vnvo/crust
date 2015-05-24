(function (){
    'use strict';

    angular
        .module('crust.servers.serveraccounts',[
            'crust.servers.serveraccounts.controllers',
            'crust.servers.serveraccounts.services'
        ]);

    angular
        .module('crust.servers.serveraccounts.controllers', ['ngGrid']);

    angular
        .module('crust.servers.serveraccounts.services', []);

})();
