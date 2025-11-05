# Copyright (c) 2024, Innocent PM and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate, nowdate
import json


@frappe.whitelist(allow_guest=True)
def get_featured_listings(limit=10):
	"""Get featured listings for homepage"""
	try:
		limit = cint(limit)
		listings = frappe.db.sql("""
			SELECT 
				l.name,
				l.title,
				l.description,
				l.price,
				l.currency,
				l.location,
				l.category,
				l.condition,
				l.listing_type,
				l.views_count,
				l.creation,
				c.category_name,
				c.icon as category_icon,
				(SELECT li.image FROM `tabListing Image` li 
				 WHERE li.parent = l.name AND li.is_primary = 1 
				 ORDER BY li.sort_order ASC LIMIT 1) as primary_image,
				(SELECT COUNT(*) FROM `tabListing Image` li 
				 WHERE li.parent = l.name) as image_count
			FROM `tabListing` l
			LEFT JOIN `tabCategory` c ON l.category = c.name
			WHERE l.status = 'Active' 
				AND l.featured = 1 
				AND l.expires_on >= %s
			ORDER BY l.creation DESC
			LIMIT %s
		""", (nowdate(), limit), as_dict=True)
		
		return {
			"success": True,
			"data": listings,
			"count": len(listings)
		}
	except Exception as e:
		frappe.log_error(f"Error in get_featured_listings: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=True)
def get_listings_by_category(category, limit=20, offset=0, filters=None):
	"""Get listings by category with optional filters"""
	try:
		limit = cint(limit)
		offset = cint(offset)
		
		conditions = ["l.status = 'Active'", "l.expires_on >= %s"]
		values = [nowdate()]
		
		if category and category != "all":
			conditions.append("l.category = %s")
			values.append(category)
		
		# Parse filters if provided
		if filters:
			if isinstance(filters, str):
				filters = json.loads(filters)
			
			if filters.get('min_price'):
				conditions.append("l.price >= %s")
				values.append(flt(filters['min_price']))
			
			if filters.get('max_price'):
				conditions.append("l.price <= %s")
				values.append(flt(filters['max_price']))
			
			if filters.get('condition'):
				conditions.append("l.condition = %s")
				values.append(filters['condition'])
			
			if filters.get('listing_type'):
				conditions.append("l.listing_type = %s")
				values.append(filters['listing_type'])
			
			if filters.get('location'):
				conditions.append("l.location LIKE %s")
				values.append(f"%{filters['location']}%")
		
		where_clause = " AND ".join(conditions)
		
		listings = frappe.db.sql(f"""
			SELECT 
				l.name,
				l.title,
				l.description,
				l.price,
				l.currency,
				l.location,
				l.category,
				l.condition,
				l.listing_type,
				l.views_count,
				l.creation,
				l.featured,
				c.category_name,
				c.icon as category_icon,
				(SELECT li.image FROM `tabListing Image` li 
				 WHERE li.parent = l.name AND li.is_primary = 1 
				 ORDER BY li.sort_order ASC LIMIT 1) as primary_image,
				(SELECT COUNT(*) FROM `tabListing Image` li 
				 WHERE li.parent = l.name) as image_count
			FROM `tabListing` l
			LEFT JOIN `tabCategory` c ON l.category = c.name
			WHERE {where_clause}
			ORDER BY l.featured DESC, l.creation DESC
			LIMIT %s OFFSET %s
		""", values + [limit, offset], as_dict=True)
		
		# Get total count for pagination
		total_count = frappe.db.sql(f"""
			SELECT COUNT(*) as count
			FROM `tabListing` l
			WHERE {where_clause}
		""", values, as_dict=True)[0].count
		
		return {
			"success": True,
			"data": listings,
			"count": len(listings),
			"total": total_count,
			"has_more": (offset + limit) < total_count
		}
	except Exception as e:
		frappe.log_error(f"Error in get_listings_by_category: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=True)
def search_listings(query, limit=20, offset=0, filters=None):
	"""Search listings by title and description"""
	try:
		limit = cint(limit)
		offset = cint(offset)
		
		conditions = ["l.status = 'Active'", "l.expires_on >= %s"]
		values = [nowdate()]
		
		if query:
			conditions.append("(l.title LIKE %s OR l.description LIKE %s)")
			search_term = f"%{query}%"
			values.extend([search_term, search_term])
		
		# Apply additional filters
		if filters:
			if isinstance(filters, str):
				filters = json.loads(filters)
			
			if filters.get('category'):
				conditions.append("l.category = %s")
				values.append(filters['category'])
			
			if filters.get('min_price'):
				conditions.append("l.price >= %s")
				values.append(flt(filters['min_price']))
			
			if filters.get('max_price'):
				conditions.append("l.price <= %s")
				values.append(flt(filters['max_price']))
		
		where_clause = " AND ".join(conditions)
		
		listings = frappe.db.sql(f"""
			SELECT 
				l.name,
				l.title,
				l.description,
				l.price,
				l.currency,
				l.location,
				l.category,
				l.condition,
				l.listing_type,
				l.views_count,
				l.creation,
				c.category_name,
				c.icon as category_icon,
				(SELECT li.image FROM `tabListing Image` li 
				 WHERE li.parent = l.name AND li.is_primary = 1 
				 ORDER BY li.sort_order ASC LIMIT 1) as primary_image
			FROM `tabListing` l
			LEFT JOIN `tabCategory` c ON l.category = c.name
			WHERE {where_clause}
			ORDER BY l.featured DESC, l.creation DESC
			LIMIT %s OFFSET %s
		""", values + [limit, offset], as_dict=True)
		
		return {
			"success": True,
			"data": listings,
			"count": len(listings),
			"query": query
		}
	except Exception as e:
		frappe.log_error(f"Error in search_listings: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=True)
def get_listing_details(listing_id):
	"""Get detailed information about a specific listing"""
	try:
		listing = frappe.db.sql("""
			SELECT 
				l.*,
				c.category_name,
				c.icon as category_icon,
				u.full_name as seller_name,
				up.phone_number as seller_phone,
				up.whatsapp_number as seller_whatsapp,
				up.location as seller_location,
				up.profile_image as seller_image,
				up.rating as seller_rating,
				up.total_ratings as seller_total_ratings
			FROM `tabListing` l
			LEFT JOIN `tabCategory` c ON l.category = c.name
			LEFT JOIN `tabUser` u ON l.created_by_user = u.name
			LEFT JOIN `tabUser Profile` up ON l.created_by_user = up.user
			WHERE l.name = %s AND l.status = 'Active'
		""", (listing_id,), as_dict=True)
		
		if not listing:
			return {"success": False, "error": "Listing not found"}
		
		listing = listing[0]
		
		# Get listing images
		images = frappe.get_all(
			"Listing Image",
			filters={"parent": listing_id},
			fields=["image", "is_primary", "sort_order"],
			order_by="is_primary DESC, sort_order ASC"
		)
		
		listing["images"] = images
		
		return {
			"success": True,
			"data": listing
		}
	except Exception as e:
		frappe.log_error(f"Error in get_listing_details: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def increment_views(listing_id):
	"""Increment view count for a listing"""
	try:
		frappe.db.sql("""
			UPDATE `tabListing` 
			SET views_count = COALESCE(views_count, 0) + 1 
			WHERE name = %s
		""", (listing_id,))
		frappe.db.commit()
		
		return {"success": True}
	except Exception as e:
		frappe.log_error(f"Error in increment_views: {str(e)}")
		return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=True)
def get_top_selling_listings(limit=10):
	"""Get top selling listings based on views"""
	try:
		limit = cint(limit)
		listings = frappe.db.sql("""
			SELECT 
				l.name,
				l.title,
				l.price,
				l.currency,
				l.category,
				l.views_count,
				c.category_name,
				(SELECT li.image FROM `tabListing Image` li 
				 WHERE li.parent = l.name AND li.is_primary = 1 
				 ORDER BY li.sort_order ASC LIMIT 1) as primary_image
			FROM `tabListing` l
			LEFT JOIN `tabCategory` c ON l.category = c.name
			WHERE l.status = 'Active' 
				AND l.expires_on >= %s
			ORDER BY l.views_count DESC, l.creation DESC
			LIMIT %s
		""", (nowdate(), limit), as_dict=True)
		
		return {
			"success": True,
			"data": listings,
			"count": len(listings)
		}
	except Exception as e:
		frappe.log_error(f"Error in get_top_selling_listings: {str(e)}")
		return {"success": False, "error": str(e)}
