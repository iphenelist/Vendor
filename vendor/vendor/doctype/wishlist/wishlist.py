# Copyright (c) 2024, Innocent PM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Wishlist(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		added_date: DF.Datetime | None
		listing: DF.Link | None
		user: DF.Link | None
	# end: auto-generated types

	pass
