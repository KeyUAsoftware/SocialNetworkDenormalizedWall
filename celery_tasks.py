task
def process_profile_post_creation(post_id):
    post = Post.objects.get(id=post_id)
    if not post.finao.public:
        return
    for user in post.finao.users_following_only_finao.iterator():
        user.add_post_to_home_feed(post, type=PROFILE_FROM_FOLLOW_FINAO)
    for user in post.finao.users_following_only_tile.iterator():
        user.add_post_to_home_feed(post, type=PROFILE_FROM_FOLLOW_TILE)
    for user in post.finao.users_following_only_all_tiles.iterator():
        user.add_post_to_home_feed(post, type=PROFILE_FROM_FOLLOW_ALL_TILES)


@task
def process_profile_user_follow_finao(follow_id):
    follow = Follower.objects.get(id=follow_id)
    if not follow.finao.public:
        return
    for post in follow.finao.post_set.iterator():
        follow.user.add_post_to_home_feed(post, type=PROFILE_FROM_FOLLOW_FINAO)


@task
def process_profile_user_follow_tile(follow_id):
    follow = Follower.objects.get(id=follow_id)
    for post in follow.target_user.public_posts.filter(
            finao__tile=follow.tile).iterator():
        if post.finao.public:
            follow.user.add_post_to_home_feed(
                post=post, type=PROFILE_FROM_FOLLOW_TILE)


@task
def process_profile_user_follow_all_tiles(follow_id):
    follow = Follower.objects.get(id=follow_id)
    for post in follow.target_user.public_posts.iterator():
        if post.finao.public:
            follow.user.add_post_to_home_feed(
                post=post, type=PROFILE_FROM_FOLLOW_ALL_TILES)


@task
def process_profile_user_unfollow_finao(finao_id, user_id):
    finao = FINAO.objects.get(id=finao_id)
    user = UserModel.objects.get(id=user_id)
    for post in finao.post_set.all().iterator():
        user.remove_post_from_home_feed(post, type=PROFILE_FROM_FOLLOW_FINAO)


@task
def process_profile_user_unfollow_tile(tile_id, target_user_id, user_id):
    target_user = UserModel.objects.get(id=target_user_id)
    user = UserModel.objects.get(id=user_id)
    for post in target_user.public_posts.filter(
            finao__tile__id=tile_id).iterator():
        user.remove_post_from_home_feed(post, type=PROFILE_FROM_FOLLOW_TILE)


@task
def process_profile_user_unfollow_all_tiles(target_user_id, user_id):
    target_user = UserModel.objects.get(id=target_user_id)
    user = UserModel.objects.get(id=user_id)
    for post in target_user.public_posts.iterator():
        user.remove_post_from_home_feed(
            post, type=PROFILE_FROM_FOLLOW_ALL_TILES)


@task
def process_group_post_creation(post_id):
    post = Post.objects.get(id=post_id)
    group = post.finao.group
    for user in group.members.exclude(id=post.creator_id).iterator():
        if group.receive_all_posts_to_home_feed(user):
            user.add_post_to_home_feed(post, type=GROUP_MEMBER_ALL)
        if group.receive_posts_from_following(user) \
                and user in post.creator.followers:
            user.add_post_to_home_feed(post, type=GROUP_MEMBER_USERS_I_FOLLOW)
        if group.receive_posts_from_inspired(user) and Inspire.objects.filter(
                user=user, post__creator=post.creator).exists():
            user.add_post_to_home_feed(post, type=GROUP_MEMBER_USERS_I_INSPIRE)
        if group.receive_posts_from_both_inspired_and_following(user) and \
                Inspire.objects.filter(
                    user=user, post__creator=post.creator
                ).exists() and user in post.creator.followers:
            user.add_post_to_home_feed(
                post, type=GROUP_MEMBER_USER_I_FOLLOW_AND_INSPIRE)
    for user in group.followers.all().iterator():
        user.add_post_to_home_feed(post, type=GROUP_FOLLOWER_ALL)


@task
def process_group_join(groupmember_id):
    group_member = GroupMemberType.objects.get(id=groupmember_id)
    user = group_member.member
    group = group_member.group
    for post in group.all_posts.exclude(creator=user).iterator():
        if group.receive_all_posts_to_home_feed(user):
            user.add_post_to_home_feed(post, type=GROUP_MEMBER_ALL)
        if group.receive_posts_from_following(user) \
                and user in post.creator.followers:
            user.add_post_to_home_feed(post, type=GROUP_MEMBER_USERS_I_FOLLOW)
        if group.receive_posts_from_inspired(user) and Inspire.objects.filter(
                user=user, post__creator=post.creator).exists():
            user.add_post_to_home_feed(post, type=GROUP_MEMBER_USERS_I_INSPIRE)
        if group.receive_posts_from_both_inspired_and_following(user) and \
                Inspire.objects.filter(
                    user=user, post__creator=post.creator
                ).exists() and user in post.creator.followers:
            user.add_post_to_home_feed(
                post, type=GROUP_MEMBER_USER_I_FOLLOW_AND_INSPIRE)


