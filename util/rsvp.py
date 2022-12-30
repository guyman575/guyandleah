

class Rsvp:
    def __init__(self,name,invite_id,attending,rehearsal_attending, food, email):
        self.name = name
        self.invite_id = invite_id
        self.attending = attending
        self.rehearsal_attending = rehearsal_attending
        self.food = food
        # Email will be the same for both members of a couple
        # as only one email is collected
        self.email = email

    @classmethod
    def from_form(cls,form,index):
        name = form.get(f"rsvp_name_{index}")
        id = form.get(f"rsvp_id_{index}")
        attending = form.get(f"attending_{index}")
        rehearsal = form.get(f"rehearsal_{index}")
        food = form.get(f"food_pref_{index}")
        email = form.get("email")
        return Rsvp(name,id,attending,rehearsal,food, email)