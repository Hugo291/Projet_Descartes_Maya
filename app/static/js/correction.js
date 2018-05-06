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
            success: function(data){
                if(data.success){
                     $('.state').html(
				        '<div class="alert alert-success alert-dismissible" role="alert"> ' +
                            '<strong>Success : </strong> Page n° '+page_number+' changed !! <button type="button" class="close" data-dismiss="alert" aria-label="Close"> ' +
                            '<span aria-hidden="true">&times;</span> </button> ' +
                        '</div>'
                );
                }else{
                    $('.state').html(
				        '<div class="alert alert-danger alert-dismissible" role="alert"> ' +
                            '<strong>Error : </strong> The page could not be modified <button type="button" class="close" data-dismiss="alert" aria-label="Close"> ' +
                            '<span aria-hidden="true">&times;</span> </button> ' +
                        '</div>'
                );
                }


            } , error:function (data) {
                $('.state').html(
				        '<div class="alert alert-danger alert-dismissible" role="alert"> ' +
                            '<strong>Error : </strong> The page could not be modified <button type="button" class="close" data-dismiss="alert" aria-label="Close"> ' +
                            '<span aria-hidden="true">&times;</span> </button> ' +
                        '</div>'
                );
            }});
    });

});