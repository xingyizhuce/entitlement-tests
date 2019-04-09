import json

def get_cdn_testing_skus():
    account_info = json.load(open("../../CDN/json/account_info_cdn.json"))

    sku_list = []

    for release in ["6", "7", "8"]:
        for pid in account_info[release].keys():
            sku_list.append(account_info[release][pid]["Stage"]["sku"])
            sku_list.append(account_info[release][pid]["Stage"]["base_sku"])

    uniq_sku_list = list(set(sku_list))

    sku_str = ""
    for sku in uniq_sku_list:
        sku_str += sku + ","

    print "Account name: entitlement_testing"
    print "SKUs for CDN testing got from account_info_cdn.json: ", sku_str

if __name__ == '__main__':
    get_cdn_testing_skus()
