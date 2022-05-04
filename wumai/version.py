from pbr import version as pbr_version

version_info = pbr_version.VersionInfo("wumai")


def version_string():
    return version_info.semantic_version().debian_string()
