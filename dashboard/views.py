import requests
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.views import View
from dashboard.models import Article, PayoutSetting, UserPayout
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Article


# Login and Logout views
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already taken"})

        user = User.objects.create_user(
            username=username, password=password, email=email
        )
        login(request, user)
        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(
                request, "login.html", {"error": "Invalid username or password"}
            )

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


class FetchNewsView(View):
    def get(self, request):
        API_URL = "https://newsapi.org/v2/top-headlines"
        API_KEY = "1786c16917524312b47812f89dc7300e"  # Replace with your actual API key

        params = {
            "country": "us",
            "apiKey": API_KEY,
        }

        response = requests.get(API_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            for article_data in data.get("articles", []):
                # Handle missing author gracefully
                author_name = article_data.get("author") or "Unknown"
                published_at = article_data.get("publishedAt") or "2024-01-01"
                url_to_image = article_data.get("urlToImage") or ""

                # Create or update the article
                Article.objects.get_or_create(
                    title=article_data["title"],
                    defaults={
                        "author": author_name,
                        "published_at": published_at,
                        "type": "news",
                        "url": article_data.get("url", ""),
                        "url_to_image": url_to_image,
                    },
                )

        # Fetch all articles and paginate them
        articles = Article.objects.all()
        paginator = Paginator(articles, 14)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, "dashboard/fetch_articles.html", {"page_obj": page_obj})


# Admin-only view to set payout per article
class SetPayoutView(APIView):
    permission_classes = [IsAuthenticated]

    # Handle GET request to retrieve current payout per article
    def get(self, request):
        payout_setting = PayoutSetting.objects.first()
        if payout_setting:
            return Response({"payout_per_article": payout_setting.payout_per_article})
        else:
            return Response({"error": "No payout setting found"}, status=404)

    # Handle POST request to set payout per article
    def post(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Unauthorized"}, status=403)

        payout_per_article = request.data.get("payout_per_article")

        if not payout_per_article:
            return Response({"error": "Payout value is required"}, status=400)

        payout_setting, created = PayoutSetting.objects.get_or_create(id=1)
        payout_setting.payout_per_article = payout_per_article
        payout_setting.save()

        return Response({"message": "Payout per article updated successfully!"})


# Export PDF function
@api_view(["GET"])
def export_pdf(request):
    user = request.user
    user_payout = UserPayout.objects.filter(user=user).first()

    if not user_payout:
        return Response({"error": "No payout data found"}, status=404)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, f"User: {user.username}")
    p.drawString(100, 730, f"Total Articles: {user_payout.total_articles}")
    p.drawString(100, 710, f"Total Payout: ${user_payout.total_payout}")
    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")


# Export CSV function
@api_view(["GET"])
def export_csv(request):
    user = request.user
    user_payout = UserPayout.objects.filter(user=user).first()

    if not user_payout:
        return Response({"error": "No payout data found"}, status=404)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="payout_report.csv"'

    writer = csv.writer(response)
    writer.writerow(["Username", "Total Articles", "Total Payout"])
    writer.writerow(
        [user.username, user_payout.total_articles, user_payout.total_payout]
    )

    return response


# Export to Google Sheets function
@api_view(["GET"])
def export_google_sheets(request):
    user = request.user
    user_payout = UserPayout.objects.filter(user=user).first()

    if not user_payout:
        return Response({"error": "No payout data found"}, status=404)

    try:
        # Google Sheets API setup
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "your_credentials_file.json", scope
        )
        client = gspread.authorize(creds)

        # Open a worksheet
        sheet = client.open("Payout Reports").sheet1
        row = [user.username, user_payout.total_articles, user_payout.total_payout]
        sheet.append_row(row)

        return Response({"message": "Exported to Google Sheets successfully!"})

    except Exception as e:
        return Response(
            {"error": f"Failed to export to Google Sheets: {str(e)}"}, status=500
        )


# Dashboard view class
class DashboardView(View):
    def get(self, request, *args, **kwargs):
        # Get the current user
        user = request.user

        # Get the total number of articles
        total_articles = Article.objects.filter(user=user).count()

        # Get the user payout information
        user_payout = UserPayout.objects.filter(user=user).first()

        # Calculate total payout if user payout exists, otherwise set to 0
        total_payout = 0.0
        if user_payout:
            total_payout = user_payout.total_payout

        # Get the current payout setting
        payout_setting = PayoutSetting.objects.first()

        context = {
            "message": "Welcome to the Dashboard!",
            "total_articles": total_articles,  # Pass the total articles to the template
            "total_payout": total_payout,  # Pass the total payout to the template
            "payout_per_article": (
                payout_setting.payout_per_article if payout_setting else "Not set"
            ),
        }
        return render(request, "dashboard/dashboard.html", context)
