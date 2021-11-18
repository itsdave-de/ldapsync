# Copyright (c) 2021, itsdave and contributors
# For license information, please see license.txt

from inspect import CO_NESTED
import frappe
from ldap3 import Server, Connection, MODIFY_REPLACE
from frappe.client import get_password
from frappe import enqueue
from ldapsync.tools import enqueue_sync_all_contacts

from frappe.model.document import Document

class ldapsyncSettings(Document):

    @frappe.whitelist()
    def test_connection(self):
        password = get_password("ldapsync Settings", "ldapsyncSettings", "password")
        server = Server(self.server, use_ssl = False)
        conn = Connection(
            server,
            self.user,
            password,
            )
        conn.bind()
        frappe.msgprint(str(conn))

    @frappe.whitelist()
    def sync_all_contacts(self):
        enqueue_sync_all_contacts()
  