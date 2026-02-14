def check_role_access(role, metadata):
    if role == "Admin":
        return True
    return metadata.get("department") == role
