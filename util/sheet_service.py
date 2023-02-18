import gspread

from oauth2client.service_account import ServiceAccountCredentials


class SheetService():

    RESERVATIONS_SHEET = 'reservations'
    RSVP_SHEET = 'RSVPs'
    SCOPES = ["https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"]

    def __init__(self,credentials_dict, sheet_id):
        credential = \
            ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, SheetService.SCOPES)
        self.client = gspread.authorize(credential)
        self.sheet_id = sheet_id

    def getReservationData(self,name):
        reservations_db_sheet = \
            self.client.open_by_key(self.sheet_id).worksheet(SheetService.RESERVATIONS_SHEET)
        all_reservations = reservations_db_sheet.get_all_records()
        print(all_reservations)
        invite_id = 0
        for reservation in all_reservations:
            if reservation['name'].lower() == name.lower():
                invite_id = reservation['invite_id']
        
        matching_reservations = [res for res in all_reservations if res['invite_id'] == invite_id]
        return matching_reservations

        

    def makeRsvp(self,rsvps):
        rsvp_sheet = \
            self.client.open_by_key(self.sheet_id).worksheet(SheetService.RSVP_SHEET)
        values = [
            [rsvp.name,
            rsvp.invite_id,
            rsvp.attending,
            rsvp.rehearsal_attending,
            rsvp.food,
            rsvp.email] for rsvp in rsvps]
        rsvp_sheet.append_rows(values,insert_data_option='INSERT_ROWS')
