# Copyright (c) 2024, Innocent PM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class UserProfile(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		bio: DF.Text | None
		location: DF.Data | None
		phone: DF.Data | None
		profile_image: DF.AttachImage | None
		user: DF.Link | None
		whatsapp: DF.Data | None
	# end: auto-generated types

	pass
