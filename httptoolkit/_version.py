from os import environ

ref_type = environ.get("GITHUB_REF_TYPE")

__version__ = environ.get("GITHUB_REF_NAME") if ref_type == "tag" else "0.dev0"
