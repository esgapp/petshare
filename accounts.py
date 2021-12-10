import bcrypt

def hashPassword(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verifyLogin(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode(), stored_password)

def createAccount(username, password, mail, phone):
    try:
        date_created = datetime.datetime.now()
        password = hashPassword()
        user = User(Username = username, Password = password, Mail = mail, Date_created = date_created, Phone = phone)
        db.session.add(entry)
        db.session.commit()
        return True
    except:
        return False