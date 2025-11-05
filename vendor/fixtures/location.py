import frappe


def execute():
	"""Add or update Tanzania locations in the Location doctype."""

	tanzania_locations = [
		{"location": "Arusha", "latitude": -3.37, "longitude": 36.68},
		{"location": "Dar es Salaam", "latitude": -6.82, "longitude": 39.27},
		{"location": "Dodoma", "latitude": -6.16, "longitude": 35.75},
		{"location": "Geita", "latitude": -2.87, "longitude": 32.23},
		{"location": "Iringa", "latitude": -7.77, "longitude": 35.7},
		{"location": "Kagera", "latitude": -1.33, "longitude": 31.82},
		{"location": "Katavi", "latitude": -6.34, "longitude": 31.07},
		{"location": "Kigoma", "latitude": -4.88, "longitude": 29.63},
		{"location": "Kilimanjaro", "latitude": -3.33, "longitude": 37.34},
		{"location": "Lindi", "latitude": -9.99, "longitude": 39.72},
		{"location": "Manyara", "latitude": -4.22, "longitude": 35.75},
		{"location": "Mara", "latitude": -1.5, "longitude": 33.8},
		{"location": "Mbeya", "latitude": -8.9, "longitude": 33.45},
		{"location": "Mjini Magharibi", "latitude": -6.16, "longitude": 39.2},
		{"location": "Morogoro", "latitude": -6.82, "longitude": 37.67},
		{"location": "Mtwara", "latitude": -10.27, "longitude": 40.18},
		{"location": "Mwanza", "latitude": -2.52, "longitude": 32.9},
		{"location": "Njombe", "latitude": -9.33, "longitude": 34.77},
		{"location": "Pemba North", "latitude": -5.06, "longitude": 39.72},
		{"location": "Pemba South", "latitude": -5.25, "longitude": 39.77},
		{"location": "Pwani", "latitude": -6.77, "longitude": 38.92},
		{"location": "Rukwa", "latitude": -7.97, "longitude": 31.62},
		{"location": "Ruvuma", "latitude": -10.68, "longitude": 35.65},
		{"location": "Shinyanga", "latitude": -3.66, "longitude": 33.42},
		{"location": "Simiyu", "latitude": -2.8, "longitude": 33.98},
		{"location": "Singida", "latitude": -4.82, "longitude": 34.75},
		{"location": "Songwe", "latitude": -9.27, "longitude": 33.42},
		{"location": "Tabora", "latitude": -5.02, "longitude": 32.8},
		{"location": "Tanga", "latitude": -5.07, "longitude": 39.1},
		{"location": "Unguja North", "latitude": -5.88, "longitude": 39.25},
		{"location": "Unguja South", "latitude": -6.13, "longitude": 39.35},
	]

	added, updated, failed = [], [], []
	logger = frappe.logger("tanzania_locations_patch")

	try:
		frappe.db.savepoint("before_tanzania_locations")

		for loc in tanzania_locations:
			name = loc["location"]
			lat, lon = loc["latitude"], loc["longitude"]

			try:
				if frappe.db.exists("Location", name):
					# Update coordinates if changed
					location_doc = frappe.get_doc("Location", name)
					if location_doc.latitude != lat or location_doc.longitude != lon:
						location_doc.latitude = lat
						location_doc.longitude = lon
						location_doc.save(ignore_permissions=True)
						updated.append(name)
				else:
					# Create new location
					location_doc = frappe.new_doc("Location")
					location_doc.location = name  # Correct fieldname
					location_doc.latitude = lat
					location_doc.longitude = lon
					location_doc.insert(ignore_permissions=True)
					added.append(name)
			except Exception as e:
				failed.append({"name": name, "error": str(e)})
				logger.error(f"Failed to process {name}: {e}")

		frappe.db.commit()

		summary = f"Locations installed: ✅ Added: {len(added)}, 🔄 Updated: {len(updated)}, ❌ Failed: {len(failed)}"
		logger.info(f"Tanzania locations patch complete. {summary}")
		print(summary)

	except Exception as err:
		frappe.db.rollback(save_point="before_tanzania_locations")
		logger.error(f"Patch failed entirely: {err}")
		raise
