$(document).ready(function() {

	$('form').on('submit', function(event) {

		event.preventDefault();

		$("#submit-upload").prop("disabled",true);

        let formData = new FormData($('form')[0]);

        $.ajax({

			xhr : function() {

                let xhr = new window.XMLHttpRequest();

                xhr.upload.addEventListener('progress', function(e) {

					if (e.lengthComputable) {
                        let percent = Math.round((e.loaded / e.total) * 100);
                        setProgress(percent);
					}

				});

				return xhr;
			},
			type : 'POST',
			url : '/scan/upload',
			data : formData,
			processData : false,
			contentType : false,

			success : function(data) {

				if(data.success !== undefined){
				    $('.state').html(
				        '<div class="alert alert-success alert-dismissible" role="alert"> <strong>Success : </strong> '+data.success+'  <button type="button" class="close" data-dismiss="alert" aria-label="Close"> <span aria-hidden="true">&times;</span> </button> </div>'
                        );

                        window.setTimeout(function(){
                            window.location='/scan/files';
                        } , 3000);
					//
				} else {
					 $('.state').html(
				        '<div class="alert alert-danger alert-dismissible" role="alert"> <strong>Error : </strong> '+data.error+'  <button type="button" class="close" data-dismiss="alert" aria-label="Close"> <span aria-hidden="true">&times;</span> </button> </div>'
                    );
                    setProgress(0);

				}
			} ,

			error : function(data){
			    setProgress(0);
			    $('.state').html(
				        '<div class="alert alert-danger alert-dismissible" role="alert"> <strong>Error : </strong> '+data+'  <button type="button" class="close" data-dismiss="alert" aria-label="Close"> <span aria-hidden="true">&times;</span> </button> </div>'
                        );
			}

		});

	});



	function setProgress(percent){
        $('#progressBar').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%');
	}

});


$(function(){

  $('#input-file').fileselect();

});

