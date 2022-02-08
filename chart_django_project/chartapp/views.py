from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from .forms import ChartForm


def index(request):

    form = ChartForm(request.POST or None)
    chart = None
    if request.method == "POST":
        form = ChartForm(request.POST)
        if form.is_valid():
            chart = form.cleaned_data['chart']
            print(chart)

    my_data = parse()
    context = {
        "accounts": my_data[0],
        "balance": my_data[1],
        "form": form,
        "chart": chart
    }
    return render(request, 'chartapp/index.html', context)


def parse():
    # ------------- URL and HEADERS -------------
    URL = 'https://etherscan.io/accounts/1?ps=100'
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36",
        "accept": "*/*"}

    # ------------- REQUEST TO A WEBSITE -------------
    r = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')

    # ------------- FINDING TABLE WITH ACCOUNTS -------------
    address_table = soup.find('table', class_='table table-hover')
    addresses = []

    for address in address_table.find_all('tbody'):
        rows = address.find_all('tr')
        for row in rows:
            url = row.find('a').get('href')
            addresses.append(url.replace("/address/", ""))

    # ------------- SPLITTING OF ADDRESSES TO 5 EQUALLY LIKELY CHUNKS -------------
    chunked_list = list()
    chunk_size = 20
    for i in range(0, len(addresses), chunk_size):
        chunked_list.append(addresses[i:i + chunk_size])

    api_request = []
    for item in chunked_list:
        temp = []
        for i in item:
            temp.append(i)
        api_request.append('https://api.etherscan.io/api?module=account&action=balancemulti&address=' + ','.join(
            temp) + '&tag=latest&apikey=CDCEENVDX4YPI9YNRUHC2WHXKMWQDHR2F2')
        temp = []

    # ------------- CHECKING CHUNKS -------------
    print(len(api_request))

    print(list(requests.get(api_request[0]).json()))

    # ------------- PARSING INFORMATION FROM JSON -------------
    top_accounts = []
    for i in api_request:
        temp = requests.get(i).json()['result']
        for j in temp:
            top_accounts.append(j)

    # ------------- SORTING THE PARSER INFORMATION (ACCOUNTS - BALANCE)
    my_data = [[], []]
    for item in top_accounts:
        if 'account' in item:
            my_data[0].append(item['account'])

        if 'balance' in item:
            my_data[1].append(int(item['balance'])/(10**18))

    # ------------- RETURNING RESULT -------------
    return my_data
