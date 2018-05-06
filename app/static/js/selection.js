$(function () {

    //set listener on page
    $('.page-element-selection').click(function() {

        //search value
        searchBox(this);
    });

    //get first page's value on load
    searchBox($('.page-element-selection:first'));

});
//start loader
function startLoad(text) {
    $('#load-process').html(
        "<div class='row'>" +
            "<div class='loader mr-3 ml-3'></div>" +
            "<div>"+text+"</div>" +
        "</div>"
    );
}
//end loader
function endLoad(text) {
    $('#load-process').html("" +
        "<div class='row '>" +
            "<div class='ml-3'>" +
                text+"" +
            "</div>" +
        "</div>")
}

//set select method
function setBackgroundSelect(CurrentSelect) {
    $('.page-element-selection').removeClass("select");
    $(CurrentSelect).addClass('select');
}


//set value after get ajax value
function setInfoPage(ctx , pdf_id , page_number) {
     //get info of scan page box(word) and text
        $.ajax({url: "/scan/page/"+pdf_id+"/"+page_number, success: function(results){

            if(ctx != null) {
                //boxs word
                var boxs = results.box;
                last_boxs = boxs;
                //create all box
                for (let index in boxs) {

                    //draw box in canvas
                    let box = boxs[index];
                    ctx.rect(box.position_left, box.position_top, box.size_width, box.size_height);
                    ctx.stroke();
                    ctx.lineWidth = 1;
                    ctx.strokeStyle = "#FF0000";
                }
            }
            //set value in textarea
            setTextAreaText(results.text);

            //end load
            endLoad('The page n°'+(parseInt(page_number)+1)+' is loaded');
        }});
}
//set value in text area
function setTextAreaText(text) {
    $('#textarea-text-page').val(text);
}

//canvas
function canvasBox(currentSelect) {
    var src = $(currentSelect).find("img").attr('src');

    var canvas = document.getElementById("canvas-selection");

    //canvas
    ctx = canvas.getContext("2d");

    //image background convas
    var background = new Image();
    background.src = src;

    //set canvas size
    canvas.width = background.width;
    canvas.height = background.height;

    //set size of
    $('#textarea-text-page').height = background.height;
    $('.scroll-list-image').height = background.height;


    canvas.background= src;

    background.onload = function(){
        ctx.drawImage(background,0,0);
    };

    return ctx;
}

//main method
function searchBox(currentSelect) {

    //set background in current page selected
    setBackgroundSelect(currentSelect);

    //get pdf id
    var pdf_id = $(currentSelect).data('pdf_id');

    //get page number
    var page_number = $(currentSelect).data('page_number');

    // set load start
    startLoad("waiting for the page "+(page_number+1));
    let ctx = null;

    let canvas = document.getElementById("canvas-selection");

    if(canvas != null){
        //create canvas
         ctx = canvasBox(currentSelect);
    }
    //set date
    setInfoPage(ctx , pdf_id , page_number);
}


//selection langue

$(function () {

    var current_value_selected = "";

    $('textarea:first').keyup(update).mousedown(update).mousemove(update).mouseup(update);

    function update(e) {
        var range = $(this).getSelection();
        current_value_selected = range.text;
    }

    $('#btn-lang-1').click(function () {
        $('#textarea_lang_1').html(current_value_selected);
    });
    $('#btn-lang-2').click(function () {
        $('#textarea_lang_2').html(current_value_selected);
    });

    $('#form-selection').on('submit', function(event) {

        event.preventDefault();

        var textLangue1 = $('#textarea_lang_1').html();
        var textLangue2 = $('#textarea_lang_2').html();
        var ValueLanguage1 = $( "#lang-select-1" ).val();
        var ValueLanguage2 = $('#lang-select-2').val();


        $.ajax({
            url: "/scan/add_word",
            type: "POST",
            data: {
                'text_word_1':textLangue1,
                'lang_1':ValueLanguage1,
                'text_word_2':textLangue2 ,
                'lang_2':ValueLanguage2
            },
            success : function (data) {
                if(data.success){
                    alert(data.success);
                    $('#textarea_lang_2').empty();
                    $('#textarea_lang_1').empty();
                     $('.state').html(
				        '<div class="alert alert-success alert-dismissible" role="alert"> <strong>Success : </strong> '+data.success+'  <button type="button" class="close" data-dismiss="alert" aria-label="Close"> <span aria-hidden="true">&times;</span> </button> </div>'
					 );

                }else{
                    $('.state').html(
				        '<div class="alert alert-danger alert-dismissible" role="alert"> <strong>Error : </strong> '+data.error+'  <button type="button" class="close" data-dismiss="alert" aria-label="Close"> <span aria-hidden="true">&times;</span> </button> </div>'
					 );
                }
            },error : function (data) {
                $('.state').html(
				        '<div class="alert alert-danger alert-dismissible" role="alert"> <strong>Error : </strong> One error raise during update <button type="button" class="close" data-dismiss="alert" aria-label="Close"> <span aria-hidden="true">&times;</span> </button> </div>'
					 );

            }
        });
    });



});


