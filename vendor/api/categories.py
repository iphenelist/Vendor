# Copyright (c) 2024, Innocent PM and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint


@frappe.whitelist(allow_guest=True)
def get_category_tree():
	"""Get complete category tree structure"""
	try:
		categories = frappe.get_all(
			"Category",
			filters={"is_active": 1},
			fields=["name", "category_name", "parent_category", "icon", "image", "sort_order", "description"],
			order_by="sort_order asc, category_name asc"
		)
		
		# Build tree structure
		category_map = {}
		root_categories = []
		
		for category in categories:
			category["children"] = []
			category_map[category.name] = category
		
		for category in categories:
			if category.parent_category and category.parent_category in category_map:
				category_map[category.parent_category]["children"].append(category)
			else:
				root_categories.append(category)
		
		return {
			"success": True,
			"data": root_categories,
			"count": len(root_categories)
		}
	except Exception as e:
		frappe.log_error(f"Error in get_category_tree: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=True)
def get_popular_categories(limit=10):
	"""Get popular categories based on listing count"""
	try:
		limit = cint(limit)
		categories = frappe.db.sql("""
			SELECT 
				c.name,
				c.category_name,
				c.icon,
				c.image,
				c.description,
				COUNT(l.name) as listing_count
			FROM `tabCategory` c
			LEFT JOIN `tabListing` l ON l.category = c.name AND l.status = 'Active'
			WHERE c.is_active = 1
			GROUP BY c.name
			ORDER BY listing_count DESC, c.category_name ASC
			LIMIT %s
		""", (limit,), as_dict=True)
		
		return {
			"success": True,
			"data": categories,
			"count": len(categories)
		}
	except Exception as e:
		frappe.log_error(f"Error in get_popular_categories: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=True)
def get_all_categories():
	"""Get all active categories for dropdowns"""
	try:
		categories = frappe.get_all(
			"Category",
			filters={"is_active": 1},
			fields=["name", "category_name", "parent_category", "icon"],
			order_by="category_name asc"
		)
		
		return {
			"success": True,
			"data": categories,
			"count": len(categories)
		}
	except Exception as e:
		frappe.log_error(f"Error in get_all_categories: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=True)
def get_category_details(category_name):
	"""Get detailed information about a specific category"""
	try:
		category = frappe.get_doc("Category", category_name)
		
		# Get category statistics
		stats = frappe.db.sql("""
			SELECT 
				COUNT(*) as total_listings,
				COUNT(CASE WHEN status = 'Active' THEN 1 END) as active_listings,
				AVG(price) as avg_price,
				MIN(price) as min_price,
				MAX(price) as max_price
			FROM `tabListing`
			WHERE category = %s
		""", (category_name,), as_dict=True)[0]
		
		# Get breadcrumbs
		breadcrumbs = category.get_breadcrumbs()
		
		# Get child categories
		children = category.get_children()
		
		return {
			"success": True,
			"data": {
				"category": category.as_dict(),
				"stats": stats,
				"breadcrumbs": breadcrumbs,
				"children": children
			}
		}
	except Exception as e:
		frappe.log_error(f"Error in get_category_details: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=True)
def get_featured_categories(limit=6):
	"""Get featured categories for homepage display"""
	try:
		limit = cint(limit)
		
		# Get categories with most listings as featured
		categories = frappe.db.sql("""
			SELECT 
				c.name,
				c.category_name,
				c.icon,
				c.image,
				c.description,
				COUNT(l.name) as listing_count
			FROM `tabCategory` c
			LEFT JOIN `tabListing` l ON l.category = c.name AND l.status = 'Active'
			WHERE c.is_active = 1 AND c.parent_category IS NULL
			GROUP BY c.name
			HAVING listing_count > 0
			ORDER BY listing_count DESC, c.sort_order ASC
			LIMIT %s
		""", (limit,), as_dict=True)
		
		return {
			"success": True,
			"data": categories,
			"count": len(categories)
		}
	except Exception as e:
		frappe.log_error(f"Error in get_featured_categories: {str(e)}")
		return {"success": False, "error": str(e)}
