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

    if (!Scratch.INIT_DATA.IS_SOCIAL) {
        $('#post textarea').limit('0');
        $('#post textarea').focus(function() {
            openResendDialogue(); //see account-nav.js for function definition
        });
    }

    // Follow/unfollow topic logic
    var $follow = $('.follow-topic');
    var followclick = function(evt) {
        evt.preventDefault();
        var $button = $(evt.target);
        var $loading = $follow.find('.loading');
        var $error = $follow.find('.error');
        $loading.show();
        $error.hide();
        $.get($button.attr('href')).done(function(data) {
            if ($button.hasClass('follow-button')) {
                // now following, show unfollow
                $follow.find('.follow-button').hide();
                $follow.find('.unfollow-button').show();
            } else {
                // want to unfollow topic
                $follow.find('.follow-button').show();
                $follow.find('.unfollow-button').hide();
            }
        }).fail(function() {
            $error.show();
        }).always(function() {
            $loading.hide();
        });
    };
    $follow.find('.follow-button').on('click', followclick);
    $follow.find('.unfollow-button').on('click', followclick);

})(jQuery);
