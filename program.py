from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import keyring, time, ipaddress, os, sys, csv

############################Global Vars############################
retries = 3


############################FUNCTIONS##############################

def resource_path(rel_path):
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, rel_path)
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(sys.executable), rel_path)
    return path


def open_csv_file():
    csv_file = resource_path("printers.csv")
    name_list = []
    ip_list = []

    with open(csv_file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hostname = row["hostname"]
            ip = row["ip"]
            name_list.append(hostname)
            ip_list.append(ip)
            print(hostname, ip)

    return ip_list, name_list


#def get_ips():
#    ip_list = []
#    names_list = []
#
#    while True:
#        try:
#            num_ips = int(input("How many Printers?:"))
#            if num_ips < 1:
#                raise ValueError
#            else:
#                break
#        except ValueError:
#            print("Please enter a valid number")
#
#    for x in range(1, num_ips + 1):
#        while True:
#            try:
#                ip_add = input(f"Please enter IP address #{x}: ")
#
#                if isinstance(ipaddress.ip_address(ip_add), ipaddress.IPv4Address):
#                    ip_list.append(ip_add)
#                    break
#                else:
#                    raise ValueError
#
#           except ValueError:
#                print("Please enter a valid IP address")
#
#        host_names = input(f"Please enter Hostname #{x}: ")
#        names_list.append(host_names)
#
#    return ip_list, names_list


#def find_model():
    #model = driver.find_element(By.CSS_SELECTOR, '[data-bind="text:getHeaderInfo(1)"]')
    #modelo = model.text
    #print(modelo)


def login_printer():
    printer_user = keyring.get_password("PrinterUser", "User")
    printer_pass = keyring.get_password("PrinterPass", "Pass")

    for i in range(retries):
        try:
            driver.switch_to.frame("wlmframe")

            driver.implicitly_wait(20)
            switch_menu1 = driver.find_element(By.CSS_SELECTOR, '[id="tm2"]')
            switch_menu1.click()

            switch_menu2 = driver.find_element(By.CSS_SELECTOR, '[id="s80"]')
            switch_menu2.click()

            time.sleep(4)
            driver.switch_to.frame("printingjobs")
            grab_sn = driver.find_element(By.CSS_SELECTOR, '[data-bind="text: serialNumber"]')
            sn = grab_sn.text
            # print(sn)
            grab_mac = driver.find_element(By.CSS_SELECTOR, '[data-bind="text: macAddress"]')
            mac = grab_mac.text

            driver.switch_to.parent_frame()
            login = driver.find_element(By.CSS_SELECTOR, '[id="s10"]')
            login.click()

            login_field = driver.find_element(By.CSS_SELECTOR, '[id="arg01_UserName"]')
            login_field.click()
            login_field.send_keys(printer_user)

            login_password = driver.find_element(By.CSS_SELECTOR, '[id="arg02_Password"]')
            login_password.click()
            #login_password.send_keys(sn)
            login_password.send_keys(printer_pass)

            time.sleep(3)
            login_submit = driver.find_element(By.CSS_SELECTOR, '[data-bind="value: mes()[20]"]')
            login_submit.click()

            print("[+] Logged in")
            return mac

        except:
            i = str(i + 1)
            print("Failed attempt #" + i + " at logging in")


def energy_printer():
    for i in range(retries):
        try:

            device_settings_menu = driver.find_element(By.CSS_SELECTOR, '[id="tm9"]')
            device_settings_menu.click()

            device_settings_energy_saver = driver.find_element(By.CSS_SELECTOR, '[id="s27"]')
            device_settings_energy_saver.click()

            driver.switch_to.frame("printingjobs")
            quick_recovery = driver.find_element(By.CSS_SELECTOR, 'input[type="radio"][name="arg01"][value="1"]')
            quick_recovery.click()

            sleep_timer_dropdown = driver.find_element(By.CSS_SELECTOR, '[name="arg07"]')
            select = Select(sleep_timer_dropdown)
            select.select_by_value("120")

            device_settings_submit = driver.find_element(By.CSS_SELECTOR, '[name="submit001"]')
            device_settings_submit.click()

            try:
                alert = driver.switch_to.alert
                alert.accept()
            except:
                pass

            print("[+] Set Energy Saving")
            return True

        except:
            i = i + 1
            print(f"Failed attempt #{i} at configuring energy settings")


def time_printer():
    for i in range(retries):
        try:

            driver.switch_to.parent_frame()
            device_settings_menu_2 = driver.find_element(By.CSS_SELECTOR, '[id="s28"]')
            device_settings_menu_2.click()

            driver.switch_to.frame("printingjobs")
            device_settings_date_time = driver.find_element(By.CSS_SELECTOR, '[name="arg08_TimeZone"]')
            select = Select(device_settings_date_time)
            select.select_by_value("timez_ctl_time")

            #device_settings_daylight = driver.find_element(By.CSS_SELECTOR, '[name="arg09_SummerTime"]')
            #ActionChains(driver) \
                #.scroll_to_element(device_settings_daylight) \
                #.move_to_element(device_settings_daylight) \
                #.pause(.5) \
                #.click(device_settings_daylight) \
                #.pause(.5) \
                #.perform()

            device_settings_time_server = driver.find_element(By.CSS_SELECTOR, '[id="arg10_TimeServer"]')
            driver.execute_script("arguments[0].scrollIntoView(true);", device_settings_time_server)
            device_settings_time_server.clear()
            device_settings_time_server.send_keys("10.1.249.110")

            device_settings_submit2 = driver.find_element(By.CSS_SELECTOR, '[name="submit001"]')
            device_settings_submit2.click()

            try:
                alert = driver.switch_to.alert
                alert.accept()
            except:
                pass

            print("[+] Set Date and Time settings")
            return True

        except:
            i = i + 1
            print(f"Failed attempt #{i} at configuring time and date")


def snmp_printer():
    snmp_read = keyring.get_password("PrinterSNMPRead", "SNMP")
    snmp_write = keyring.get_password("PrinterSNMPWrite", "SNMP")

    for i in range(retries):
        try:

            time.sleep(3)
            driver.switch_to.parent_frame()
            management_settings_menu = driver.find_element(By.CSS_SELECTOR, '[id="tm50"]')
            ActionChains(driver) \
                .scroll_to_element(management_settings_menu) \
                .move_to_element(management_settings_menu) \
                .click(management_settings_menu) \
                .perform()

            management_settings_snmp = driver.find_element(By.CSS_SELECTOR, '[id="s75"]')
            ActionChains(driver) \
                .scroll_to_element(management_settings_snmp) \
                .move_to_element(management_settings_snmp) \
                .click(management_settings_snmp) \
                .perform()

            driver.switch_to.frame("printingjobs")
            # snmp_read_com = driver.find_element(By.CSS_SELECTOR, '[id="arg01_ReadCommunity"]')
            # snmp_read_com.click()
            # snmp_read_com.clear()
            # snmp_read_com.send_keys(snmp_read)

            # snmp_write_com = driver.find_element(By.CSS_SELECTOR, '[id="arg02_WriteCommunity"]')
            # snmp_write_com.click()
            # snmp_write_com.clear()
            # snmp_write_com.send_keys(snmp_write)

            hp_web_jetadmin = driver.find_element(By.CSS_SELECTOR, '[id="arg05_HpWeb"]')
            ActionChains(driver) \
                .scroll_to_element(hp_web_jetadmin) \
                .move_to_element(hp_web_jetadmin) \
                .click(hp_web_jetadmin) \
                .perform()

            management_settings_snmp_submit = driver.find_element(By.CSS_SELECTOR, '[name="submit001"]')
            management_settings_snmp_submit.click()

            try:
                alert = driver.switch_to.alert
                alert.accept()
            except:
                pass

            print("[+] Set SNMP")
            return True

        except:
            i = i + 1
            print(f"Failed attempt #{i} at configuring SNMP")


def admin_printer():
    printer_pass = keyring.get_password("PrinterPass", "Pass")
    time.sleep(3)

    for i in range(retries):
        try:

            driver.switch_to.parent_frame()
            management_settings_auth = driver.find_element(By.CSS_SELECTOR, '[id="s71"]')
            management_settings_auth.click()
            time.sleep(5)

            # click Admin user ISSUES HERE.
            # No one can be logged into printer page as Admin or it will freeze
            driver.switch_to.frame("funsetrule")
            management_settings_admin = WebDriverWait(driver, 13).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'a[data-bind="attr: { href: $parent.col1col2Attr().href }"]')))
            ActionChains(driver) \
                .scroll_to_element(management_settings_admin) \
                .click(management_settings_admin) \
                .perform()

            driver.switch_to.parent_frame()
            driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, '[class="popWin1_iframe active"]'))
            management_settings_admin_pass = driver.find_element(By.CSS_SELECTOR, '[id="InpPassword"]')
            management_settings_admin_pass.click()
            management_settings_admin_pass.clear()
            management_settings_admin_pass.send_keys(printer_pass)

            management_settings_admin_pass_conf = driver.find_element(By.CSS_SELECTOR, '[id="ConfPassword"]')
            management_settings_admin_pass_conf.click()
            management_settings_admin_pass_conf.clear()
            management_settings_admin_pass_conf.send_keys(printer_pass)

            management_settings_admin_submit = driver.find_element(By.CSS_SELECTOR, '[name="submit001"]')
            management_settings_admin_submit.click()
            time.sleep(3)

            try:
                alert = driver.switch_to.alert
                alert.accept()
            except:
                pass

            print("[+] Set Admin Pass")
            return True

        except:
            i = i + 1
            print(f"Failed attempt #{i} at setting admin pass")


