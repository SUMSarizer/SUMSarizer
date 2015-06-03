$(function() {
    $("a.btn-link").each(function(){
        if($(this).attr("href") == (window.location.pathname+window.location.search))
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

    $('#searchDingus').keyup(function(){
        var searchText = $(this).val();
        $('ul#otherUsers > li').each(function(){
            var currentLiText = $(this).text(),
                showCurrentLi = currentLiText.indexOf(searchText) !== -1;            
            $(this).toggle(showCurrentLi);
        });     
    });
});
