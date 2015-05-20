$(function() {
    $("a.btn-link").each(function(){
        if($(this).attr("href") == window.location.pathname)
        $(this).addClass("btn-danger");
    	$(this).removeClass('btn-link');
    })

	var chart = $("#mainChart"),
	    aspect = chart.width() / chart.height(),
	    container = chart.parent();
	$(window).on("resize", function() {
	    var targetWidth = container.width();
	    chart.attr("width", targetWidth);
	    chart.attr("height", Math.round(targetWidth / aspect));
	}).trigger("resize");

});

