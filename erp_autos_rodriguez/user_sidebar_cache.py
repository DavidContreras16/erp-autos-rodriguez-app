import frappe


def populate_can_read_cache(login_manager=None):
    """Pre-populate the per-user "user_perm_can_read" cache that the desk sidebar uses.

    Frappe v16 (2026 fork) has a bug: WorkspaceSidebar.get_can_read_items() does not
    return the user's can_read list, so non-Administrator users never see sidebar
    items of doctype type. Mirror the correct implementation from
    frappe/desk/desktop.py here, so curated sidebars render for every role.
    """
    if frappe.session.user in ("Guest", "Administrator"):
        return

    try:
        from frappe.cache_manager import build_domain_restricted_doctype_cache

        build_domain_restricted_doctype_cache()
    except Exception:
        pass

    user = frappe.get_user()
    if not user.can_read:
        user.build_permissions()
    frappe.cache.set_value(
        "user_perm_can_read", user.can_read, user=frappe.session.user, expires_in_sec=21600
    )