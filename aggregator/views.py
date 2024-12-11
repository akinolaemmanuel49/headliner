from django.shortcuts import render
from django.core.paginator import Paginator
from utils.headliner import bbcnews_headlines, headlines, nbcnews_headlines

def index(request):
    # Fetch headlines from sources
    sources = [nbcnews_headlines(), bbcnews_headlines()]
    aggregated = headlines(sources)

    # Add pagination for each network
    paginated_headlines = {}
    for network, network_headlines in aggregated.items():
        paginator = Paginator(network_headlines, 5)  # 5 headlines per page
        page_number = request.GET.get(f"{network}_page", 1)  # Get page number for this specific network
        page_obj = paginator.get_page(page_number)
        paginated_headlines[network] = page_obj

    return render(
        request,
        "aggregator/index.html",
        {"paginated_headlines": paginated_headlines},
    )

def search(request):
    # 
    pass