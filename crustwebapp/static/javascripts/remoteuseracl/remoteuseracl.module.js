(function (){
    'use strict';

    angular
        .module('crust.remoteuseracls', [
            'crust.remoteuseracls.controllers',
            'crust.remoteuseracls.services'
        ]);

    angular
        .module('crust.remoteuseracls.controllers', ['ngGrid', 'ui.bootstrap']);

    angular
        .module('crust.remoteuseracls.services', []);

})();
