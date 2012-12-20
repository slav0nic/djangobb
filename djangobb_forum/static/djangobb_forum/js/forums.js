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
      header_id = $a.parent().attr('id'),
      body_id = header_id.replace("head", "body"),
      item_id = '#' + body_id;
      if ($inbox.hasClass('collapsed')){
        $inbox.removeClass("collapsed");
        $.cookie(body_id, '');
      }else {
        $inbox.addClass("collapsed");
        $.cookie(body_id, 'collapsed');
      }
      $inbox.slideToggle("slow");
    });
    
    set_collapser(1);
  
    set_collapser(2);
  
  });
  
})(jQuery);