(function () {
    'use strict';

    var author = $('#id_author');
    var link = $('#delete-all-posts');
    link.click(function () {
        var username = author.val();
        if (!username) return;
        $.ajax('/discuss/admin/ajax/post-count/' + username + '/').done(function (data) {
            if (!data) return alert(username + ' does not exist');
            var n = Math.min(+data, 20);
            if (n === 0) return alert(username + ' doesn\'t have any posts')
            if (!confirm('About to move ' + n + ' of ' + data + ' posts to the Dustbin')) return;
            $.ajax('/discuss/admin/ajax/delete-all-posts/' + username + '/').done(function () {
                alert('Moved ' + n + ' posts to the Dustbin');
            });
        });
    });

}());