def hostname_printer(lis, i):
    for x in range(retries):
        try:

            driver.switch_to.parent_frame()
            device_settings_menu = driver.find_element(By.CSS_SELECTOR, '[id="tm9"]')
            device_settings_menu.click()

            device_settings_system = driver.find_element(By.CSS_SELECTOR, '[id="s29"]')
            device_settings_system.click()

            driver.switch_to.frame("printingjobs")
            device_settings_system_name = driver.find_element(By.CSS_SELECTOR, '[id="arg01_HostName"]')
            device_settings_system_name.click()
            device_settings_system_name.clear()
            device_settings_system_name.send_keys(lis[i])

            device_settings_system_submit = driver.find_element(By.CSS_SELECTOR, '[name="submit001"]')
            device_settings_system_submit.click()

            try:
                alert = driver.switch_to.alert
                alert.accept()
            except:
                pass

            print("[+] Set Hostname")
            return True

        except:
            x = x + 1
            print(f"Failed attempt #{x} at setting hostname")


def restart_printer():
    time.sleep(10)

    for i in range(retries):
        # fails here due to printer quick restart that occurs after hostname change. This is why refresh and switch to frame is needed
        try:
            driver.refresh()

            driver.switch_to.frame("wlmframe")
            management_settings_menu = driver.find_element(By.CSS_SELECTOR, '[id="tm50"]')
            ActionChains(driver) \
                .scroll_to_element(management_settings_menu) \
                .move_to_element(management_settings_menu) \
                .click(management_settings_menu) \
                .perform()

            management_settings_reset = driver.find_element(By.CSS_SELECTOR, '[id="s78"]')
            ActionChains(driver) \
                .scroll_to_element(management_settings_reset) \
                .move_to_element(management_settings_reset) \
                .click(management_settings_reset) \
                .perform()

            driver.switch_to.frame("printingjobs")
            management_settings_reset_button = driver.find_element(By.CSS_SELECTOR, '[id="wTwohundredPX"]')
            management_settings_reset_button.click()

            try:
                alert = driver.switch_to.alert
                alert.accept()
            except:
                pass

            print("[+] Restarted printer")
            return True

        except:
            i = i + 1
            print(f"Failed attempt #{i} at restarting printer")


