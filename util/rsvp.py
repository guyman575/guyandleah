

class Rsvp:
    def __init__(self,name,invite_id,attending,rehearsal_attending, food):
        self.name = name
        self.invite_id = invite_id
        self.attending = attending
        self.rehearsal_attending = rehearsal_attending
        self.food = food

    @classmethod
    def from_form(cls,form,index):
        name = form.get(f"rsvp_name_{index}")
        id = form.get(f"rsvp_id_{index}")
        attending = form.get(f"attending_{index}")
        rehearsal = form.get(f"rehearsal_{index}")
        food = form.get(f"food_pref_{index}")
        return Rsvp(name,id,attending,rehearsal,food)