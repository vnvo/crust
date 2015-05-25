(function (){
    'use strict';

    angular
        .module('crust.commandgroups', [
            'crust.commandgroups.controllers',
            'crust.commandgroups.services'
        ]);

    angular
        .module('crust.commandgroups.controllers', ['ngGrid']);

    angular
        .module('crust.commandgroups.services', []);

})();
