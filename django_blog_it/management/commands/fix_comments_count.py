from django.core.management.base import BaseCommand
from django_blog_it.models import Article


class Command(BaseCommand):
    help = 'Fix comments count for all articles'

    def handle(self, *args, **kwargs):
        articles = Article.objects.all()
        fixed_count = 0

        for article in articles:
            # 计算实际的父评论数量（不包括回复）
            actual_count = article.comments.filter(parent=None, is_active=True).count()

            if article.comments_count != actual_count:
                article.comments_count = actual_count
                article.save(update_fields=['comments_count'])
                fixed_count += 1
                self.stdout.write(
                    f'Fixed article "{article.title}": {article.comments_count} -> {actual_count}'
                )

        self.stdout.write(self.style.SUCCESS(f'Successfully fixed {fixed_count} articles'))
