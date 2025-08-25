import frappe
import requests

def initiate_login(email, password):
	url = "http://192.168.1.16:8000/api/method/login?usr={}&pwd={}".format(email, password)
	response = requests.request("POST", url)
	if response.status_code == 200:
		frappe.cache().hset("cookies", email, response.cookies)
	return response.cookies

def get_cookies(email, password):
	cookies = frappe.cache().hget("cookies", email)
	if cookies:
		return cookies
	else:
		return initiate_login(email, password)
	
def post_request(url, payload=None, bpcl_docname=None):
    headers = {"Content-Type": "application/json"}
    bpcl = frappe.get_doc("BPCL", bpcl_docname)
    cookies = get_cookies(bpcl.email, bpcl.password)  

    res = requests.post(url, json=payload, headers=headers, cookies=cookies)

    if res.status_code in (401, 403):
        print("Session expired, initiating login again")
        cookies = initiate_login(bpcl.email, bpcl.password)
        frappe.cache().hset("cookies", bpcl.email, cookies)
        res = requests.post(url, json=payload, headers=headers, cookies=cookies)
    return res