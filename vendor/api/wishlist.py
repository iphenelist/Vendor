# Copyright (c) 2024, Innocent PM and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate


@frappe.whitelist()
def add_to_wishlist(listing_id, notes=None):
	"""Add a listing to user's wishlist"""
	try:
		user = frappe.session.user
		if user == "Guest":
			return {"success": False, "error": "Please login to add items to wishlist"}
		
		# Check if already in wishlist
		existing = frappe.db.exists("Wishlist", {
			"user": user,
			"listing": listing_id
		})
		
		if existing:
			return {"success": False, "error": "Item already in wishlist"}
		
		# Create wishlist entry
		wishlist_doc = frappe.get_doc({
			"doctype": "Wishlist",
			"user": user,
			"listing": listing_id,
			"added_date": frappe.utils.now(),
			"notes": notes
		})
		wishlist_doc.insert()
		
		return {
			"success": True,
			"message": "Item added to wishlist",
			"wishlist_id": wishlist_doc.name
		}
	except Exception as e:
		frappe.log_error(f"Error in add_to_wishlist: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def remove_from_wishlist(listing_id):
	"""Remove a listing from user's wishlist"""
	try:
		user = frappe.session.user
		if user == "Guest":
			return {"success": False, "error": "Please login to manage wishlist"}
		
		wishlist_item = frappe.db.get_value("Wishlist", {
			"user": user,
			"listing": listing_id
		}, "name")
		
		if not wishlist_item:
			return {"success": False, "error": "Item not found in wishlist"}
		
		frappe.delete_doc("Wishlist", wishlist_item)
		
		return {
			"success": True,
			"message": "Item removed from wishlist"
		}
	except Exception as e:
		frappe.log_error(f"Error in remove_from_wishlist: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_user_wishlist(limit=50, offset=0):
	"""Get user's wishlist items"""
	try:
		user = frappe.session.user
		if user == "Guest":
			return {"success": False, "error": "Please login to view wishlist"}
		
		wishlist_items = frappe.db.sql("""
			SELECT 
				w.name as wishlist_id,
				w.added_date,
				w.notes,
				l.name as listing_id,
				l.title,
				l.price,
				l.currency,
				l.location,
				l.category,
				l.status,
				c.category_name,
				(SELECT li.image FROM `tabListing Image` li 
				 WHERE li.parent = l.name AND li.is_primary = 1 
				 ORDER BY li.sort_order ASC LIMIT 1) as primary_image
			FROM `tabWishlist` w
			LEFT JOIN `tabListing` l ON w.listing = l.name
			LEFT JOIN `tabCategory` c ON l.category = c.name
			WHERE w.user = %s
			ORDER BY w.added_date DESC
			LIMIT %s OFFSET %s
		""", (user, limit, offset), as_dict=True)
		
		# Get total count
		total_count = frappe.db.count("Wishlist", {"user": user})
		
		return {
			"success": True,
			"data": wishlist_items,
			"count": len(wishlist_items),
			"total": total_count
		}
	except Exception as e:
		frappe.log_error(f"Error in get_user_wishlist: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_wishlist_count():
	"""Get count of items in user's wishlist"""
	try:
		user = frappe.session.user
		if user == "Guest":
			return {"success": True, "count": 0}
		
		count = frappe.db.count("Wishlist", {"user": user})
		
		return {
			"success": True,
			"count": count
		}
	except Exception as e:
		frappe.log_error(f"Error in get_wishlist_count: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def check_wishlist_status(listing_id):
	"""Check if a listing is in user's wishlist"""
	try:
		user = frappe.session.user
		if user == "Guest":
			return {"success": True, "in_wishlist": False}
		
		exists = frappe.db.exists("Wishlist", {
			"user": user,
			"listing": listing_id
		})
		
		return {
			"success": True,
			"in_wishlist": bool(exists)
		}
	except Exception as e:
		frappe.log_error(f"Error in check_wishlist_status: {str(e)}")
		return {"success": False, "error": str(e)}
