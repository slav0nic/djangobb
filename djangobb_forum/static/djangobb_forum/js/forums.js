(function($){
    // pre-ready
    // Enables toggling of the forum list's categories open and closed
    function set_collapser(cat_id) {
        var category_body_id = "category_body_" + cat_id;
        if($.cookie(category_body_id)){
            var head_id = "#" + category_body_id.replace("body", "head"),
                $inbox=$(head_id).next();
            $inbox.addClass("collapsed");
            $inbox.hide();
        }
    }
  
    // ready
    $(document).ready(function(){
    
        // the enables forum collapsing when the toggle element is clicked
        $("#idx1").on('click','a.toggle',function(event){
            var $a = $(this),
                $inbox = $a.closest('div.box').children('.box-content'),
                $header = $a.parent(),
                body_id = $header.attr('id').replace("head", "body"),
                item_id = '#' + body_id;
            if ($header.hasClass('collapsed')){
                $header.removeClass("collapsed");
                $.cookie(body_id, '');
            } else {
                $header.addClass("collapsed");
                $.cookie(body_id, 'collapsed');
            }
            $inbox.slideToggle("slow");
        });
        set_collapser(1);
        set_collapser(2);
    });

    // IP mute ban dialog when trying to post
    $('#post').on('submit', function(evt) {
        if (Scratch.INIT_DATA.IS_IP_BANNED) {
            evt.preventDefault();
            $('#ip-mute-ban').modal();
            return;
        }
    });

    var $subscribe = $('#subscribe');
    // Unsubscribe from topic button
    $subscribe.find('.unsubscribe a').on('click', function(evt) {
        evt.preventDefault();
        var $a = $(evt.target);
        var $loading = $subscribe.find('.unsubscribe .loading');
        $loading.show();
        $.get($a.attr('href')).success(function(data) {
            $subscribe.find('.unsubscribe').hide();
            $subscribe.find('.success').show();
        }).error(function() {
            $subscribe.find('.error').show();
        }).always(function() {
            $loading.hide();
        });
    });
    // Undo unsubscribe from topic
    $subscribe.find('.success a').on('click', function(evt) {
        evt.preventDefault();
        var $a = $(evt.target);
        var $loading = $subscribe.find('.success .loading');
        $loading.show();
        $.get($a.attr('href')).success(function(data) {
            $subscribe.find('.unsubscribe').show();
            $subscribe.find('.success').hide();
        }).error(function() {
            $subscribe.find('.error').show();
        }).always(function() {
            $loading.hide();
        });
    });
  
})(jQuery);
