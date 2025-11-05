# Copyright (c) 2024, Innocent PM and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class Listing(WebsiteGenerator):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address: DF.SmallText | None
		approved_by: DF.Link | None
		approved_on: DF.Datetime | None
		category: DF.Link | None
		condition: DF.Literal["New", "Used", "Refurbished"]
		contact_email: DF.Data | None
		contact_phone: DF.Data | None
		contact_whatsapp: DF.Data | None
		created_by_user: DF.Link | None
		currency: DF.Link | None
		description: DF.LongText | None
		expires_on: DF.Date | None
		featured: DF.Check
		latitude: DF.Float
		listing_type: DF.Literal["For Sale", "For Rent", "Service", "Job"]
		location: DF.Data | None
		longitude: DF.Float
		meta_description: DF.Text | None
		meta_keywords: DF.Text | None
		meta_title: DF.Data | None
		naming_series: DF.Select | None
		price: DF.Currency
		show_contact_info: DF.Check
		status: DF.Literal["Draft", "Active", "Sold", "Expired", "Rejected"]
		title: DF.Data
		views_count: DF.Int
	# end: auto-generated types

	def before_insert(self):
		"""Set default values before inserting"""
		self.created_by_user = frappe.session.user
		self.set_default_expiry()
		self.set_default_contact_info()

	def validate(self):
		"""Validate listing data"""
		self.validate_contact_info()
		self.validate_price()
		self.validate_expiry_date()
		self.set_meta_title()

	def validate_contact_info(self):
		"""Ensure at least one contact method is provided"""
		if not self.contact_phone and not self.contact_email and not self.contact_whatsapp:
			frappe.throw("Please provide at least one contact method (phone, email, or WhatsApp)")

	def validate_price(self):
		"""Validate price field"""
		if self.listing_type in ["For Sale", "For Rent"] and not self.price:
			frappe.throw("Price is required for sale and rental listings")

	def validate_expiry_date(self):
		"""Validate expiry date"""
		if self.expires_on and frappe.utils.getdate(self.expires_on) < frappe.utils.getdate(
			frappe.utils.today()
		):
			frappe.throw("Expiry date cannot be in the past")

	def set_default_expiry(self):
		"""Set default expiry date (30 days from now)"""
		if not self.expires_on:
			self.expires_on = frappe.utils.add_days(frappe.utils.today(), 30)

	def set_default_contact_info(self):
		"""Set default contact info from user profile"""
		if not any([self.contact_phone, self.contact_email, self.contact_whatsapp]):
			user = frappe.get_doc("User", frappe.session.user)
			self.contact_email = user.email

	def set_meta_title(self):
		"""Set meta title if not provided"""
		if not self.meta_title:
			self.meta_title = self.title

	def on_update(self):
		"""Handle listing updates"""
		if self.status == "Active" and not self.approved_on:
			self.approved_on = frappe.utils.now()
			self.approved_by = frappe.session.user

	def get_context(self, context):
		"""Build context for web view template"""
		# Add all document fields to context
		context.doc = self

		# Get images
		context.images = self.get("images") or []

		# Get category details
		if self.category:
			context.category_doc = frappe.get_doc("Category", self.category)

		# Format price with currency
		if self.price:
			context.formatted_price = frappe.utils.fmt_money(self.price, currency=self.currency or "TZS")

		# Increment view count
		if not frappe.flags.in_test:
			frappe.db.set_value(
				"Listing", self.name, "views_count", self.views_count + 1, update_modified=False
			)

		# Set meta tags for SEO
		context.metatags = {
			"title": self.meta_title or self.title,
			"description": self.meta_description or self.description[:160] if self.description else "",
			"keywords": self.meta_keywords or "",
			"image": context.images[0].image if context.images else None,
		}

		# Check if listing is expired
		if self.expires_on:
			context.is_expired = frappe.utils.getdate(self.expires_on) < frappe.utils.getdate()
		else:
			context.is_expired = False

		# Add breadcrumbs
		context.parents = [{"title": "Listings", "route": "/listing"}]
		if self.category and hasattr(context, "category_doc"):
			context.parents.append(
				{"title": context.category_doc.category_name, "route": f"/listing?category={self.category}"}
			)

		return context
