var MAX_GROUP_SIZE = 2;

for (let i = 0; i < MAX_GROUP_SIZE; i++){
    $(document).ready(function(){
        $(`input[name$="attending_${i}"]`).click(function(){
            var inputValue = $(this).val();
            if (inputValue == "Yes"){
                $(`#ifattending_${i}`).show()
            }
            else (
                $(`#ifattending_${i}`).hide()
            )
        });
    });
}

$(document).ready(function(){
    $('form').each(function() {
        $(this).submit(
            function() {
                $(this).find(':input[type=submit]').prop('disabled', true);
            }
        );
    });
});