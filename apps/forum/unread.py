from forum.models import Topic, Post, Read

def cache_unreads(qs, user):
    if not len(qs) or not user.is_authenticated():
        return qs
    if isinstance(qs[0], Topic):
        reads = Read.objects.filter(topic__pk__in=set(x.id for x in qs),
            user=user).select_related()
        read_map = dict((x.topic.id, x) for x in reads)

        for topic in qs:
            topic._read = read_map.get(topic.id, None)
        return qs
    elif isinstance(qs[0], Post):
        ids = set(x.topic.id for x in qs)
        reads = Read.objects.filter(topic__pk__in=ids, user=user).select_related()
        read_map = dict((x.topic.id, x) for x in reads)

        for post in qs:
            post.topic._read = read_map.get(post.topic.id, None)
        return qs
    else:
        raise Exception('cache_unreads could process only Post or Topic querysets')
