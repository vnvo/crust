/**
* Authentication Service
* @namespace crust.authentication.services
*/
(function (){
    'use strict';

    angular
        .module('crust.authentication.services')
        .factory('Authentication', Authentication);

    Authentication.$inject = ['$cookies', '$http', '$filter', 'Snackbar'];

    /**
     * @namespace Authentication
     * @returns {Factory}
     */
    function Authentication($cookies, $http, $filter, Snackbar){
        /**
         * @name Authentication
         * @desc The Factory for Authentication mechanism to be returned
         */

        var Authentication = {
            login: login,
            logout: logout,
            getAuthenticatedAccount: getAuthenticatedAccount,
            isAdmin: isAdmin,
            getLoginTime: getLoginTime,
            isAuthenticated: isAuthenticated,
            setAuthenticatedAccount: setAuthenticatedAccount,
            unauthenticate: unauthenticate
        };

        return Authentication;

        ///////////////////////////////////

        /**
         * @name login
         * @desc Try to authenticate a supervisor using username & password
         * @param {string} username, Username entered by user
         * @param {string} password, Password entered by user
         * @returns {Promise}
         * @memberOf crust.authentication.services.Authentication
         */
        function login(username, password){
            return $http.post(
                '/api/v1/auth/login/',
                {username: username,
                 password: password
                }
            ).then(loginSuccessFn, loginErrorFn);

            /**
             * @name loginSuccessfn
             * @desc set authenticated account on successful login
             */
            function loginSuccessFn(data, status, header, config){
                Authentication.setAuthenticatedAccount(data.data);
                window.location = '/';
            }

            /**
             * @name loginErrorfn
             * @desc show error message on failed login
             */
            function loginErrorFn(data, status, header, config){
                Snackbar.error('Login Error, ', {errors:data.data});
                console.log('Login, Internal Error'); // @todo: alert user
                console.log(data);
            }
        }

        /**
         * @name logout
         * @desc log the current user out
         * @returns {Promise}
         * @memberOf crust.authentication.services.Authentication
         */
        function logout(){
            return $http.post(
                '/api/v1/auth/logout/'
            ).then(logoutSuccessFn, logoutErrorFn);

            /**
             * @name logoutSuccessfn
             * @desc Unauthenticate and redirect to login page on success
             */
            function logoutSuccessFn(data, status, header, config){
                Authentication.unauthenticate();
                window.location = '/login';
            }

            /**
             * @name logoutErrorfn
             * @desc log something to console for now
             */
            function logoutErrorFn(data, status, header, config){
                Snackbar.error('Logout Error, ', {errors: data});
                console.log('Logout, Internal Error');
            }
        }

        /**
         * @name getAuthenticatedaccount
         * @name fetch authenticated account for current session
         * @returns {object|undefined}
         * @memberOf crust.authentication.services.Authentication
         */
        function getAuthenticatedAccount(){
            if (!$cookies.authenticatedAccount)
                return undefined;

            return JSON.parse($cookies.authenticatedAccount);
        }


        function isAdmin(){
            return Authentication.getAuthenticatedAccount().is_admin;
        }

        /**
         * @name getLogintime
         * @desc Return login time for the current user
         * @returns {string|undefined}
         * @memberOf crust.authentication.services.Authentication
         */
        function getLoginTime(){
            if (!$cookies.accountLoginTime)
                return undefined;

            return $cookies.accountLoginTime;
        }

        /**
         * @name isAuthenticated
         * @desc checks if current session has an authenticated user
         * @returns {boolean}
         * @memberOf crust.authentication.services.Authentication
         */
        function isAuthenticated(){
            console.log($cookies.accountLoginTime);
            var now = (new Date).getTime();
            console.log(now-$cookies.accountLoginTime);
            return !!$cookies.authenticatedAccount ||
                now-$cookies.accountLoginTime < 600;
        }

        /**
         * @name setAuthenticatedaccount
         * @desc set authenticated account and login time in cookie
         * @param {object} supervisor account info to be set
         * @returns {undefined}
         * @memberOf crust.authentication.services.Authentication
         */
        function setAuthenticatedAccount(account){
            $cookies.authenticatedAccount = JSON.stringify(account);
            $cookies.accountLoginTime = (new Date).getTime();
            //$filter('date')(new Date(),'yyyy-MM-dd H:mm:ss');
            console.log('login='+$cookies.accountLoginTime);
        }

        /**
         * @name unauthenticate
         * @desc delete the cookie where authenticated account info is kept
         * @returns {undefined}
         * @memberOf crust.authentication.services.Authentication
         */
        function unauthenticate(){
            delete $cookies.authenticatedAccount;
            delete $cookies.accountLoginTime;
        }
    }

})();
