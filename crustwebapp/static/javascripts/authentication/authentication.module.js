(function (){
    'use strict';

    angular
        .module('crust.authentication', [
            'crust.authentication.controllers',
            'crust.authentication.services'
        ]);

    angular
        .module('crust.authentication.controllers', []);

    angular
        .module('crust.authentication.services', ['ngCookies']);

})();
