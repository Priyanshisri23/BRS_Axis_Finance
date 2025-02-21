from ldap3 import Server, Connection, ALL, SUBTREE, SIMPLE
import logging
from app.core.config import config

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


def ldap_authenticate_user(username: str, password: str) -> bool:
    """Authenticates a user against LDAP using their username and password."""
    try:
        server = Server(config.LDAP_SERVER_URL, port=config.LDAP_PORT, get_info=ALL)
        conn = Connection(server, config.LDAP_BIND_DN, config.LDAP_BIND_PASSWORD, auto_bind=True)

        # Search for user in LDAP
        search_filter = config.LDAP_USER_SEARCH_FILTER.format(username=username)
        conn.search(
            search_base=config.LDAP_BASE_DN,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=config.LDAP_USER_ATTRIBUTES,
        )

        if not conn.entries:
            logging.error(f"User '{username}' not found in LDAP.")
            return False

        user_entry = conn.entries[0]
        user_dn = str(user_entry.entry_dn)

        # Authenticate using user DN and password
        conn.unbind()
        auth_conn = Connection(server, user_dn, password, authentication=SIMPLE, auto_bind=True)
        auth_conn.unbind()

        logging.info(f"User authenticated successfully: {user_dn}")
        return True

    except Exception as e:
        logging.error(f"Authentication failed for '{username}': {e}")
        return False


def get_ldap_user_info(username: str):
    """Fetch user details from LDAP by username."""
    try:
        server = Server(config.LDAP_SERVER_URL, port=config.LDAP_PORT, get_info=ALL)
        conn = Connection(server, config.LDAP_BIND_DN, config.LDAP_BIND_PASSWORD, auto_bind=True)

        search_filter = config.LDAP_USER_SEARCH_FILTER.format(username=username)
        conn.search(
            search_base=config.LDAP_BASE_DN,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=config.LDAP_USER_ATTRIBUTES,
        )

        if not conn.entries:
            logging.error(f"User '{username}' not found in LDAP.")
            return None

        user_entry = conn.entries[0]

        # Extract user details safely
        full_name = str(user_entry["cn"]) if "cn" in user_entry else None
        first_name = str(user_entry["givenName"]) if "givenName" in user_entry else (full_name.split()[0] if full_name else "Unknown")
        last_name = str(user_entry["sn"]) if "sn" in user_entry else (full_name.split()[-1] if full_name else "Unknown")
        email = str(user_entry["mail"]) if "mail" in user_entry else None

        # Validate email format (ensure it's not an empty list or invalid format)
        if not email or "@" not in email:
            logging.error(f"Invalid or missing email for user '{username}'.")
            return None  # Return None to prevent database insertion

        user_data = {
            "dn": str(user_entry.entry_dn),
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "username": username,
        }

        logging.info(f"LDAP User Info Retrieved: {user_data}")
        conn.unbind()
        return user_data

    except Exception as e:
        logging.error(f"Error retrieving user info from LDAP: {e}")
        return None
