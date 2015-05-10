(function() {
    'use strict';

    angular
        .module('crust.servers.server_groups', [
            'crust.servers.server_groups.controllers',
            'crust.servers.server_groups.services',
            'crust.servers.server_groups.directives'
        ]);

    angular
        .module('crust.servers.server_groups.controllers', [
            'ngGrid'
        ]);

    angular
        .module('crust.servers.server_groups.services', []);

    angular
        .module('crust.servers.server_groups.directives', [
            'ngDialog', 'ngGrid'
        ]);

})();
