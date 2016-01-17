(function(){
    /*
     Crust - Dashboard
     This module handles all the interactions and data presentation
     on the /dashboard route which consists mainly of widgets for
     other modules
     */
    'use strict';

    angular
        .module('crust.dashboard',[
            'crust.dashboard.controllers'
        ]);

    angular
        .module('crust.dashboard.controllers', ['highcharts-ng']);
})();
