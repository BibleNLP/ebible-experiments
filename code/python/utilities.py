def choose_yes_no(prompt: str) -> bool:

    choice: str = " "
    while choice not in ["n","y"]:
        choice: str = input(prompt).strip()[0].lower()
    if choice == "y":
        return True
    elif choice == "n":
        return False
    

def is_excluded(source, excludes):

    for exclude in excludes:
        if exclude in source:
            return True

    return False


def is_included(source, includes):

    for include in includes:
        if include in source:
            return True
    return False