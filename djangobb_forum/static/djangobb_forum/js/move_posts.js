$(document).ready(function () {
    $('form').submit(function (e) {
        var t = this,
            id = /\d+/.exec($('[name=to_topic]').val());
        e.preventDefault();
        if (!id) {
            alert('Invalid topic ID.');
            return;
        }
        $.get('/discuss/topic/' + id[0] + '/title/', function (title) {
            if (confirm('Do you really want to move these posts to "' + title + '"?')) {
                t.submit();
            }
        });
    });
});
