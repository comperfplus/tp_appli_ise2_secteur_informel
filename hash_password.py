from getpass import getpass
from werkzeug.security import generate_password_hash

password = getpass("Mot de passe à enregistrer : ")
print("\nHash à insérer dans users_accounts.password :\n")
print(generate_password_hash(password))
