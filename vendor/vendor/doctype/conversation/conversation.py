# Copyright (c) 2024, Innocent PM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Conversation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		buyer: DF.Link | None
		listing: DF.Link | None
		seller: DF.Link | None
		status: DF.Literal["Active", "Closed"]
	# end: auto-generated types

	pass
