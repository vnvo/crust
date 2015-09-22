(function(){
    'use strict';

    angular
        .module('crust.crustsessions.controllers')
        .controller('CrustSessionLogsController', CrustSessionLogsController);

    CrustSessionLogsController.$inject = [
        '$scope', '$routeParams', 'CrustSessions',
        'Snackbar', '$timeout', '$sce'
    ];

    function CrustSessionLogsController($scope, $routeParams, CrustSessions,
                                        Snackbar, $timeout, $sce) {
        var vm = this;

        $scope.session_id = $routeParams.session_id;
        $scope.current_page = 1;
        $scope.page_size = 50000;
        $scope.current_session_event = null;
        $scope.current_session_event_index = 0;
        $scope.session_play = false;
        $scope.session_events = [];
        $scope.last_event_epoch = null;

        $scope.playSessionEvents = function(){
            console.log('playing session events');
            if(!$scope.session_play)
                return;

            console.log(
                $scope.current_session_event_index,
                $scope.session_events.length
            );

            if($scope.current_session_event_index >= $scope.session_events.length-1){
                console.log('end of session_logs');
                return;
            }
            console.log('play event index:', $scope.current_session_event_index);
            // display current event
            $scope.current_session_event = $scope.session_events[
                $scope.current_session_event_index
            ];

            //set next event and delay for display
            var next_event_index = $scope.current_session_event_index + 1;
            var next_event = $scope.session_events[next_event_index];
            var delay = next_event.event_time -  $scope.current_session_event.event_time;
            delay = delay*1000; //to seconds
            console.log('delay next event: ', delay*1000);

            $timeout(
                function(){
                    $scope.current_session_event_index = next_event_index;
                    $scope.playSessionEvents();
                }, delay
            );

        };

        $scope.getNextPage = function(){
            CrustSessions.logs(
                $scope.session_id, $scope.page_size, $scope.current_page
            ).then(
                function(data, status, headers, config){
                    $scope.session_events = data.data;
                    $timeout(
                        function(){console.log($scope.session_events.length);},
                        100
                    );
                },
                function(data, status, headers, config){
                    Snackbar.error('Could not get Session Logs');
                    console.log(data);
                }
            );
        };

        $scope.getNextPage();
        $scope.$watch('session_play',function(){
            console.log('watched: session_play', $scope.session_play);
            $scope.playSessionEvents();
        });
    }


})();
