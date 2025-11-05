# Copyright (c) 2024, Innocent PM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cstr


class Category(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		category_name: DF.Data
		description: DF.Text | None
		icon: DF.Data | None
		image: DF.AttachImage | None
		is_active: DF.Check
		meta_description: DF.Text | None
		meta_keywords: DF.Text | None
		meta_title: DF.Data | None
		parent_category: DF.Link | None
		sort_order: DF.Int
	# end: auto-generated types

	def validate(self):
		"""Validate category data"""
		self.validate_parent_category()
		self.set_meta_title()

	def validate_parent_category(self):
		"""Ensure category doesn't reference itself as parent"""
		if self.parent_category == self.name:
			frappe.throw("Category cannot be its own parent")
		
		# Check for circular reference
		if self.parent_category:
			self.check_circular_reference(self.parent_category, [self.name])

	def check_circular_reference(self, parent_category, visited):
		"""Check for circular reference in category hierarchy"""
		if parent_category in visited:
			frappe.throw("Circular reference detected in category hierarchy")
		
		visited.append(parent_category)
		parent_doc = frappe.get_doc("Category", parent_category)
		if parent_doc.parent_category:
			self.check_circular_reference(parent_doc.parent_category, visited)

	def set_meta_title(self):
		"""Set meta title if not provided"""
		if not self.meta_title:
			self.meta_title = self.category_name

	def get_children(self):
		"""Get all child categories"""
		return frappe.get_all(
			"Category",
			filters={"parent_category": self.name, "is_active": 1},
			fields=["name", "category_name", "description", "icon", "image", "sort_order"],
			order_by="sort_order asc, category_name asc"
		)

	def get_all_descendant_categories(self):
		"""Get all descendant categories (recursive)"""
		children = []
		direct_children = self.get_children()
		
		for child in direct_children:
			children.append(child)
			child_doc = frappe.get_doc("Category", child.name)
			children.extend(child_doc.get_all_descendant_categories())
		
		return children

	def get_breadcrumbs(self):
		"""Get category breadcrumb trail"""
		breadcrumbs = []
		current = self
		
		while current:
			breadcrumbs.insert(0, {
				"name": current.name,
				"category_name": current.category_name
			})
			
			if current.parent_category:
				current = frappe.get_doc("Category", current.parent_category)
			else:
				current = None
		
		return breadcrumbs

	@staticmethod
	def get_category_tree():
		"""Get complete category tree structure"""
		categories = frappe.get_all(
			"Category",
			filters={"is_active": 1},
			fields=["name", "category_name", "parent_category", "icon", "image", "sort_order"],
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
		
		return root_categories

	@staticmethod
	def get_popular_categories(limit=10):
		"""Get popular categories based on listing count"""
		return frappe.db.sql("""
			SELECT 
				c.name,
				c.category_name,
				c.icon,
				c.image,
				COUNT(l.name) as listing_count
			FROM `tabCategory` c
			LEFT JOIN `tabListing` l ON l.category = c.name AND l.status = 'Active'
			WHERE c.is_active = 1
			GROUP BY c.name
			ORDER BY listing_count DESC, c.category_name ASC
			LIMIT %s
		""", (limit,), as_dict=True)

	def on_update(self):
		"""Clear cache when category is updated"""
		frappe.cache().delete_key("category_tree")
		frappe.cache().delete_key("popular_categories")

	def on_trash(self):
		"""Validate before deletion"""
		# Check if category has listings
		listing_count = frappe.db.count("Listing", {"category": self.name})
		if listing_count > 0:
			frappe.throw(f"Cannot delete category. It has {listing_count} listing(s) associated with it.")
		
		# Check if category has children
		children_count = frappe.db.count("Category", {"parent_category": self.name})
		if children_count > 0:
			frappe.throw(f"Cannot delete category. It has {children_count} child categor(ies).")
		
		# Clear cache
		frappe.cache().delete_key("category_tree")
		frappe.cache().delete_key("popular_categories")
