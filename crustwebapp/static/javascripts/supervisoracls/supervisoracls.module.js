(function (){
    'use strict';

    angular
        .module('crust.supervisoracls', [
            'crust.supervisoracls.controllers',
            'crust.supervisoracls.services'
        ]);

    angular
        .module('crust.supervisoracls.controllers', ['ngGrid', 'ui.bootstrap']);

    angular
        .module('crust.supervisoracls.services', []);

})();
