from django.contrib import admin
from .models import (Article, Category, Tag, BlogUser, Comment, 
                     Like, Favorite, Follow, UserProfile)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'website', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'bio', 'location']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('用户信息', {
            'fields': ('user', 'avatar', 'bio')
        }),
        ('个人信息', {
            'fields': ('website', 'location', 'birth_date')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'description', 'is_active', 'created_by', 'category_posts']
    list_filter = ['is_active', 'created_by']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ['created_by']
    
    def category_posts(self, obj):
        return obj.category_posts()
    category_posts.short_description = '文章数量'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['user', 'content', 'created_at']
    show_change_link = True


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'created_by', 'created_on', 
                    'views', 'likes_count', 'comments_count']
    list_filter = ['status', 'category', 'is_page', 'created_on', 'created_by']
    search_fields = ['title', 'content', 'meta_keywords']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['created_by', 'category']
    filter_horizontal = ['tags']
    readonly_fields = ['views', 'likes_count', 'favorites_count', 'comments_count', 
                       'created_on', 'updated_on']
    date_hierarchy = 'created_on'
    ordering = ['-created_on']
    inlines = [CommentInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'slug', 'category', 'tags', 'content')
        }),
        ('发布信息', {
            'fields': ('status', 'publish_on', 'is_page', 'created_by')
        }),
        ('SEO信息', {
            'fields': ('meta_description', 'meta_keywords', 'meta_author'),
            'classes': ('collapse',)
        }),
        ('统计数据', {
            'fields': ('views', 'likes_count', 'favorites_count', 'comments_count'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_on', 'updated_on'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['make_published', 'make_drafted', 'make_trashed']
    
    def make_published(self, request, queryset):
        count = queryset.update(status='Published')
        self.message_user(request, f'成功将 {count} 篇文章设置为已发布')
    make_published.short_description = '设置为已发布'
    
    def make_drafted(self, request, queryset):
        count = queryset.update(status='Drafted')
        self.message_user(request, f'成功将 {count} 篇文章设置为草稿')
    make_drafted.short_description = '设置为草稿'
    
    def make_trashed(self, request, queryset):
        count = queryset.update(status='Trashed')
        self.message_user(request, f'成功将 {count} 篇文章移至回收站')
    make_trashed.short_description = '移至回收站'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'content_preview', 'created_at', 'is_active', 'likes_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['content', 'user__username', 'article__title']
    raw_id_fields = ['user', 'article', 'parent']
    readonly_fields = ['created_at', 'updated_at', 'likes_count']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '评论内容'
    
    actions = ['activate_comments', 'deactivate_comments']
    
    def activate_comments(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {count} 条评论')
    activate_comments.short_description = '激活选中评论'
    
    def deactivate_comments(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'成功禁用 {count} 条评论')
    deactivate_comments.short_description = '禁用选中评论'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_article', 'get_comment', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'article__title']
    raw_id_fields = ['user', 'article', 'comment']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def get_article(self, obj):
        return obj.article.title if obj.article else '-'
    get_article.short_description = '文章'
    
    def get_comment(self, obj):
        return f'评论ID: {obj.comment.id}' if obj.comment else '-'
    get_comment.short_description = '评论'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'article__title']
    raw_id_fields = ['user', 'article']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']
    raw_id_fields = ['follower', 'following']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(BlogUser)
class BlogUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['user__username']
    raw_id_fields = ['user']
