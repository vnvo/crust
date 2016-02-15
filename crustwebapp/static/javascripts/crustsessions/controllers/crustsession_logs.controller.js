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
        vm.event_time = null;
        $scope.current_session_event_index = 0;
        $scope.current_event_id = null;
        $scope.session_play = false;
        $scope.playback_speed = 'No Delay';
        $scope.session_events = [];
        $scope.session_status = null;
        vm.session_created_at = null;
        vm.session_terminated_at = null;
        $scope.last_event_epoch = null;


        $scope.$on('$destroy', function(){
            $scope.session_play = false;
        });

        vm.sendMsg = function(){
            CrustSessions.sendMsg($scope.session_id, vm.message).then(
                function(data, status, headers, config){
                    Snackbar.show('Message Sent');
                    vm.message = null;
                },
                function(data, status, headers, config){
                    Snackbar.error('Error on sending message.');
                }
            );
        };

        $scope.killSession = function(){
            if(!confirm('You are killing an Active Session, Are you sure?'))
                return;

            CrustSessions.kill($scope.session_id).then(
                killSuccess, killError
            );
            function killSuccess(data, status, headers, config){
                Snackbar.show('Session Killed Successfuly.');

            }
            function killError(data, status, headers, config){
                Snackbar.error(
                    'Can not Kill Active Session',
                    {errors: data.data}
                );
            }
        };

        function formatEventTime(evt){
            var et = new Date(evt*1000); //unix epoch
            return et.toISOString().replace('T',' ').split('.')[0];
        }

        $scope.playSessionEvents = function(){
            console.log('playing session events');
            if(!$scope.session_play)
                return;

            console.log(
                $scope.current_session_event_index,
                $scope.session_events.length
            );

            if($scope.current_session_event_index >= $scope.session_events.length-1){
                console.log('no more session event');
                if($scope.session_status.indexOf('CLOSED')!=-1){
                    console.log('end of session');
                    $scope.session_play = false;
                    $scope.current_session_event_index = 0;
                    return;
                }else{
                    console.log('get next page ...');
                    $timeout(
                        function(){$scope.getNextPage();},
                        100);
                }
            }
            console.log('play event index:', $scope.current_session_event_index);
            // display current event
            $scope.current_session_event = $scope.session_events[
                $scope.current_session_event_index
            ];
            vm.event_time = formatEventTime(
                $scope.current_session_event.event_time
            );

            $scope.current_event_id = $scope.current_session_event['id'];

            //set next event and delay for display
            var next_event_index = $scope.current_session_event_index + 1;
            var next_event = $scope.session_events[next_event_index];
            if(next_event==undefined){
                $scope.current_session_event_index = $scope.session_events.length-1;
                $timeout(
                    function(){
                        $scope.playSessionEvents();
                    }, 1000
                );
                return;
            }
            if($scope.playback_speed!='No Delay'){
                var delay = next_event.event_time -  $scope.current_session_event.event_time;
                delay = delay*1000; //to seconds
                delay = delay/$scope.playback_speed;
                console.log('delay next event: '+delay);
            }
            else{
                console.log('playback in no delay');
                delay = 200;
            }

            $timeout(
                function(){
                    $scope.current_session_event_index = next_event_index;
                    $scope.playSessionEvents();
                }, delay
            );
        };

        function getSession(){
            CrustSessions.get($scope.session_id).then(
                function(data, status, headers, config){},
                function(data, status, headers, config){}
            );
        }

        $scope.getNextPage = function(){
            CrustSessions.logs(
                $scope.session_id, $scope.page_size,
                $scope.current_page, $scope.last_event_epoch
            ).then(
                function(data, status, headers, config){
                    $scope.session_events = data.data.events;
                    $scope.session_status = data.data.status;
                    vm.session_created_at = data.data.session_created_at;
                    vm.session_terminated_at = data.data.session_terminated_at;
                    $timeout(
                        function(){console.log($scope.session_events.length);},
                        100
                    );
                },
                function(data, status, headers, config){
                    Snackbar.error('Could not get Session Logs');
                    //console.log(data);
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
