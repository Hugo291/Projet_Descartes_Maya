$(function () {
    var timerId = setInterval(function() {
        refresh();
    }, 10000);
    function refresh() {
        $.ajax({
            url: '/scan/progress',
            type: 'GET',
            success: function (data) {
                for (let i = 0; i < data.files.length; i++) {
                    console.log(data.files[i].id);

                    $('.table-line').each(function (index) {

                        let html_id = $(this).find('td').eq(0).html();

                        if (parseInt(data.files[i].id) === parseInt(html_id)) {
                            $(this).find('td').eq(2).html(data.files[i].html);
                        }
                    });

                }

            },

        });
    }


});