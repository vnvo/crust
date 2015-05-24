(function (){
    'use strict';

    angular
        .module('crust.remoteusers', [
            'crust.remoteusers.controllers',
            'crust.remoteusers.services'
        ]);

    angular
        .module('crust.remoteusers.controllers', ['ngGrid']);

    angular
        .module('crust.remoteusers.services', []);

})();
