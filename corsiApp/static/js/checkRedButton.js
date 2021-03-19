$(document).ready(function(){
  checkRedButtonJs();

	function checkRedButtonJs(){
		$.ajax({
			url: 'checkRedButtonDj/',
			type: 'post',
			data:{idSec: "" },
			success: function(data){
				// Perform operation on the return value
				alert(data);
			}
		});
	}

	$(document).ready(function(){
	 setInterval(checkRedButtonJs,1000);
	});
});
