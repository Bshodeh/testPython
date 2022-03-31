

document.addEventListener("DOMContentLoaded", function(event) { 
  // Update tocs
  addToc();
  
  
});

var addToc = function () {
	var header,
		headers,
		i,
		listSize,
		toc=[];
	
	headers = document.querySelectorAll("h1, h2, h3, h4, h5, h6");
	
	listSize = headers.length;
	for (i=0; i<listSize; i++) {
		toc.push(getTocLink (headers[i]))
	}
	
	tocElem = document.getElementById('toc');
	tocElem.innerHTML = toc.join('');
	
}


var getTocLink = function (headerElem) {
	var href,
		text,
		tag;
	tag = headerElem.tagName.toLowerCase();
	href = headerElem.id;
	text = headerElem.innerHTML;
	return '<li class="toc' + tag + '"><a href="#' + href + '">' + text + '</a></li>';
	
};

