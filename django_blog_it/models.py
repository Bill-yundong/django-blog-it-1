import arrow
from django.db import models
from django.template.defaultfilters import slugify
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

BLOG_STATUS_CHOICE = (
    ('Drafted', 'Drafted'),
    ('Published', 'Published'),
    ('Trashed', 'Trashed'),
    ('Review', 'Review')
)

ROLE_CHOICE = (
    ('Blog Admin', 'blog_admin'),
    ('Blog Publisher', 'blog_publisher'),
    ('Blog Author', 'blog_author'),
)


class BlogUser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name="user_roles")
    role = models.CharField(max_length=200, choices=ROLE_CHOICE,
                            default='blog_author')
    is_active = models.BooleanField(default=True)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True, default='')
    website = models.URLField(blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='')
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_followers_count(self):
        return self.followers.count()

    def get_following_count(self):
        return self.following.count()


class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)
    slug = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=500)
    is_active = models.BooleanField(default=False)
    meta_description = models.TextField(max_length=160, null=True, blank=True)
    meta_keywords = models.TextField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def category_posts(self):
        return Article.objects.filter(category=self).count()


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)
    slug = models.CharField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        tempslug = slugify(self.name)
        if self.id:
            tag = Tag.objects.get(pk=self.id)
            if tag.name != self.name:
                self.slug = create_tag_slug(tempslug)
        else:
            self.slug = create_tag_slug(tempslug)
        super(Tag, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


def create_tag_slug(tempslug):
    slugcount = 0
    while True:
        try:
            Tag.objects.get(slug=tempslug)
            slugcount += 1
            tempslug = tempslug + '-' + str(slugcount)
        except ObjectDoesNotExist:
            return tempslug


class Article(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='articles')
    content = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='related_posts')
    status = models.CharField(
        max_length=10, choices=BLOG_STATUS_CHOICE, default='Drafted')
    publish_on = models.DateField()
    meta_description = models.TextField(max_length=160, null=True, blank=True)
    meta_keywords = models.TextField(max_length=255, null=True, blank=True)
    meta_author = models.TextField(max_length=255, null=True, blank=True)
    is_page = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    favorites_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def create_activity(self, user, content):
        return History.objects.create(
            user=user, post=self, content=content
        )

    def create_activity_instance(self, user, content):
        return History(
            user=user, post=self, content=content
        )

    @property
    def created_on_arrow(self):
        return arrow.get(self.created_on).humanize()

    @property
    def published_on_arrow(self):
        return arrow.get(self.publish_on).humanize()

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def get_comments(self):
        return self.comments.filter(parent=None).order_by('-created_at')


def create_slug(tempslug):
    slugcount = 0
    while True:
        try:
            Article.objects.get(slug=tempslug)
            slugcount += 1
            tempslug = tempslug + '-' + str(slugcount)
        except ObjectDoesNotExist:
            return tempslug


class History(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    post = models.ForeignKey(
        Article, related_name='history', on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    is_page = models.BooleanField(default=False)

    def __str__(self):
        return '{username} {content} {blog_title}'.format(
            username=str(self.user.get_username()),
            content=str(self.content),
            blog_title=str(self.post.title)
        )


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    likes_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.article.title}'

    def get_replies(self):
        return self.replies.filter(is_active=True)

    def get_likes_count(self):
        return self.likes.count()


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'article', 'comment']

    def __str__(self):
        if self.article:
            return f'{self.user.username} likes {self.article.title}'
        return f'{self.user.username} likes comment {self.comment.id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.article:
            self.article.likes_count = self.article.likes.count()
            self.article.save(update_fields=['likes_count'])
        if self.comment:
            self.comment.likes_count = self.comment.likes.count()
            self.comment.save(update_fields=['likes_count'])

    def delete(self, *args, **kwargs):
        article = self.article
        comment = self.comment
        super().delete(*args, **kwargs)
        if article:
            article.likes_count = article.likes.count()
            article.save(update_fields=['likes_count'])
        if comment:
            comment.likes_count = comment.likes.count()
            comment.save(update_fields=['likes_count'])


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'article']

    def __str__(self):
        return f'{self.user.username} favorites {self.article.title}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.article.favorites_count = self.article.favorites.count()
        self.article.save(update_fields=['favorites_count'])

    def delete(self, *args, **kwargs):
        article = self.article
        super().delete(*args, **kwargs)
        article.favorites_count = article.favorites.count()
        article.save(update_fields=['favorites_count'])


class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['follower', 'following']

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if hasattr(self.following, 'profile'):
            self.following.profile.save()
        if hasattr(self.follower, 'profile'):
            self.follower.profile.save()

    def delete(self, *args, **kwargs):
        following = self.following
        follower = self.follower
        super().delete(*args, **kwargs)
        if hasattr(following, 'profile'):
            following.profile.save()
        if hasattr(follower, 'profile'):
            follower.profile.save()
