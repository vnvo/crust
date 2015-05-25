(function (){
    'use strict';

    angular
        .module('crust.commandpatterns', [
            'crust.commandpatterns.controllers',
            'crust.commandpatterns.services'
        ]);

    angular
        .module('crust.commandpatterns.controllers', ['ngGrid']);

    angular
        .module('crust.commandpatterns.services', []);

})();
