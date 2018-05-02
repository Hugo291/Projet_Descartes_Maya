$(function () {

    $('.btn-correction').click(function (e) {

        //remove action
        e.preventDefault();
        //get id pdf
        var pdf_id = $('.select').data('pdf_id');

        //get the page number
        var page_number = $('.select').data('page_number');

        //url ajax
        var url = "/scan/correct/"+pdf_id+"/"+page_number;

        //ajax
        $.ajax({
            url: url,
            type:"POST",
            data:{
                //the text of textarea send
                'text':$('#textarea-text-page').val()
            },
            success: function(results){
                //alert result
                alert(results);
            }});
    });

});