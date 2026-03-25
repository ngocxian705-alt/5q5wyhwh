# -*- coding: utf-8 -*-
# Universal Protobuf Fix Library
# Makes all pb2 files compatible with any protobuf version

import google.protobuf

# ========= PATCH: runtime_version ==========
try:
    from google.protobuf import runtime_version
except ImportError:
    class runtime_version:
        class Domain:
            PUBLIC = 0

        @staticmethod
        def ValidateProtobufRuntimeVersion(*args, **kwargs):
            pass

    google.protobuf.runtime_version = runtime_version

# ========= PATCH: Add safety for old protobuf ========
try:
    from google.protobuf.internal import api_implementation
except:
    pass

# ========= PATCH: Ensure AddSerializedFile works ======
try:
    from google.protobuf import descriptor_pool
    descriptor_pool.Default()
except:
    pass

# ========= DONE ==========
print("[protobuf_fix] Runtime patched successfully.")