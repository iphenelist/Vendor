# Copyright (c) 2024, Innocent PM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ListingImage(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		image: DF.AttachImage | None
		is_primary: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		sort_order: DF.Int
	# end: auto-generated types

	pass