def config_printer(list_ip, list_name):
    for i in range(len(list_ip)):
        ip = 'http://' + list_ip[i] + '/'
        print(ip)

        print("Accessing printer page")
        try:
            driver.get(ip)
        except:
            print(f"Selenium failed to reach {ip}. Skipping...")
            print()
            continue

        #try:
            #find_model()
        #except:
            #print(f"Unable to find model of  + {list_ip[i]}")
            #raise

        try:
            mac = login_printer()
        except:
            er2 = "Failed to login into " + list_ip[i]
            print(er2)
            raise

        try:
            energy_printer()
        except:
            er3 = "Failed at configuring Energy Saver & Timer settings on " + list_ip[i]
            print(er3)
            raise

        try:
            time_printer()
        except:
            er4 = "Failed at configuring Date & Time Settings on " + list_ip[i]
            print(er4)
            raise

        try:
            snmp_printer()
        except:
            er5 = "Failed at configuring SNMP settings on " + list_ip[i]
            print(er5)
            raise

        try:
            admin_printer()
        except:
            er6 = "Failed at configuring Authentication settings " + list_ip[i]
            print(er6)
            raise

        try:
            hostname_printer(list_name, i)
        except:
            er7 = "Failed at configuring Hostname settings on " + list_ip[i]
            print(er7)
            raise

        try:
            restart_printer()
        except:
            er8 = "Failed at restarting " + list_ip[i]
            print(er8)
            raise

        w = "Done with " + list_name[i]
        t = list_name[i] + " - " + list_ip[i] + " - " + mac
        print(w)
        print(t)
        print()
        print()
        # time.sleep(30) remove later, used for debugging


