from django.shortcuts import render
from django.core.paginator import Paginator
from utils.headliner import bbcnews_headlines, headlines, nbcnews_headlines


def index(request):
    # Fetch headlines from sources
    sources = [nbcnews_headlines(), bbcnews_headlines()]
    aggregated = headlines(sources)

    # Get search and filter parameters from request
    search_query = request.GET.get("search", "").strip()
    selected_network = request.GET.get("network", "").strip()

    # Filter headlines by network and search query
    filtered_headlines = {}
    for network, network_headlines in aggregated.items():
        # Skip networks if a specific one is selected and doesn't match
        if selected_network and network.lower() != selected_network:
            continue

        # Filter headlines by search query if present
        if search_query:
            network_headlines = [
                headline
                for headline in network_headlines
                if search_query.lower() in headline["text"].lower()
            ]

        # Add the filtered headlines to the results
        filtered_headlines[network] = network_headlines

    # Add pagination for each network
    paginated_headlines = {}
    for network, network_headlines in filtered_headlines.items():
        paginator = Paginator(network_headlines, 5)  # 5 headlines per page
        page_number = request.GET.get(
            f"{network}_page", 1
        )  # Get page number for this network
        page_obj = paginator.get_page(page_number)
        paginated_headlines[network] = page_obj

    return render(
        request,
        "aggregator/index.html",
        {
            "paginated_headlines": paginated_headlines,
            "search_query": search_query,
            "selected_network": selected_network,
        },
    )
