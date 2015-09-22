(function (){
    'use strict';

    angular
        .module('crust.crustsessions', [
            'crust.crustsessions.controllers',
            'crust.crustsessions.services'
        ]);

    angular
        .module('crust.crustsessions.controllers', ['ngGrid', 'ui.bootstrap']);

    angular
        .module('crust.crustsessions.services', []);

})();
