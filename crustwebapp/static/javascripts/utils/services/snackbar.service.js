/**
 * Snackbar
 * @namespace crust.utils.services
 */
(function ($, _) {
    'use strict';

    angular
        .module('crust.utils.services')
        .factory('Snackbar', Snackbar);

    /**
     * @namespace Snackbar
     */
    function Snackbar() {
        /**
         * @name Snackbar
         * @desc The factory to be returned
         */
        var Snackbar = {
            error: error,
            show: show
        };

        return Snackbar;

        ////////////////////

        /**
         * @name _snackbar
         * @desc Display a snackbar
         * @param {string} content The content of the snackbar
         * @param {Object} options Options for displaying the snackbar
         */
        function _snackbar(content, options) {
            options = _.extend({ timeout: 3000 }, options);
            options.content = content;

            $.snackbar(options);
        }


        /**
         * @name error
         * @desc Display an error snackbar
         * @param {string} content The content of the snackbar
         * @param {Object} options Options for displaying the snackbar
         * @memberOf crust.utils.services.Snackbar
         */
        function error(content, options) {
            if(options.errors){
                angular.forEach(
                    options.errors,
                    function(key, val){
                        _snackbar(key+' : '+val);
                    }
                );
            }
            else
                _snackbar('Error: ' + content, options);
        }


        /**
         * @name show
         * @desc Display a standard snackbar
         * @param {string} content The content of the snackbar
         * @param {Object} options Options for displaying the snackbar
         * @memberOf crust.utils.services.Snackbar
         */
        function show(content, options) {
            _snackbar(content, options);
        }
    }
})($, _);
