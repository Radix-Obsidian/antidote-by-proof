"""Auth decorator rule definition for Antidote scanner."""

# Route decorators that mark a function as an HTTP endpoint
ROUTE_DECORATORS = {
    "app.get", "app.post", "app.put", "app.delete", "app.patch",
    "app.route",
    "router.get", "router.post", "router.put", "router.delete",
    "router.patch", "router.route",
    # Flask blueprints
    "bp.get", "bp.post", "bp.route",
    "blueprint.get", "blueprint.post", "blueprint.route",
}

# Auth decorators that satisfy the auth requirement
AUTH_DECORATORS = {
    "login_required",
    "jwt_required",
    "require_auth",
    "auth_required",
    "permission_required",
    "requires_auth",
    "token_required",
}

RULE_NAME = "missing-auth-decorator"
SEVERITY = "CRITICAL"
DESCRIPTION = "Route handler missing authentication decorator"
