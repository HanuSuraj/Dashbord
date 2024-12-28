from django.contrib import admin
from .models import Article, PayoutSetting, UserPayout


# Customize admin view for Article model
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "type", "published_at")
    search_fields = ("title", "author")
    list_filter = ("type", "published_at")
    ordering = ("-published_at",)


# Register PayoutSetting model
@admin.register(PayoutSetting)
class PayoutSettingAdmin(admin.ModelAdmin):
    list_display = ("payout_per_article",)


# Register UserPayout model
@admin.register(UserPayout)
class UserPayoutAdmin(admin.ModelAdmin):
    list_display = ("user", "total_articles", "total_payout")
    search_fields = ("user__username",)
