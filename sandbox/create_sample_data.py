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
    'Python Programming Best Practices',
    'Getting Started with Vue.js 3',
    'Database Optimization Techniques',
    'My Journey as a Developer',
    'Building REST APIs with Django',
    'JavaScript ES6+ Features',
    'Docker for Developers',
    'Machine Learning Basics',
    'Web Security Essentials',
    'CSS Grid Layout Guide',
    'Git Workflow Tips'
]

for i, base_title in enumerate(base_titles):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_title = f'{base_title}'
    slug = slugify(f'{unique_title}-{timestamp}-{i}')
    
    try:
        article = Article.objects.create(
            title=unique_title,
            slug=slug,
            content=f'<h2>{base_title}</h2><p>This is a comprehensive sample article about {base_title.lower()}.</p><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p><p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>',
            category=categories[0] if i < 8 else (categories[1] if len(categories) > 1 else categories[0]),
            status='Published',
            publish_on=datetime.now().date() - timedelta(days=i),
            created_by=admin_user,
            views=100 + i * 15,
            likes_count=10 + i * 2,
            comments_count=2 + i
        )
        article.tags.set(tags[i:i+2] if i+2 < len(tags) else tags[-2:])
        print(f'创建文章: {article.title}')
    except Exception as e:
        print(f'创建文章失败 {unique_title}: {e}')

print('\n示例数据创建完成！')
print(f'\n统计信息:')
print(f'分类数量: {Category.objects.count()}')
print(f'标签数量: {Tag.objects.count()}')
print(f'文章数量: {Article.objects.count()}')
