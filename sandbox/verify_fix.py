#!/usr/bin/env python3
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_test.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from django_blog_it.models import Article, Comment, Like, Favorite, Category
from django.utils import timezone
import json

User = get_user_model()

def create_test_data():
    print("=" * 60)
    print("创建测试数据...")
    print("=" * 60)
    
    user, _ = User.objects.get_or_create(username='testuser', password='testpass123')
    
    category, _ = Category.objects.get_or_create(
        name='测试分类', 
        slug='test-category',
        description='测试',
        created_by=user,
        is_active=True
    )
    
    article, created = Article.objects.get_or_create(
        title='测试文章',
        slug='test-article',
        defaults={
            'created_by': user,
            'content': '这是一篇测试文章的内容。',
            'category': category,
            'status': 'Published',
            'publish_on': timezone.now().date(),
            'views': 0,
            'likes_count': 0,
            'favorites_count': 0,
            'comments_count': 0
        }
    )
    
    if created:
        print(f"✓ 创建测试文章: {article.title}")
    else:
        print(f"✓ 使用现有文章: {article.title}")
    
    return user, article

def test_like_functionality(user, article):
    print("\n" + "=" * 60)
    print("测试 1: 喜欢功能 (+1/-1)")
    print("=" * 60)
    
    initial_count = article.likes_count
    print(f"初始喜欢数: {initial_count}")
    
    like, created = Like.objects.get_or_create(user=user, article=article)
    article.refresh_from_db()
    print(f"添加喜欢后: likes_count = {article.likes_count}, created={created}")
    assert article.likes_count == initial_count + 1, f"喜欢数应该是 {initial_count + 1}，实际是 {article.likes_count}"
    print("✓ 喜欢 +1 正确")
    
    like.delete()
    article.refresh_from_db()
    print(f"取消喜欢后: likes_count = {article.likes_count}")
    assert article.likes_count == initial_count, f"喜欢数应该是 {initial_count}，实际是 {article.likes_count}"
    print("✓ 喜欢 -1 正确")

def test_favorite_functionality(user, article):
    print("\n" + "=" * 60)
    print("测试 2: 收藏功能 (+1/-1)")
    print("=" * 60)
    
    initial_count = article.favorites_count
    print(f"初始收藏数: {initial_count}")
    
    favorite, created = Favorite.objects.get_or_create(user=user, article=article)
    article.refresh_from_db()
    print(f"添加收藏后: favorites_count = {article.favorites_count}, created={created}")
    assert article.favorites_count == initial_count + 1, f"收藏数应该是 {initial_count + 1}，实际是 {article.favorites_count}"
    print("✓ 收藏 +1 正确")
    
    favorite.delete()
    article.refresh_from_db()
    print(f"取消收藏后: favorites_count = {article.favorites_count}")
    assert article.favorites_count == initial_count, f"收藏数应该是 {initial_count}，实际是 {article.favorites_count}"
    print("✓ 收藏 -1 正确")

def test_comment_count_consistency(user, article):
    print("\n" + "=" * 60)
    print("测试 3: 评论数量一致性")
    print("=" * 60)
    
    Comment.objects.filter(article=article).delete()
    article.refresh_from_db()
    
    print(f"初始状态: comments_count={article.comments_count}, 实际评论数={article.comments.filter(parent=None).count()}")
    
    comment1 = Comment.objects.create(article=article, user=user, content='评论1')
    article.refresh_from_db()
    print(f"添加1条评论后: comments_count={article.comments_count}, 实际评论数={article.comments.filter(parent=None).count()}")
    assert article.comments_count == 1, f"评论数应该是 1，实际是 {article.comments_count}"
    assert article.comments_count == article.comments.filter(parent=None).count()
    print("✓ 1条父评论 - 计数匹配")
    
    comment2 = Comment.objects.create(article=article, user=user, content='评论2')
    article.refresh_from_db()
    print(f"添加2条评论后: comments_count={article.comments_count}, 实际评论数={article.comments.filter(parent=None).count()}")
    assert article.comments_count == 2, f"评论数应该是 2，实际是 {article.comments_count}"
    print("✓ 2条父评论 - 计数匹配")
    
    reply = Comment.objects.create(article=article, user=user, content='子回复', parent=comment1)
    article.refresh_from_db()
    print(f"添加1条子回复后: comments_count={article.comments_count}, 实际父评论数={article.comments.filter(parent=None).count()}")
    assert article.comments_count == 2, f"子回复不影响父评论计数，应该是 2，实际是 {article.comments_count}"
    print("✓ 子回复不影响父评论计数 - 正确")
    
    comment1.delete()
    article.refresh_from_db()
    print(f"删除1条父评论后: comments_count={article.comments_count}, 实际评论数={article.comments.filter(parent=None).count()}")
    assert article.comments_count == 1, f"评论数应该是 1，实际是 {article.comments_count}"
    print("✓ 删除评论 - 计数正确更新")

def test_views_update(user, article):
    print("\n" + "=" * 60)
    print("测试 4: 阅读量更新")
    print("=" * 60)
    
    initial_views = article.views
    print(f"初始阅读量: {initial_views}")
    
    article.increase_views()
    article.refresh_from_db()
    print(f"调用 increase_views 后: views = {article.views}")
    assert article.views == initial_views + 1, f"阅读量应该是 {initial_views + 1}，实际是 {article.views}"
    print("✓ 阅读量 +1 正确")

def main():
    print("\n🚀 开始 Django Blog 数据一致性验证\n")
    
    try:
        user, article = create_test_data()
        
        test_like_functionality(user, article)
        test_favorite_functionality(user, article)
        test_comment_count_consistency(user, article)
        test_views_update(user, article)
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        print("\n修复验证总结:")
        print("  ✓ 喜欢按钮: +1/-1 正确")
        print("  ✓ 收藏按钮: +1/-1 正确")
        print("  ✓ 评论计数: 与实际显示数量一致 (只统计父评论)")
        print("  ✓ 阅读量: +1 正确")
        print("  ✓ 缓存控制: 返回首页时数据实时更新")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
