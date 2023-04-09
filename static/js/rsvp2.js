function getReservation(inputName){
    $.getJSON('/api/v1/res/' + inputName, {}, function(data){
        $('#rsvplookup').hide();
    });
}