############################FUNCTIONS##############################
##############################MAIN#################################
driver_path = resource_path("chromedriver.exe")

print(
    '          _____                             _____   __                                                                                    ')
print(
    '         / ____|    ____      _________    |  ___| |__|   _______     __    __    _____     ____                                          ')
print(
    '        | |       /      \   |   ___   |  _|  |_    __   /   __   \  |  |  |  |  |   __|  /  |*|  \                                       ')
print(
    '        | |      |   / \   | |  |   |  | |_   __|  |  |  |  |  |  |  |  |  |  |  |  |    |   _____|                                       ')
print(
    '        | |_____ |   \_/   | |  |   |  |   |  |    |  |  |  |__|  |  |  |__|  |  |  |     \  \_____                                       ')
print(
    '         \______| \_______/  |__|   |__|   |__|    |__|  |____    |   \______/   |__|       \_____/                                       ')
print(
    '                                                        ___   |   |                                                                       ')
print(
    '                                                        \  \_/   /                                                                        ')
print(
    '                                                          \ __ /                                                                          ')
print(
    '          _____              __                   __                                                                                      ')
print(
    '         |      \   _____   |__|  _________      |  |        ____      _____                                                              ')
print(
    '         |    __/  |   __|   __  |   ___   |  ___|  |___   /  |*|  \  |   __|                                                             ')
print(
    '         |  |      |  |     |  | |  |   |  | |___    ___| |   _____|  |  |                                                                ')
print(
    '         |  |      |  |     |  | |  |   |  |     |  |      \  \_____  |  |                                                                ')
print(
    '         |__|      |__|     |__| |__|   |__|     |__|        \_____/  |__|                                                                ')
print(
    '                                                                                                                                          ')
print(' ______________________________ ')
print('|                              |')
print('|       Kyocera PA5500x        |')
print('|______________________________|')
print('| |________=======__________|__|')
print('| |                         |  |')
print('| |                         | O|')
print('|_|_________________________|__|')
print('|                              |')
print('|                          []  |')
print('|_______=================______|')
print()

while True:

    print("Welcome to the Kyocera PA5500x Automated Configurator!")
    print("1. Start configuring!")
    print("2. Quit :(")
    print()
    switch = input("Please enter a number (1 or 2): ")
    print()
    print()
    if switch == "1":
        #list_o_ip, list_o_names = get_ips()
        list_o_ip, list_o_names = open_csv_file()

        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.binary_location = resource_path(r"chrome-win64\chrome.exe")
        service = Service(driver_path)
        options.accept_insecure_certs = True
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--mute-audio')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 10)

        # Because printer has no cert, accept it and ignore errors

        config_printer(list_o_ip, list_o_names)
        driver.quit()
    elif switch == "2":
        break
    else:
        print("Please enter either 1 or 2")

##############################MAIN#################################
