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
                            $(this).find('td').eq(2).html(data.files[i].html);
                        }
                    });

                }

            },

        });
    }


});