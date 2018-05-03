$(document).ready(function() {

	$('form').on('submit', function(event) {

		//remove action
		event.preventDefault();

		//disable submit
		$("#submit-upload").prop("disabled",true);

		//get form values
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
				//create alert-success
				if(data.success !== undefined){
				    $('.state').html(
				        '<div class="alert alert-success alert-dismissible" role="alert"> <strong>Success : </strong> '+data.success+'  <button type="button" class="close" data-dismiss="alert" aria-label="Close"> <span aria-hidden="true">&times;</span> </button> </div>'
                        );
						//redirect user to list of files after 3 second
                        window.setTimeout(function(){
                            window.location='/scan/files';
                        } , 3000);
					//create alert-danger
				} else {
					 $('.state').html(
				        '<div class="alert alert-danger alert-dismissible" role="alert"> <strong>Error : </strong> '+data.error+'  <button type="button" class="close" data-dismiss="alert" aria-label="Close"> <span aria-hidden="true">&times;</span> </button> </div>'
					 );
					 //set progress 0
                    setProgress(0);
                    $("#submit-upload").prop("disabled",false);

				}
			} ,

			error : function(data){
			    setProgress(0);
			    $('.state').html(
				        '<div class="alert alert-danger alert-dismissible" role="alert"> <strong>Error : </strong> an error occurred during the upload <button type="button" class="close" data-dismiss="alert" aria-label="Close"> <span aria-hidden="true">&times;</span> </button> </div>'
                        );
			}

		});

	});


	//set progress
	function setProgress(percent){
        $('#progressBar').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%');
	}

});

//create design on input file
$(function(){

  $('#input-file').fileselect();

});

