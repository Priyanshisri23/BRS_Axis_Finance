# from ldap3 import Server, Connection, ALL, SUBTREE, NTLM

# # LDAP Configuration
# LDAP_SERVER_URL = "ldap://10.0.42.62"
# LDAP_PORT = 389
# # LDAP_BIND_DN = "CN=AFLSAPADAPP01,OU=Service Accounts,DC=axisb,DC=com"
# LDAP_BIND_DN = "CN=citrix Xen App,OU=Service Accounts,DC=axisb,DC=com"

# # LDAP_BIND_DN = "AFLSAPADAPP01"
# LDAP_BIND_PASSWORD = "Total$2024"
# LDAP_BASE_DN = "DC=axisb,DC=com"
# LDAP_SEARCH_FILTER = "(sAMAccountName=AFLSAPADAPP01)"
# LDAP_USER_SEARCH_FILTER = "(&(objectClass=person)(uid={username}))"
# LDAP_USER_ATTRIBUTES = ["cn", "displayName", "mail", "uid", "sAMAccountName", "memberOf"]


# server = Server(LDAP_SERVER_URL, get_info=ALL)
# conn = Connection(server, user='axisb\\AFLSAPADAPP01', password=LDAP_BIND_PASSWORD, authentication=NTLM, auto_bind=True)
# print(conn)




# def ldap_search():
#     try:
#         server = Server(LDAP_SERVER_URL, port=LDAP_PORT, get_info=ALL)
#         conn = Connection(server, user=LDAP_BIND_DN,password=LDAP_BIND_PASSWORD, auto_bind=True)
#         print("Success...!! Connected!!")


#         con.search(
#             search_base=LDAP_SEARCH_BASE,
#             search_filter=LDAP_SEARCH_FILTER,
#             search_scope=SUBTREE,
#             attributes=LDAP_ATTRIBUTES
#         )

#         if conn.entries:
#             for entry in conn.entries:
#                 print(entry)

#         else:
#             print("No entry found")

        
#         conn.unbind()
    
#     except Exception as e:
#         print(f"an error occured: {e}")


# # ldap_search()


# def bind_service_account():
#     """
#     Test binding with the service account to ensure connectivity to LDAP server.
#     """
#     try:
#         server = Server(LDAP_SERVER_URL, port=LDAP_PORT, get_info=ALL)
#         print(f"LDAP Bind DN: {LDAP_BIND_DN}")
#         conn = Connection(server, LDAP_BIND_DN, LDAP_BIND_PASSWORD, auto_bind=True)
#         print("[SUCCESS] Service account bind successful.")
#         conn.unbind()
#         return True
#     except Exception as e:
#         print(f"[ERROR] Failed to bind service account: {e}")
#         return False

# # bind_service_account()

# # def search_user(user_id):
# #     """
# #     Search for a user in LDAP using the provided user ID.
# #     Returns the user DN and attributes if found.
# #     """
# #     try:
# #         server = Server(LDAP_SERVER_URL, port=LDAP_PORT, get_info=ALL)
# #         conn = Connection(server, LDAP_BIND_DN, LDAP_BIND_PASSWORD, auto_bind=True)

# #         search_filter = LDAP_USER_SEARCH_FILTER.format(username=user_id)
# #         conn.search(
# #             search_base=LDAP_BASE_DN,
# #             search_filter=search_filter,
# #             search_scope=SUBTREE,
# #             attributes=LDAP_USER_ATTRIBUTES
# #         )

# #         if conn.entries:
# #             user_entry = conn.entries[0]
# #             user_data = {
# #                 "dn": str(user_entry.entry_dn),
# #                 **{attr: str(user_entry[attr]) for attr in LDAP_USER_ATTRIBUTES if attr in user_entry}
# #             }
# #             print(f"[SUCCESS] User found: {user_data}")
# #             conn.unbind()
# #             return user_data
# #         else:
# #             print(f"[ERROR] User '{user_id}' not found.")
# #             conn.unbind()
# #             return None
# #     except Exception as e:
# #         print(f"[ERROR] Failed to search user: {e}")
# #         return None


