class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def home_feed_list(request):
        user = get_object_by_uid(uid=request.query_params.get('id'))
        limit = int(request.query_params.get('limit', 10))
        offset = int(request.query_params.get('offset', 0))
        queryset = user.home_feed_posts_with_recomended.prefetch_related(
            'creator',
            'creator__userprofile',
            'finao__creator__userprofile',
            'finao',
            'finao__group',
            'finao__tile',
            'finao__creator',
            'media_set',
            'weather',
            'location',
            'inspire_set',
            'encourage_set',
            'follower_set',
            'finao__follower_set',
            'finao__tile__follower_set',
            'finao__creator__followers_user'
        )
        serializer = PostSerializer(
            queryset[offset:offset+limit],
            many=True,
            context={
                'recommended': user.recommended_posts.values_list(
                    'id', flat=True),
                'request': request,
                'home-feed': True
            }
        )
        return Response({'data': serializer.data})