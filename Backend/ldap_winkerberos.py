# import winkerberos as kerberos
# import ldap3

# _, krb_context = kerberos.authGSSClientInit("ldap@10.0.42.62")

# kerberos.authGSSClientStep(krb_context, "")

# krb_token = kerberos.authGSSClientResponse(krb_context)

# print(krb_token)

try:
    import winkerberos
    print("Winkerberos install")

except:
    print("Winkerbreos not installed")