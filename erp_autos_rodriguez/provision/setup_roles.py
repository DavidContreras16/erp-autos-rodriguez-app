"""Roles y permisos del modelo contenido (2 roles) + usuarios de prueba.

Ejecutar: bench --site development.localhost execute erp_autos_rodriguez.provision.setup_roles.run

- Administrador = System Manager (built-in): todo, incluidos usuarios.
- Operador = rol custom: maneja toda la operacion (vehiculos, ventas, catalogos),
  sin administracion de usuarios/sistema.
Retira los 5 roles del modelo disperso.
"""
import frappe

APP_DOCTYPES = ["Vehiculo", "Proveedor", "Cliente", "Almacen", "Repuesto"]
OLD_ROLES = ["Compras", "Logistica", "Taller", "Control de Calidad", "Ventas"]

SM = {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1,
      "print": 1, "email": 1, "report": 1, "share": 1, "export": 1}
OP = {"role": "Operador", "read": 1, "write": 1, "create": 1, "delete": 1,
      "print": 1, "email": 1, "report": 1, "share": 1, "export": 1}


def _ensure_operador_role():
    if not frappe.db.exists("Role", "Operador"):
        frappe.get_doc({"doctype": "Role", "role_name": "Operador", "desk_access": 1}).insert(ignore_permissions=True)
        print("CREATED Role Operador")
    else:
        print("SKIP Role Operador")


def _set_perms():
    for dt in APP_DOCTYPES:
        d = frappe.get_doc("DocType", dt)
        d.set("permissions", [])
        d.append("permissions", dict(SM))
        d.append("permissions", dict(OP))
        d.save(ignore_permissions=True)
        print("PERMS set", dt)


def _drop_old_roles():
    for role in OLD_ROLES:
        if not frappe.db.exists("Role", role):
            continue
        for hr in frappe.get_all("Has Role", filters={"role": role}):
            frappe.delete_doc("Has Role", hr.name, force=1, ignore_permissions=True)
        for cp in frappe.get_all("Custom DocPerm", filters={"role": role}):
            frappe.delete_doc("Custom DocPerm", cp.name, force=1, ignore_permissions=True)
        try:
            frappe.delete_doc("Role", role, force=1, ignore_permissions=True)
            print("DELETED Role", role)
        except Exception as e:
            print("KEEP Role", role, "->", str(e)[:60])


def _ensure_user(email, first, roles, pwd):
    if frappe.db.exists("User", email):
        u = frappe.get_doc("User", email)
    else:
        u = frappe.new_doc("User")
        u.email = email
        u.first_name = first
        u.new_password = pwd
        u.send_welcome_email = 0
    u.enabled = 1
    u.set("roles", [])
    for r in roles:
        u.append("roles", {"role": r})
    u.save(ignore_permissions=True)
    print("USER", email, "roles=", roles)


def run():
    _ensure_operador_role()
    # Los permisos de Vehiculo/catalogos ya vienen del JSON del doctype al instalar la app.
    # Solo se reescriben en dev (modificar doctypes estandar requiere developer_mode).
    if frappe.conf.developer_mode:
        _set_perms()
        _drop_old_roles()
    _ensure_user("operador@autosrodriguez.com", "Operador", ["Operador"], "Autos2026!")
    _ensure_user("admin@autosrodriguez.com", "Administrador", ["System Manager", "Operador"], "Autos2026!")
    frappe.db.commit()
    print("SETUP_ROLES_DONE")
