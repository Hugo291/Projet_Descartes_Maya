$(function () {
    //reload page every 10 seconds
    setInterval(function() {
        refresh();
    }, 10000);

    //method refresh
    function refresh() {
        //ajax get values of progress files in json
        $.ajax({
            url: '/scan/progress',
            type: 'GET',
            success: function (data) {
                for (let i = 0; i < data.files.length; i++) {

                    //select table's line
                    $('.table-line').each(function (index) {

                        //get id of line
                        let html_id = $(this).find('td').eq(0).html();

                        //if line's id is equal ajax id
                        if (parseInt(data.files[i].id) === parseInt(html_id)) {

                            //set ajax html in line's
                            $(this).find('td').eq(2).html(data.files[i].html_status);
                            if (data.files[i].state === 2 || data.files[i].state === -1){
                                console.log(data.files[i].state);
                                var start = '<a class="text-center d-block" href="/scan/';

                                $(this).find('td').eq(3).html(start+'selection_extract/'+data.files[i].id+'"><i class="fa fa-folder-open"></i></a>');
                                $(this).find('td').eq(4).html(start+'download/'+data.files[i].id+'"><i class="fa fa-download"></i></a>');
                                $(this).find('td').eq(5).html(start+'selection_language/'+data.files[i].id+'"><i class="fa fa-language"></i></a>');
                            }

                        }
                    });

                }

            },

        });
    }


});