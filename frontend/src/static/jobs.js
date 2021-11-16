// wait until the dom is loaded
document.addEventListener('DOMContentLoaded', function(event){
	var form = document.getElementById("formCont");

	var jobBatchToken;

	function handleForm(event) {
		// prevent the default action of reloading the page or 
		// going somewhere else
		event.preventDefault();
		
		var xhr = new XMLHttpRequest();
		xhr.open("POST", "/api/model/upload");
		xhr.setRequestHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8");
		xhr.setRequestHeader("Access-Control-Allow-Origin", "*");

		xhr.onreadystatechange = function(){
			if(xhr.readyState === 4){
				console.log(xhr.status);
				var jsonResult = JSON.parse(xhr.responseText);
				jobBatchToken = jsonResult.batch_token;
				checkBatchJob();
			}
		}
	
	 	// get the image from the form
		var imageFile = document.getElementById("file-selector").files[0];
		var formData = new FormData();

		if(imageFile) {
			formData.append('image', imageFile);
			xhr.send(formData);
		}
	}

	function checkBatchJob() {
		var xhr = new XMLHttpRequest();

		xhr.open("GET", "/api/model/batch?token=" + jobBatchToken);
		xhr.setRequestHeader("Access-Control-Allow-Origin", "*");

		xhr.onreadystatechange = function() {
			if(xhr.readyState === 4) {
				console.log(xhr.status);
				console.log(xhr.response);
			}
		}

		xhr.send();
	}

	form.addEventListener('submit', handleForm);
});
