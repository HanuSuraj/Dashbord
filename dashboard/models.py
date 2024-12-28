from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


# Model to store Articles with an inline author name
class Article(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(
        max_length=255, default="Unknown"
    )  # Author stored as a string
    published_at = models.DateTimeField(default=now)  # Use `now` for default datetime
    type = models.CharField(
        max_length=50,
        default="news",
        choices=[
            ("news", "News"),
            ("blog", "Blog"),
            ("report", "Report"),
        ],
    )  # Added choices for better validation
    url = models.URLField(max_length=1024, blank=True, null=True)
    url_to_image = models.URLField(max_length=1024, blank=True, null=True)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["-published_at"]  # Default order by published date, descending

    def __str__(self):
        return self.title


# Model to store Payout per article/blog
class PayoutSetting(models.Model):
    payout_per_article = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Payout Setting"
        verbose_name_plural = "Payout Settings"

    def __str__(self):
        return f"Payout: {self.payout_per_article} per article"

    def save(self, *args, **kwargs):
        # Ensure only one PayoutSetting instance exists
        if not self.pk and PayoutSetting.objects.exists():
            raise ValueError("Only one PayoutSetting instance can exist.")
        super().save(*args, **kwargs)


# Model to store User payouts (for calculating total)
class UserPayout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_articles = models.PositiveIntegerField(
        default=0
    )  # Use `PositiveIntegerField` for counts
    total_payout = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0
    )  # Store payout in decimal format

    def update_payout(self):
        payout_setting = PayoutSetting.objects.first()
        if payout_setting:
            self.total_payout = self.total_articles * payout_setting.payout_per_article
            self.save()

    def __str__(self):
        return f"{self.user.username}'s Payout"
