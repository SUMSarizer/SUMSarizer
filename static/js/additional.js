$(function() {
    $("a.btn-link").each(function(){
        if($(this).attr("href") == window.location.pathname)
        $(this).addClass("btn-danger");
    	$(this).removeClass('btn-link');
    })
});