$(function() {
    settings = {
      tl: { radius: 1 },
      tr: { radius: 1 },
      bl: { radius: 10 },
      br: { radius: 10 },
      antiAlias: true,
      autoPad: false,
      validTags: ['div', 'ul', 'li']
    }

    $('.corners').each(function() {
        var cornersObj = new curvyCorners(settings, this);
        cornersObj.applyCornersToAll();
    });
});
