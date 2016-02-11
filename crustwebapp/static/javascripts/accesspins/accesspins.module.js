(function (){
    'use strict';

    angular
        .module('crust.accesspins', [
            'crust.accesspins.controllers',
            'crust.accesspins.services'
        ]);

    angular
        .module('crust.accesspins.controllers', ['ngGrid']);

    angular
        .module('crust.accesspins.services', []);

})();
