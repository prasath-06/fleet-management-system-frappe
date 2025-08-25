import frappe
import requests
import json
from travel_tracks.travel_tracks.session_handler import post_request

from frappe.model.document import Document

class BPCL(Document):
	pass


@frappe.whitelist()
def registration(company_name, email, phone):
    url = "http://192.168.1.38:8000/api/method/fm.fuel_management.api.onboard_transport_company"
    data = {"company_name": company_name, "email": email, "phone": phone}
    res = requests.post(url, json=data)

    if res.status_code == 200:
        response_data = res.json().get("message", {})
        print("Raw Response:", response_data)

        bpcl_doc = frappe.new_doc("BPCL")
        bpcl_doc.company_name = company_name
        bpcl_doc.email = email
        bpcl_doc.phone = phone
        bpcl_doc.password = response_data.get("password")
        bpcl_doc.company_id = response_data.get("company_id")
        bpcl_doc.wallet_id = response_data.get("wallet_id")
        bpcl_doc.insert()

        company_doc = frappe.new_doc("Company")
        company_doc.company_name = company_name
        company_doc.default_currency = "INR"
        company_doc.company_abbr = company_name[:3].upper()
        company_doc.insert()

        return {
            "message": "Details sent to bunk company successfully!",
        }
    else:
        return {"message": f"Failed: {res.status_code} {res.text}"}

@frappe.whitelist()
def add_vehicles(vehicles=None, bpcl_docname=None):
	if not vehicles or not bpcl_docname:
		return "Missing vehicles or document name."
	else:
		vehicles = frappe.parse_json(vehicles)
		url = "http://192.168.1.16:8000/api/method/fm.fuel_management.api.create_fleet_card"
		bpcl = frappe.get_doc("BPCL", bpcl_docname)
		company_id = bpcl.company_id
		success= 0
		failure= 0
		for vehicle in vehicles:
			payload = {
				"company_id": company_id,"vehicle_list": [vehicle.get("vehicle_details")]
				}	
			res = post_request(url, payload, bpcl_docname=bpcl.name)			
			if res.status_code == 200:
				res_json = res.json().get("message", {})

				if res_json.get("status") == "success":
					api_vehicle_list = res_json.get("card_details", [])			
					for vehicle in api_vehicle_list:
						bpcl.append("vehicle", {
							"vehicles": vehicle.get("vehicle_no"),
							"card": vehicle.get("card_no"),
							"pin": vehicle.get("pin"),
						})
					success += 1
				else:
					failure+=1
			else:
				failure+= 1
				frappe.msgprint(f"HTTP Error {res.status_code}: {res.text}")

		bpcl.save(ignore_permissions=True)
		frappe.db.commit()

		return {
			"message": f"{success} vehicle(s) added, {failure} failed."
		}

@frappe.whitelist()
def update_vehicle_pins(vehicle=None, bpcl_docname=None):

	vehicles = frappe.parse_json(vehicle)
	bpcl = frappe.get_doc("BPCL", bpcl_docname)
	url = "http://192.168.1.16:8000/api/method/fm.fuel_management.api.change_card_pin"
	success = 0
	failure = 0
	for v in vehicles:
		card_no = v.get("card")  
		new_pin = v.get("pin")
		old_pin = 0
		for row in bpcl.vehicle:  
			if row.card == card_no:
				old_pin = row.pin
				break
		payload = {
			"card_no": card_no,
			"old_pin": old_pin,
			"new_pin": new_pin
		}
		res = post_request(url, payload, bpcl_docname=bpcl.name)
		frappe.log_error(f"Response: {res.text}", "Update Vehicle Pins")

		if res.status_code == 200:
			for row in bpcl.vehicle:
				if row.card == card_no:
					row.pin = new_pin
					break
			success += 1
		else:
			failure += 1
	bpcl.save(ignore_permissions=True)
	frappe.db.commit()
	return {
		"message": f"{success} PIN(s) updated, {failure} failed."
	}


