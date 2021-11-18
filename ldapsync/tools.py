import frappe
from ldap3 import Server, Connection, MODIFY_REPLACE
from frappe.client import get_password
from frappe import enqueue

def invoke_contact_sync(doc, method=None):
    settings = frappe.get_single("ldapsync Settings")
    if not settings.sync_enabled == 1:
        return
    frappe.enqueue(sync_contact(doc.name))
    return True

def enqueue_sync_all_contacts():
    contact_list = frappe.get_all("Contact", filters={"disable_ldap_sync": 0})
    for contact in contact_list:
        enqueue(sync_contact(contact["name"]))

def sync_contact(contact):
    settings = frappe.get_single("ldapsync Settings")

    contact_doc = frappe.get_doc("Contact", contact)
    if contact_doc.disable_ldap_sync == 1:
        return False

    password = get_password("ldapsync Settings", "ldapsyncSettings", "password")
    server = Server(settings.server)
    conn = Connection(
        server,
        settings.user,
        password,
        )
    conn.bind()

    dn = ""
    dn += contact_doc.company_name + "." if contact_doc.company_name else ""
    dn += contact_doc.first_name + "." if contact_doc.first_name else ""
    dn += contact_doc.last_name + "." if contact_doc.last_name else ""  
    if dn.endswith("."):
        dn = dn[:-1]
    dn = "CN=" + dn + "," + settings.basepath

    print(dn)
    
    if not contact_doc.displayname:
        contact_doc.displayname = contact_doc.name

    mapping = {
        "displayname": "displayname",
        "givenName": "first_name",
        "sn": "last_name",
        "company": "company_name",
        "telephoneNumber": "phone",
        "mobile": "mobile_no",
        "mail": "email_id"
    }
    params = {}
    for key in mapping.keys():
        if getattr(contact_doc, mapping[key]) not in ("", None):
            params[key] = getattr(contact_doc, mapping[key])
    print(params)
    
    if contact_doc.ldap_dn:
        print("update")
        try:
            conn.search(settings.basepath, "(distinguishedName="+ contact_doc.ldap_dn + ")", attributes=params.keys())
            if len(conn.entries) == 0:
                conn.add(dn, 'contact', params)
                contact_doc.ldap_dn = dn
                contact_doc.save()
                return

            for el in conn.entries:
                for key in params.keys():
                    if getattr(el, key) != getattr(contact_doc, mapping[key]):
                        print("changed")
                        print(contact_doc.ldap_dn)
                        print(key)
                        print(getattr(contact_doc, mapping[key]))
                        value = getattr(contact_doc, mapping[key])
                        req = conn.modify(contact_doc.ldap_dn,
                            {key: [(MODIFY_REPLACE, [value])]})
                        print(conn.result)
        except:
            #pass
            frappe.throw("Contact could not be updated in LDAP")
    else:
        try:
            conn.add(dn, 'contact', params)
            contact_doc.ldap_dn = dn
            contact_doc.save()
        except:
            #pass
            frappe.throw("Contact could not be added to LDAP")