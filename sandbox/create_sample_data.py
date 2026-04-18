import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_test.settings')
django.setup()

from django.contrib.auth import get_user_model
from django_blog_it.models import Category, Tag, Article
from django.template.defaultfilters import slugify
from datetime import datetime, timedelta

User = get_user_model()
admin_user = User.objects.get(username='admin')

# 创建标签
tags_data = ['Python', 'Django', 'JavaScript', 'Vue', 'React', 'Database', 'Frontend', 'Backend', 'DevOps', 'AI']
tags = []
for tag_name in tags_data:
    tag, created = Tag.objects.get_or_create(name=tag_name)
    tags.append(tag)
    if created:
        print(f'创建标签: {tag.name}')

# 获取或创建分类
categories = list(Category.objects.all())
if not categories:
    cat1 = Category.objects.create(
        name='Tech',
        description='Technology articles',
        is_active=True,
        created_by=admin_user
    )
    cat2 = Category.objects.create(
        name='Life',
        description='Life articles',
        is_active=True,
        created_by=admin_user
    )
    categories = [cat1, cat2]
    print(f'创建分类: {cat1.name}, {cat2.name}')

# 创建文章
base_titles = [
    'Introduction to Django Framework',
    'Python Programming Tips',
    'Vue.js for Beginners',
    'Database Optimization Guide',
    'My Programming Story',
]

for i, base_title in enumerate(base_titles):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_title = f'{base_title} {timestamp}{i}'
    slug = slugify(unique_title)
    
    try:
        article = Article.objects.create(
            title=unique_title,
            slug=slug,
            content=f'<h2>{base_title}</h2><p>This is a sample article about {base_title.lower()}.</p>',
            category=categories[0] if i < 4 else (categories[1] if len(categories) > 1 else categories[0]),
            status='Published',
            publish_on=datetime.now().date() - timedelta(days=i),
            created_by=admin_user,
            views=100 + i * 10,
            likes_count=10 + i,
            comments_count=2 + i
        )
        article.tags.set([tags[i % len(tags)]])
        print(f'创建文章: {article.title}')
    except Exception as e:
        print(f'创建文章失败 {unique_title}: {e}')

print('\n示例数据创建完成！')
print(f'\n统计信息:')
print(f'分类数量: {Category.objects.count()}')
print(f'标签数量: {Tag.objects.count()}')
print(f'文章数量: {Article.objects.count()}')
