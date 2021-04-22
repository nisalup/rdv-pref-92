from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from fake_useragent import UserAgent

import smtplib
import time

class RDVPREF92():
    RDV_CAD_PAGE_1 = "https://www.hauts-de-seine.gouv.fr/booking/create/11681/1"
    RDV_CAD_UNAVAILABLE_TEXT = "Il n'existe plus de plage horaire libre pour votre demande de rendez-vous. Veuillez recommencer ultérieurement."

    LOOP_INTERVAL=5*60

    def __init__(self):
        self.browser = self.__create_browser_obj()

    def __create_browser_obj(self):
        options = Options()
        #options.headless = True

        fp = webdriver.FirefoxProfile()
        fp.set_preference("general.useragent.override", UserAgent().random)
        fp.update_preferences()

        return webdriver.Firefox(options=options, firefox_profile=fp)

    def get_changement_adresse_rdv(self):
        self.browser.get(self.RDV_CAD_PAGE_1)

        time.sleep(5)
        #STEP 1: get list of guichets
        elements_guichet = self.browser.find_elements_by_xpath("//fieldset[@id='fchoix_Booking']/p[@class='Bligne']/input")
        num_guichets = len(elements_guichet)
        print(1)
        #loop through list of guichets
        for i in range(num_guichets):
            self.browser.get(self.RDV_CAD_PAGE_1)
            print(2)

            time.sleep(5)
            print(3)
            #STEP 2: click on each guichet
            element = self.browser.find_elements_by_xpath("//fieldset[@id='fchoix_Booking']/p[@class='Bligne']/input")[i]
            element.click()
            time.sleep(5)
            print(4)
            # STEP 3: click next
            self.browser.find_element_by_xpath("//input[@class='Bbutton']").click()

            time.sleep(5)
            print(5)
            # STEP4: look for unavailabilty
            if self.browser.find_element_by_xpath("//form[@id='FormBookingCreate']").text == self.RDV_CAD_UNAVAILABLE_TEXT:
                print("rien trouvé")
            else:
                self.send_email_notif()

    def loop_rdv_find_executor(self):
        counter = 1
        while True:
            time.sleep(self.LOOP_INTERVAL)
            try:
                self.get_changement_adresse_rdv()
            except:
                self.__do_double_refresh()
            if counter%5 == 0:
                self.browser.close()
                self.browser = self.__create_browser_obj()

            counter +=1

    def __do_double_refresh(self):
        self.browser.get(self.RDV_CAD_PAGE_1)
        time.sleep(5)
        #twice
        self.browser.refresh()
        self.browser.refresh()

    def send_email_notif(self):

        toing_user = 'toing@toing.co'
        # mail app password
        toing_password = 'xxxx'

        sent_from = toing_user
        to = ['toingup@toing.com']
        subject = 'RDV DISPO!!! CHECK ASAP!!!'
        body = "RDV DISPO!!! CHECK ASAP!!!"

        email_text = """\
        Subject: %s

        %s
        """ % (subject, body)

        try:
            server = smtplib.SMTP_SSL('smtp.toing.com', 465)
            server.ehlo()
            server.login(toing_user, toing_password)
            server.sendmail(sent_from, to, email_text)
            server.close()

            print('Email sent!')
        except:
            print('Something went wrong...')
