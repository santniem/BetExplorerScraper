$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    var received = [];

    //receive details from server
    socket.on('newnumber', function(msg) {
        var betObject = JSON.parse(msg)
        
        //maintain a list of ten numbers
        if (received.length >= 10){
            received.shift()
        }            
        received.push(betObject);
        htmlString = '';
        
        for (var i = 0; i < received.length; i++){
            htmlString = htmlString + '<tr>'
            htmlString = htmlString + '<td><a href=' + received[i]["URL"]+'>'+"LINK" + '</a></td>';
            htmlString = htmlString + '<td>' +received[i]["BetType"]+'</td>';
            htmlString = htmlString + '<td>' +received[i]["Margin"]+'%'+'</td>';
            htmlString = htmlString + '<td>' +Object.keys(received[i]["Bookie 1"]["Bookies"])+'</td>';
            htmlString = htmlString + '<td>' +Object.keys(received[i]["Bookie 2"]["Bookies"])+'</td>';
            htmlString = htmlString + '<td>' +received[i]["Bookie 1"]["HomeOdds"]+'</td>';
            htmlString = htmlString + '<td>' +received[i]["Bookie 2"]["Awayodds"]+'</td>';
            htmlString = htmlString +'</tr>'
        }
        $('#log').html(htmlString);
    });

});