@task
def process_leave_group(user_id, group_id):
    HomeFeed.objects.filter(
        user_id=user_id,
        post__finao__group_id=group_id
    ).delete()


@task
def process_user_group_settings_changed(setting_id):
    setting = UserGroupSettings.objects.get(id=setting_id)
    user = setting.user
    group = setting.group
    for post in group.all_posts.exclude(creator=user).iterator():
        if group.receive_all_posts_to_home_feed(user):
            user.add_post_to_home_feed(post, type=GROUP_MEMBER_ALL)
        else:
            user.remove_post_from_home_feed(post, type=GROUP_MEMBER_ALL)
        if group.receive_posts_from_following(user) \
                and user in post.creator.followers:
            user.add_post_to_home_feed(post, type=GROUP_MEMBER_USERS_I_FOLLOW)
        else:
            user.remove_post_from_home_feed(
                post, type=GROUP_MEMBER_USERS_I_FOLLOW)
        if group.receive_posts_from_inspired(user) and Inspire.objects.filter(
                user=user, post__creator=post.creator).exists():
            user.add_post_to_home_feed(post, type=GROUP_MEMBER_USERS_I_INSPIRE)
        else:
            user.remove_post_from_home_feed(
                post, type=GROUP_MEMBER_USERS_I_INSPIRE)
        if group.receive_posts_from_both_inspired_and_following(user) and \
                Inspire.objects.filter(
                    user=user, post__creator=post.creator
                ).exists() and user in post.creator.followers:
            user.add_post_to_home_feed(
                post, type=GROUP_MEMBER_USER_I_FOLLOW_AND_INSPIRE)
        else:
            user.remove_post_from_home_feed(
                post, type=GROUP_MEMBER_USER_I_FOLLOW_AND_INSPIRE)


@task
def process_user_group_follower_added(group_id, pk_set):
    group = Group.objects.get(id=group_id)
    for pk in pk_set:
        user = UserModel.objects.get(id=pk)
        for post in group.public_posts.iterator():
            user.add_post_to_home_feed(post, type=GROUP_FOLLOWER_ALL)


@task
def process_user_group_follower_removed(group_id, pk_set):
    group = Group.objects.get(id=group_id)
    for pk in pk_set:
        user = UserModel.objects.get(id=pk)
        for post in group.public_posts.iterator():
            user.remove_post_from_home_feed(post, type=GROUP_FOLLOWER_ALL)


@task
def process_user_sponsor_follower_added(sponsor_id, pk_set):
    sponsor = Sponsor.objects.get(id=sponsor_id)
    for pk in pk_set:
        user = UserModel.objects.get(id=pk)
        for post in sponsor.post_set.all().iterator():
            user.add_post_to_home_feed(post, type=SPONSOR)


@task
def process_user_sponsor_follower_removed(sponsor_id, pk_set):
    sponsor = Sponsor.objects.get(id=sponsor_id)
    for pk in pk_set:
        user = UserModel.objects.get(id=pk)
        for post in sponsor.post_set.all().iterator():
            user.remove_post_from_home_feed(post, type=SPONSOR)


@task
def process_sponsor_post_creation(post_id):
    post = Post.objects.get(id=post_id)
    for user in post.sponsor.followers.all().iterator():
        user.add_post_to_home_feed(post, type=SPONSOR)


@task
def repove_flagged_post_from_home_feed(flag_id):
    mark = PostMarkType.objects.get(id=flag_id)
    HomeFeed.objects.filter(
        post=mark.post, user=mark.user
    ).delete()


@periodic_task(run_every=timedelta(hours=1))
def find_recommended_posts():
    for user in UserModel.objects.all().iterator():
        tiles = user.user_tiles.values_list('id')
        # exclude or include ?
        finaos_exclude_ids = user.following_finaos.values_list('id', flat=True)

        top_followed_post = Post.objects.filter(
            ~Q(creator=user),
            ~Q(finao__id__in=finaos_exclude_ids),
            ~Q(postmarktype__user=user),
            ~Q(finao__group__members=user),
            finao__tile_id__in=tiles
        ).exclude(
            finao__public=False
        ).annotate(
            follower_count=Count('follower')
        ).order_by('-follower_count')
        if top_followed_post:
            RecommendedPost.objects.update_or_create(
                user=user,
                type=TOP_FOLLOWED,
                defaults={'post': top_followed_post.first()}
            )

        top_inspired_post = Post.objects.filter(
            ~Q(creator=user),
            ~Q(finao__id__in=finaos_exclude_ids),
            ~Q(postmarktype__user=user),
            ~Q(finao__group__members=user),
            finao__tile_id__in=tiles
        ).exclude(
            finao__public=False
        ).annotate(
            inspire_count=Count('inspire')
        ).order_by('-inspire_count')
        if top_inspired_post:
            RecommendedPost.objects.update_or_create(
                user=user,
                type=TOP_INSPIRED,
                defaults={'post': top_inspired_post.first()}
            )


@task
def remove_posts_from_homefeed(user_id, finao_id):
    HomeFeed.objects.filter(
        user__id=user_id,
        post__finao__id=finao_id
    ).delete()