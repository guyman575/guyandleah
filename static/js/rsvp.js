var MAX_GROUP_SIZE = 10;

for (let i = 0; i < MAX_GROUP_SIZE; i++){
    $(document).ready(function(){
        $(`input[name$="attending_${i}"]`).click(function(){
            var inputValue = $(this).val();
            if (inputValue == "Yes"){
                $(`#ifattending_${i}`).show();
                $(`input[name$="food_pref_${i}"]`).each(function() {
                    $(this).prop('required', true);
                });
                $(`input[name$="rehearsal_${i}"]`).each(function() {
                    $(this).prop('required', true);
                });
            }
            else {
                $(`#ifattending_${i}`).hide();
                $(`input[name$="food_pref_${i}"]`).each(function() {
                    $(this).prop('required', false);
                });
                $(`input[name$="rehearsal_${i}"]`).each(function() {
                    $(this).prop('required', false);
                });
            }
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