# # def authenticate_user(user_dn, password):
# #     """
# #     Test binding with the user's DN and password for authentication.
# #     """
# #     try:
# #         server = Server(LDAP_SERVER_URL, port=LDAP_PORT, get_info=ALL)
# #         conn = Connection(server, user_dn, password, auto_bind=True)
# #         print(f"[SUCCESS] User authenticated successfully: {user_dn}")
# #         conn.unbind()
# #         return True
# #     except Exception as e:
# #         print(f"[ERROR] User authentication failed: {e}")
# #         return False


# # if __name__ == "__main__":
# #     # Replace with test inputs
# #     # TEST_USER_ID = input("Enter User ID: ").strip()
# #     # TEST_USER_PASSWORD = input("Enter Password: ").strip()

# #     TEST_USER_ID = "434066"
# #     TEST_USER_PASSWORD = "Eklavya@2025"

# #     # Step 1: Bind service account
# #     if not bind_service_account():
# #         print("[ERROR] Unable to bind service account. Exiting...")
# #         exit(1)

# #     # Step 2: Search for the user
# #     user_data = search_user(TEST_USER_ID)
# #     if not user_data:
# #         print("[ERROR] User not found. Exiting...")
# #         exit(1)

# #     # Step 3: Authenticate the user
# #     user_dn = user_data["dn"]
# #     if authenticate_user(user_dn, TEST_USER_PASSWORD):
# #         print("[SUCCESS] Authentication complete. User is valid.")
# #     else:
# #         print("[ERROR] Authentication failed. Check credentials and try again.")







#=====================----------------------------===============================----------------------





from ldap3 import Server, Connection, ALL, SIMPLE

LDAP_SERVER_URL = "ldap://10.0.42.62"
LDAP_PORT = 389
SERVICE_ACCOUNT = "AFLSAPADAPP01"  # or "AXISB\\AFLSAPADAPP01"
SERVICE_PASSWORD = "Total$2024"
BASE_DN = "DC=axisb,DC=com"


def authenticate_user_via_service(user_id, user_password):
    """
    1) Bind using AFLSAPADAPP01 as the service account.
    2) Search for the user’s DN using (uid=user_id).
    3) Re-bind with the user’s DN + password to confirm validity.
    """
    try:
        # 1. Service account connection
        server = Server(LDAP_SERVER_URL, port=LDAP_PORT, get_info=ALL)
        service_conn = Connection(
            server,
            user=SERVICE_ACCOUNT,
            password=SERVICE_PASSWORD,
            authentication=SIMPLE,
            auto_bind=True
        )

        # 2. Search for user DN by uid
        search_filter = f"(uid={user_id})"
        service_conn.search(
            search_base=BASE_DN,
            search_filter=search_filter,
            attributes=["dn"]
        )

        if not service_conn.entries:
            print(f"User '{user_id}' not found in LDAP.")
            service_conn.unbind()
            return False

        user_dn = service_conn.entries[0].entry_dn

        # 3. Validate user credentials by binding with user's DN
        user_conn = Connection(
            server,
            user=user_dn,
            password=user_password,
            authentication=SIMPLE
        )

        if user_conn.bind():
            print(f"User '{user_id}' authenticated successfully.")
            user_conn.unbind()
            service_conn.unbind()
            return True
        else:
            print(f"Invalid credentials for user '{user_id}'.")
            service_conn.unbind()
            return False

    except Exception as e:
        print(f"Error occurred: {e}")
        return False


if __name__ == "__main__":
    test_user_id = "434066"  # Example user to verify
    test_user_password = "Eklavya@2025"  # Example password for the user
    result = authenticate_user_via_service(test_user_id, test_user_password)
    if result:
        print("Authentication succeeded.")
    else:
        print("Authentication failed.1")
