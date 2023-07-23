import requests

# See details about WITS (electricityinfo.co.nz) API at https://developer.electricityinfo.co.nz/

# Before starting you need to 'Sign Up' at https://developer.electricityinfo.co.nz/WITS/register
# Then click on 'My Apps'
# Create a new application called anything, i.e 'homeassistant'
# Enter anything for Redirect URI, such as 'https://google.com'
# Click 'Generate Credential'
# Save your Client ID and Client Secret
# You also need to enable appropriate services, i.e Pricing_API_Application_Registration

def get_access_token(client_id, client_secret):


    url = "https://api.electricityinfo.co.nz/login/oauth2/token"

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    data = {"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret}

    r = requests.post(url, headers=headers, data=data)

    response = r.json()
    return response['access_token']


def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results


def get_spot_price(access_token, schedule, marketType, node, back):
    url = 'https://api.electricityinfo.co.nz/api/market-prices/v1/schedules/' + schedule + '/prices?marketType=' + marketType + '&nodes=' + node + '&back=' + str(back) + '&offset=0'

    headers = {'Authorization': 'Bearer '+ access_token}

    r = requests.get(url, headers=headers)
    response_temp = r.json()
    return (extract_values(response_temp, 'price'), extract_values(response_temp, 'tradingDateTime'))


client_id = input ("Enter Client ID: ")
client_secret = input ("Enter Client Secret: ")


access_token = (get_access_token(client_id, client_secret))

schedule = ""
marketType = ""
node = ""
back = ""
exit_time = 0
while exit_time == 0:

    #Future: call https://api.electricityinfo.co.nz/api/market-prices/v1/schedules to retrieve a list of schedules and then iterate through the list to find each runType and marketType for the possible schedules, then offer these as options in the inputs below.

    schedule_input = input ("Enter required schedule (i.e Final, Interim, NRSL, NRSS, PRSL, PRSS, RTD, WDS): " + schedule +" ")
    marketType_input = input ("Enter required Market Type ('E' for Energy or 'R' for Reserves): " + marketType +" ")
    node_input = input ("Enter node: Find this on electricityinfo.co.nz: " + node +" ")
    back_input = input ("Enter a number for how many trading periods back you want to go (0-72):" + str(back) +" ")

    if schedule_input.upper() == "INTERIM":
        schedule = "Interim"
    elif schedule_input.upper() == "FINAL":
        schedule = "Final"
    elif schedule_input != "":
        schedule = schedule_input.upper()

    if marketType_input != "":
        marketType = marketType_input.upper()

    if node_input != "":
        node = node_input.upper()

    if back_input == "0":
        back = ""
    elif back_input != "":
        back = int(back_input)

    prices = get_spot_price(access_token, schedule, marketType, node, back)

    print(prices)
    exit_time = input ("Enter 1 to exit or hit Enter to continue: ")
    if exit_time == "":
        exit_time = 0
    else: exit_time = 1
