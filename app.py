from getpass import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import pathlib
import random
import smtplib
import sys
import time
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
import tomli_w

colorama_init()

VERSION = "1.0.0"

import tomli
if os.name == 'nt': # Windows
  import msvcrt
else:
  import tty
  import termios

# === Console Actions ===

# Clears screen
def clearscreen():
  if os.name == 'nt': # Windows
    os.system('cls')
  else:
    os.system('clear')

# Reads for keypress
def read_single_keypress():
  if os.name == 'nt': # Windows
    first_byte = msvcrt.getch()
    if first_byte in (b'\xe0', b'\x00'):
      second_byte = msvcrt.getch()
      return first_byte + second_byte
    else:
      return first_byte
  else:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
      tty.setraw(fd)
      key = sys.stdin.read(1)
    finally:
      termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key

# Displays a menu with arrow keys for navigation
def display_menu(options, selected_index, written=False):
  while True:
    if written:
      print(f"\033[{str(1+len(options))}A")
    else:
      written = True
    for i, option in enumerate(options):
      if i == selected_index:
        print(f" {Fore.CYAN}>> {option}{Style.RESET_ALL}{" " * 10}")
      else:
        print(f"   {option}{Style.RESET_ALL}{" " * 10}")
    key = read_single_keypress()
    if key in [b'\x1b[A', b'\xe0H', b'\x00H', b'H']:  # Up arrow key
      selected_index = (selected_index - 1) % len(options)
    elif key in [b'\x1b[B', b'\xe0P', b'\x00P', b'P']:  # Down arrow key
      selected_index = (selected_index + 1) % len(options)
    elif key in ['\r', '\n', b'\r']:
      break
  return selected_index

# === File Handling ===

# Gets the settings.toml data
def get_toml_data():
  path = pathlib.Path(__file__).parent / "settings.toml"
  settings_file = path.open(mode="rb")
  settings_toml = tomli.load(settings_file)
  settings_file.close()
  return settings_toml

# Checks if the important values are empty
def is_toml_empty():
  settings_toml = get_toml_data()
  if str(settings_toml["smtp"]["username"]).strip() == "": return True
  if str(settings_toml["smtp"]["passkey"]).strip() == "": return True
  if str(settings_toml["smtp"]["smtp_server"]).strip() == "": return True
  if int(settings_toml["smtp"]["smtp_port"]) == 0: return True
  if settings_toml["emails"]["ids"] == []: return True
  if settings_toml["emails"]["subjects"] == []: return True
  if settings_toml["emails"]["writeups"] == []: return True
  if settings_toml["emails"]["isfromfile"] == []: return True
  if settings_toml["csv"]["titles"] == []: return True
  if settings_toml["csv"]["placeholders"] == []: return True
  if str(settings_toml["csv"]["output_folder"]).strip() == "": return True
  return False

# Save data to settings.toml file
def save_to_toml(toml_data):
  path = pathlib.Path(__file__).parent / "settings.toml"
  settings_file = path.open(mode="wb")
  tomli_w.dump(toml_data, settings_file)
  settings_file.close()

# === Console Graphics ===

# ASCII Art for main title
def show_title(page: str):
  print("")
  print("  ______               __                ________                          __  __   ______                             __           ".replace("$", Fore.GREEN + "$" + Style.RESET_ALL))
  print(" /      \\             |  \\              |        \\                        |  \\|  \\ /      \\                           |  \\          ".replace("$", Fore.GREEN + "$" + Style.RESET_ALL))
  print("|  $$$$$$\\ __    __  _| $$_     ______  | $$$$$$$$ ______ ____    ______   \\$$| $$|  $$$$$$\\  ______   _______    ____| $$  ______  ".replace("$", Fore.GREEN + "$" + Style.RESET_ALL))
  print("| $$__| $$|  \\  |  \\|   $$ \\   /      \\ | $$__    |      \\    \\  |      \\ |  \\| $$| $$___\\$$ /      \\ |       \\  /      $$ /      \\ ".replace("$", Fore.GREEN + "$" + Style.RESET_ALL))
  print("| $$    $$| $$  | $$ \\$$$$$$  |  $$$$$$\\| $$  \\   | $$$$$$\\$$$$\\  \\$$$$$$\\| $$| $$ \\$$    \\ |  $$$$$$\\| $$$$$$$\\|  $$$$$$$|  $$$$$$\\".replace("$", Fore.GREEN + "$" + Style.RESET_ALL))
  print("| $$$$$$$$| $$  | $$  | $$ __ | $$  | $$| $$$$$   | $$ | $$ | $$ /      $$| $$| $$ _\\$$$$$$\\| $$    $$| $$  | $$| $$  | $$| $$   \\$$".replace("$", Fore.GREEN + "$" + Style.RESET_ALL))
  print("| $$  | $$| $$__/ $$  | $$|  \\| $$__/ $$| $$_____ | $$ | $$ | $$|  $$$$$$$| $$| $$|  \\__| $$| $$$$$$$$| $$  | $$| $$__| $$| $$      ".replace("$", Fore.GREEN + "$" + Style.RESET_ALL))
  print("| $$  | $$ \\$$    $$   \\$$  $$ \\$$    $$| $$     \\| $$ | $$ | $$ \\$$    $$| $$| $$ \\$$    $$ \\$$     \\| $$  | $$ \\$$    $$| $$      ".replace("$", Fore.GREEN + "$" + Style.RESET_ALL))
  print(" \\$$   \\$$  \\$$$$$$     \\$$$$   \\$$$$$$  \\$$$$$$$$ \\$$  \\$$  \\$$  \\$$$$$$$ \\$$ \\$$  \\$$$$$$   \\$$$$$$$ \\$$   \\$$  \\$$$$$$$ \\$$      ".replace("$", Fore.GREEN + "$" + Style.RESET_ALL))
  print("")
  print((" " * 127) + VERSION)
  print(Fore.CYAN + (" " * int((((133-len(page))/2) - 4))) + "- [ " + page + " ] -" + Style.RESET_ALL)
  print("")

# Run Automation Page
def run_automation_page():
  clearscreen()
  show_title("Run Automation")
  print("   Enter the .CSV file of your contacts:")
  contacts_csv = input(" > ")
  contacts_csv += "" if contacts_csv.endswith(".csv") else ".csv"
  clearscreen()
  show_title("Run Automation / Before We Start...")
  print(f"   {Fore.YELLOW}DISCLAIMER!{Style.RESET_ALL}")
  print("")
  print("   Here are settings for you to double check:")
  print("")
  settings_toml = get_toml_data()
  print(f"   {Fore.CYAN}SMTP Settings{Style.RESET_ALL}")
  print(f"   Username: {settings_toml["smtp"]["username"]}")
  print(f"   SMTP Server & Port: {settings_toml["smtp"]["smtp_server"]}:{settings_toml["smtp"]["smtp_port"]}")
  print("")
  print(f"   {Fore.CYAN}Email IDs and Write-ups{Style.RESET_ALL}")
  print(f"   {len(settings_toml["emails"]["ids"])} Email IDs: [", end='')
  for i, email_id in enumerate(settings_toml["emails"]["ids"]):
    if i % 4 == 0: print("\n     ", end='')
    print(email_id + ", ", end='')
  print("\n   ]")
  print(f"   {len(settings_toml["emails"]["writeups"])} Email Write-ups: [", end='')
  for i, writeup in enumerate(settings_toml["emails"]["writeups"]):
    if i % 1 == 0: print("\n     ", end='')
    print(settings_toml["emails"]["subjects"][i] + ": " + writeup + ", ", end='')
  print("\n   ]")
  print("")
  print(f"   {Fore.CYAN}CSV Data{Style.RESET_ALL}")
  print(f"   {len(settings_toml["csv"]["placeholders"])} Placeholders: [", end='')
  for i, placeholder in enumerate(settings_toml["csv"]["placeholders"]):
    if i % 6 == 0: print("\n     ", end='')
    print("{" + placeholder + "}, ", end='')
  print("\n   ]")
  print("   Filter based on Write-ups? " + ('Yes' if settings_toml["csv"]["segregate_by_writeups"] else 'No'))
  print("   Filter based on Email IDs? " + ('Yes' if settings_toml["csv"]["segregate_by_ids"] else 'No'))
  print("   Output .CSV folder: " + settings_toml["csv"]["output_folder"])
  print("")
  print("   Contacts List .CSV file: " + contacts_csv)
  print("")
  proceed = display_menu(['Back to Safety', 'Yes, Let\'s Do It!'], 0)
  if proceed == 0:
    main_page()
  else:
    logging_page(contacts_csv)

# Logging Page
def logging_page(contacts_csv):
  settings_toml = get_toml_data()
  clearscreen()
  show_title("Run Automation / Logging Page (Running)")
  
  # CSV Data
  contacts_file = open(contacts_csv, mode='r', encoding='utf-8')
  contacts = contacts_file.readlines()
  contacts_headers = contacts[0].replace('\n', '').split(",")
  rows = len(contacts) - 1
  columns = len(contacts_headers)
  placeholder_index = []
  for placeholder_title_header in settings_toml["csv"]["titles"]:
    if placeholder_title_header in contacts_headers: placeholder_index.append(contacts_headers.index(placeholder_title_header))
    else: placeholder_index.append(-1)
  contacts.pop(0)
  
  # Output Set-up
  cwd = os.getcwd() + "\\"
  writeup_outputs = None
  writeup_output_data = []
  id_outputs = None
  id_output_data = []
  output_path = cwd + settings_toml["csv"]["output_folder"]
  if not os.path.exists(output_path):
    os.makedirs(output_path)
  if settings_toml["csv"]["segregate_by_writeups"]:
    writeup_outputs = []
    for file in settings_toml["emails"]["writeups"]:
      try:
        filex = open(".\\" + settings_toml["csv"]["output_folder"] + "\\output-" + file.split(".")[0] + ".csv", mode='x')
        filex.close()
      except:
        pass
      filex = open(".\\" + settings_toml["csv"]["output_folder"] + "\\output-" + file.split(".")[0] + ".csv", mode='w', encoding='utf-8')
      filex.write(",".join(contacts_headers))
      writeup_outputs.append(filex)
      writeup_output_data.append(",".join(contacts_headers))
  if settings_toml["csv"]["segregate_by_ids"]:
    id_outputs = []
    for file in settings_toml["emails"]["ids"]:
      try:
        filex = open(".\\" + settings_toml["csv"]["output_folder"] + "\\output-" + file.split("@")[0] + ".csv", mode='x')
        filex.close()
      except:
        pass
      filex = open(".\\" + settings_toml["csv"]["output_folder"] + "\\output-" + file.split("@")[0] + ".csv", mode='w', encoding='utf-8')
      filex.write(",".join(contacts_headers))
      id_outputs.append(filex)
      id_output_data.append(",".join(contacts_headers))
  
  #Email SMTP Set-up
  SMTP_server = smtplib.SMTP(settings_toml["smtp"]["smtp_server"], settings_toml["smtp"]["smtp_port"])
  SMTP_server.ehlo()
  SMTP_server.starttls()
  
  SMTP_server.login(settings_toml["smtp"]["username"], settings_toml["smtp"]["passkey"])
  
  # Loading Screen
  emails_sent = 0
  loading_percentage = emails_sent/rows
  print("")
  
  # Email Sending Loop
  for contact in contacts:
    print("   [" + ("█" * round(50*loading_percentage)) + (" " * round(50*(1-loading_percentage))) + "] " + str(emails_sent) + " out of " + str(rows) + (" " * 15))
    
    contact_details = contact.replace('\n', '').split(",")
    
    contact_email = contact_details[placeholder_index[settings_toml["csv"]["placeholders"].index("email")]]
    print("   Currently sending to -> " + Fore.LIGHTBLACK_EX + contact_email + Style.RESET_ALL + (" " * (133 - len(contact_email))))
    
    email_writeup = random.choice(settings_toml["emails"]["writeups"])
    email_writeup_index = settings_toml["emails"]["writeups"].index(email_writeup)
    for i, placehold in enumerate(placeholder_index):
      if placehold != -1: email_writeup.replace("{" + settings_toml["csv"]["placeholders"][i] + "}", contact_details[placehold])
    email_subject = settings_toml["emails"]["subjects"][email_writeup_index]
    print("   Sending write-up from " + Fore.LIGHTBLACK_EX + email_writeup + Style.RESET_ALL)
    
    sending_email = random.choice(settings_toml["emails"]["ids"])
    sending_email_index = settings_toml["emails"]["ids"].index(sending_email)
    print("   Sending via: " + Fore.LIGHTBLACK_EX + sending_email + Style.RESET_ALL)
    
    message = MIMEMultipart("alternative")
    message['Subject'] = email_subject
    message['From'] = sending_email
    message['To'] = contact_email
    message.attach(MIMEText(email_writeup))
    
    # SMTP_server.send_message(
    #   from_addr=sending_email,
    #   to_addrs=contact_email,
    #   msg=message
    # )
    
    time.sleep(1)
    
    if settings_toml["csv"]["segregate_by_ids"]:
      id_output_data[sending_email_index] += "\n" + ",".join(contact_details)
      id_outputs[sending_email_index].write("\n" + ",".join(contact_details))
    if settings_toml["csv"]["segregate_by_writeups"]:
      writeup_output_data[email_writeup_index] += "\n" + ",".join(contact_details)
      writeup_outputs[email_writeup_index].write("\n" + ",".join(contact_details))
    
    emails_sent += 1
    loading_percentage = emails_sent/rows
    print("\033[6A" if loading_percentage == 1 else "\033[6A")
  
  if settings_toml["csv"]["segregate_by_ids"]:
    for filex in id_outputs:
      filex.close()
  if settings_toml["csv"]["segregate_by_writeups"]:
    for filex in writeup_outputs:
      filex.close()
  
  print("   [" + ("█" * 50) + "] " + str(emails_sent) + " out of " + str(rows))
  print(f"   All {rows} emails sent!" + (" " * 110))
  
  print(" " * 100)
  print(" " * 100)
  print(" " * 100)
  input("   Press Enter to return...")
  main_page()

# Settings Page
def settings_page(tried: bool = False):
  clearscreen()
  show_title("Settings")
  if tried:
    print(f"   {Fore.RED}You cannot run any automation yet, since your important settings are not yet completed.{Style.RESET_ALL}\n")
  print("   Choose what settings category to inspect: \n")
  options = ['[..]', 'Simple Mail Transfer Protocol (SMTP)', 'Email Addresses & Writeups', 'CSV Data Placeholders']
  selection = display_menu(options, 1)
  if selection == 0:
    main_page()
  if selection == 1: # SMTP Settings
    settings_toml = get_toml_data()
    while True:
      clearscreen()
      show_title(f"Settings / {options[1]}")
      print("   Choose what variable to edit: \n")
      smtp_options = [
        '[..]',
        f'Username: {Fore.LIGHTBLACK_EX}{str(settings_toml["smtp"]["username"]) if len(str(settings_toml["smtp"]["username"]).strip()) > 0 else "<empty>"}{Style.RESET_ALL}',
        f'Passkey: {Fore.LIGHTBLACK_EX}{"*" * len(str(settings_toml["smtp"]["passkey"])) if len(str(settings_toml["smtp"]["passkey"]).strip()) > 0 else "<empty>"}{Style.RESET_ALL}',
        f'SMTP Server (Domain or IPv4): {Fore.LIGHTBLACK_EX}{str(settings_toml["smtp"]["smtp_server"]) if len(str(settings_toml["smtp"]["smtp_server"]).strip()) > 0 else "<empty>"}{Style.RESET_ALL}',
        f'SMTP Port: {Fore.LIGHTBLACK_EX}{str(settings_toml["smtp"]["smtp_port"]) if len(str(settings_toml["smtp"]["smtp_port"]).strip()) > 0 else "0"}{Style.RESET_ALL}',]
      smtp_selection = display_menu(smtp_options, 1)
      print("")
      new_input_data = ""
      if smtp_selection == 0:
        break
      elif smtp_selection == 1:
        new_input_data = input(f"   Edit Username {Fore.LIGHTBLACK_EX}(if empty, will revert to {str(settings_toml["smtp"]["username"]) if len(str(settings_toml["smtp"]["username"]).strip()) > 0 else "<empty>"}){Style.RESET_ALL}: ")
        settings_toml["smtp"]["username"] = new_input_data if str(new_input_data).strip() != "" else settings_toml["smtp"]["username"]
      elif smtp_selection == 2:
        new_input_data = getpass(f"   Edit Passkey {Fore.LIGHTBLACK_EX}(if empty, will revert to {"*" * len(str(settings_toml["smtp"]["passkey"])) if len(str(settings_toml["smtp"]["passkey"]).strip()) > 0 else "<empty>"}){Style.RESET_ALL}: ")
        settings_toml["smtp"]["passkey"] = new_input_data if str(new_input_data).strip() != "" else settings_toml["smtp"]["passkey"]
      elif smtp_selection == 3:
        new_input_data = input(f"   Edit SMTP Server (Domain or IPv4): {Fore.LIGHTBLACK_EX}(if empty, will revert to {str(settings_toml["smtp"]["smtp_server"]) if len(str(settings_toml["smtp"]["smtp_server"]).strip()) > 0 else "<empty>"}){Style.RESET_ALL}: ")
        settings_toml["smtp"]["smtp_server"] = new_input_data if str(new_input_data).strip() != "" else settings_toml["smtp"]["smtp_server"]
      elif smtp_selection == 4:
        new_input_data = int(input(f"   Edit SMTP Port {Fore.LIGHTBLACK_EX}(if empty, will revert to {str(settings_toml["smtp"]["smtp_port"]) if len(str(settings_toml["smtp"]["smtp_port"]).strip()) > 0 else "0"}){Style.RESET_ALL}: "))
        settings_toml["smtp"]["smtp_port"] = new_input_data if str(new_input_data).strip() != "" else settings_toml["smtp"]["smtp_port"]
      save_to_toml(settings_toml)
    settings_page()
  elif selection == 2: # Email IDs and Write-ups Settings
    settings_toml = get_toml_data()
    while True:
      clearscreen()
      show_title(f"Settings / {options[2]}")
      print(f"   {len(settings_toml["emails"]["ids"])} Email IDs found")
      print(f" > {Fore.LIGHTBLACK_EX}These email IDs are what are used to send emails (will be sent randomly).{Style.RESET_ALL}\n")
      print(f"   {len(settings_toml["emails"]["writeups"])} Write-ups found")
      print(f" > {Fore.LIGHTBLACK_EX}These write-ups are the content of the emails to be sent (will be sent randomly).{Style.RESET_ALL}\n")
      print("   Choose what variable to edit: \n")
      emails_options = [
        '[..]',
        'Edit the Email IDs',
        'Edit the Write-ups'
      ]
      emails_selection = display_menu(emails_options, 1)
      print("")
      new_input_data = ""
      if emails_selection == 0:
        break
      elif emails_selection == 1:
        while True:
          clearscreen()
          show_title(f"Settings / {options[2]} / Email IDs")
          email_ids = ['[..]']
          for email_id in settings_toml["emails"]["ids"]:
            email_ids.append(email_id)
          email_ids.append(f'{Fore.LIGHTGREEN_EX} + Create New ID {Style.RESET_ALL}')
          email_id_selection = display_menu(email_ids, len(email_ids) - 1)
          print("")
          if email_id_selection == 0:
            break
          elif email_id_selection == len(email_ids) - 1:
            print("   Enter a new email address to use.")
            print("   Return <empty> to discard this change.")
            new_input_data = input(" > ")
            if new_input_data.strip() != "":
              settings_toml["emails"]["ids"].append(new_input_data)
              save_to_toml(settings_toml)
          else:
            print(f"   Edit the email address at use. {Fore.LIGHTBLACK_EX}({settings_toml["emails"]["ids"][email_id_selection - 1]}){Style.RESET_ALL}")
            print("   Return <empty> to discard this change. Return \"delete\" to delete this entry.")
            new_input_data = input(" > ")
            if new_input_data.strip() != "" and new_input_data.strip() != "delete":
              settings_toml["emails"]["ids"][email_id_selection - 1] = new_input_data
              save_to_toml(settings_toml)
            if new_input_data.strip() == "delete":
              settings_toml["emails"]["ids"].pop(email_id_selection - 1)
              save_to_toml(settings_toml)
      elif emails_selection == 2:
        while True:
          clearscreen()
          show_title(f"Settings / {options[2]} / Write-ups")
          writeups = ['[..]']
          for i, writeup in enumerate(settings_toml["emails"]["writeups"]):
            writeup = open(settings_toml["emails"]["writeups"][i], mode='r', encoding='utf-8').read()
            writeups.append(((settings_toml["emails"]["subjects"][i][0:25] + "...") if len(settings_toml["emails"]["subjects"][i]) > 27 else settings_toml["emails"]["subjects"][i]) + ": " + Fore.LIGHTBLACK_EX + ((writeup[0:50] + "...") if len(writeup) > 52 else writeup).replace('\n', ' ').replace('\r', '') + Style.RESET_ALL)
          writeups.append(f'{Fore.LIGHTGREEN_EX} + Create New Write-up {Style.RESET_ALL}')
          writeup_selection = display_menu(writeups, len(writeups) - 1)
          print("")
          if writeup_selection == 0:
            break
          elif writeup_selection == len(writeups) - 1:
            print("   Enter the subject to a new email write-up to use.")
            print("   Return <empty> to discard this change.")
            new_input_data_subjects = input(" > ")
            if new_input_data_subjects.strip() == "":
              break
            print("   Enter the body of a new email write-up to use. (File only)")
            print("   Return <empty> to discard this change.")
            new_input_data_writeup = input(" > ")
            if new_input_data_writeup.strip() == "":
              break
            settings_toml["emails"]["subjects"].append(new_input_data_subjects)
            settings_toml["emails"]["writeups"].append(new_input_data_writeup)
            settings_toml["emails"]["isfromfile"].append(True)
            save_to_toml(settings_toml)
          else:
            print("   Edit the subject to a new email write-up to use.")
            print("   " + Fore.LIGHTBLACK_EX + ((settings_toml["emails"]["subjects"][writeup_selection - 1][0:25] + "...") if len(settings_toml["emails"]["subjects"][writeup_selection - 1]) > 27 else settings_toml["emails"]["subjects"][writeup_selection - 1]) + Style.RESET_ALL)
            print("   Return <empty> to discard this change. Return \"delete\" to delete this entry.")
            new_input_data_subjects = input(" > ")
            if new_input_data_subjects.strip() == "":
              new_input_data_subjects = settings_toml["emails"]["subjects"][writeup_selection - 1]
            if new_input_data_subjects.strip() == "delete":
              settings_toml["emails"]["subjects"].pop(writeup_selection - 1)
              settings_toml["emails"]["writeups"].pop(writeup_selection - 1)
              settings_toml["emails"]["isfromfile"].pop(writeup_selection - 1)
              break
            print("   Edit the body of a new email write-up to use. (Filepath only, UTF-8 encoding)")
            print("   " + Fore.LIGHTBLACK_EX + ((settings_toml["emails"]["writeups"][writeup_selection - 1][0:50] + "...") if len(settings_toml["emails"]["writeups"][writeup_selection - 1]) > 52 else settings_toml["emails"]["writeups"][writeup_selection - 1]).replace('\n', ' ').replace('\r', '') + Style.RESET_ALL)
            print("   Return <empty> to discard this change.")
            new_input_data_writeup = input(" > ")
            if new_input_data_writeup.strip() == "":
              new_input_data_writeup = settings_toml["emails"]["writeups"][writeup_selection - 1]
            settings_toml["emails"]["subjects"][writeup_selection - 1] = new_input_data_subjects
            settings_toml["emails"]["writeups"][writeup_selection - 1] = new_input_data_writeup
            settings_toml["emails"]["isfromfile"][writeup_selection - 1] = True
            save_to_toml(settings_toml)
      save_to_toml(settings_toml)
    settings_page()
  elif selection == 3: # CSV Data
    settings_toml = get_toml_data()
    cant_delete = ['email']
    while True:
      clearscreen()
      show_title(f"Settings / {options[3]}")
      print(f"   {len(settings_toml["csv"]["placeholders"])} Placeholders found")
      print(f" > {Fore.LIGHTBLACK_EX}These placeholders are used to replace text between {'{these brackets}'} with data from the CSV file.{Style.RESET_ALL}\n")
      print(f"   Current CSV output folder: {settings_toml["csv"]["output_folder"]}")
      print(f" > {Fore.LIGHTBLACK_EX}Folder where the output data CSV files are stored.{Style.RESET_ALL}\n")
      print(f"   Filter outputs by write-ups: {f'{Fore.GREEN}Yes{Style.RESET_ALL}' if settings_toml["csv"]["segregate_by_writeups"] else f'{Fore.RED}No{Style.RESET_ALL}'}")
      print(f" > {Fore.LIGHTBLACK_EX}If 'Yes', then the output CSV files are broken based on the write-ups.{Style.RESET_ALL}\n")
      print(f"   Filter outputs by email-IDs: {f'{Fore.GREEN}Yes{Style.RESET_ALL}' if settings_toml["csv"]["segregate_by_ids"] else f'{Fore.RED}No{Style.RESET_ALL}'}")
      print(f" > {Fore.LIGHTBLACK_EX}If 'Yes', then the output CSV files are broken based on the email IDs.{Style.RESET_ALL}\n")
      print("   Choose what variable to edit: \n")
      csv_options = [
        '[..]',
        'Edit the Placeholders',
        'Edit the Filter Outputs'
      ]
      csv_selection = display_menu(csv_options, 1)
      print("")
      new_input_data = ""
      if csv_selection == 0:
        break
      elif csv_selection == 1:
        while True:
          clearscreen()
          show_title(f"Settings / {options[3]} / Edit Placeholders")
          placeholders = ['[..]']
          for i, placeholder in enumerate(settings_toml["csv"]["placeholders"]):
            placeholders.append(f'{'{'}{placeholder}{'}'}: {Fore.LIGHTBLACK_EX}{settings_toml["csv"]["titles"][i]}{Style.RESET_ALL}')
          placeholders.append(f'{Fore.LIGHTGREEN_EX} + Create New Placeholder {Style.RESET_ALL}')
          placeholder_selection = display_menu(placeholders, len(placeholders) - 1)
          if placeholder_selection == 0:
            break
          elif placeholder_selection == len(placeholders) - 1:
            print("   Enter a new placeholder, without the curly braces.")
            print("   Return <empty> to discard this change.")
            new_input_data_placeholder = input(" > ")
            if new_input_data_placeholder.strip() == "":
              break
            print("   Enter the title for what this placeholder should replace. (Case sensitive)")
            print("   Return <empty> to discard this change.")
            new_input_data_title = input(" > ")
            if new_input_data_title.strip() == "":
              break
            settings_toml["csv"]["titles"].append(new_input_data_title)
            settings_toml["csv"]["placeholders"].append(new_input_data_placeholder)
            save_to_toml(settings_toml)
          else:
            if settings_toml["csv"]["placeholders"][placeholder_selection - 1] not in cant_delete:
              print("   Edit the placeholder, without the curly braces.")
              print("   " + Fore.LIGHTBLACK_EX + settings_toml["csv"]["placeholders"][placeholder_selection - 1] + Style.RESET_ALL)
              print("   Return <empty> to discard this change. Return \"delete\" to delete this entry.")
              new_input_data_placeholder = input(" > ")
              if new_input_data_placeholder.strip() == "":
                new_input_data_placeholder = settings_toml["csv"]["placeholders"][placeholder_selection - 1]
              if new_input_data_placeholder.strip() == "delete":
                settings_toml["csv"]["titles"].pop(placeholder_selection - 1)
                settings_toml["csv"]["placeholders"].pop(placeholder_selection - 1)
                break
            else:
              new_input_data_placeholder = settings_toml["csv"]["placeholders"][placeholder_selection - 1]
            print("   Edit the title for what this placeholder should replace. (Case sensitive)")
            print("   " + Fore.LIGHTBLACK_EX + settings_toml["csv"]["titles"][placeholder_selection - 1] + Style.RESET_ALL)
            print("   Return <empty> to discard this change.")
            new_input_data_title = input(" > ")
            if new_input_data_title.strip() == "":
              new_input_data_title = settings_toml["emails"]["titles"][placeholder_selection - 1]
            settings_toml["csv"]["titles"][placeholder_selection - 1] = new_input_data_title
            settings_toml["csv"]["placeholders"][placeholder_selection - 1] = new_input_data_placeholder
            save_to_toml(settings_toml)
      elif csv_selection == 2:
        clearscreen()
        show_title(f"Settings / {options[3]} / Edit Filters")
        writeup_input = input("Filter based on write-ups? (Y/N/~)> ")
        if writeup_input.strip() == "":
          pass
        elif writeup_input.strip().lower() == 'y':
          settings_toml["csv"]["segregate_by_writeups"] = True
        elif writeup_input.strip().lower() == 'n':
          settings_toml["csv"]["segregate_by_writeups"] = False
        ids_input = input("Filter based on email IDs? (Y/N/~)> ")
        if ids_input.strip() == "":
          pass
        elif ids_input.strip().lower() == 'y':
          settings_toml["csv"]["segregate_by_ids"] = True
        elif ids_input.strip().lower() == 'n':
          settings_toml["csv"]["segregate_by_ids"] = False
        save_to_toml(settings_toml)
    settings_page()

def credits_page():
  clearscreen()
  show_title("Credits")
  print("   Program Author: Swastik Biswas")
  print("")
  print(f"   Program Name: {Fore.LIGHTBLACK_EX}Auto Email Sendr{Style.RESET_ALL}")
  print(f"   Program Description: {Fore.LIGHTBLACK_EX}Automatic email mass-sender, for outreach and campaigns.{Style.RESET_ALL}")
  print(f"   Program Type: {Fore.LIGHTBLACK_EX}Free & Open-Source{Style.RESET_ALL}")
  print(f"   Version: {Fore.LIGHTBLACK_EX}{VERSION}{Style.RESET_ALL}")
  print(f"   Contact Me: {Fore.LIGHTBLACK_EX}swastikbiswas962@gmail.com{Style.RESET_ALL}")
  print(f"               {Fore.LIGHTBLACK_EX}swastik@octran.tech{Style.RESET_ALL}")
  print(f"   GitHub Link: {Fore.LIGHTBLACK_EX}https://github.com/PolybitRockzz/auto-email-sendr{Style.RESET_ALL}")
  print("")
  print(f"   X (formerly Twitter): {Fore.LIGHTBLACK_EX}https://x.com/0xSwastikBiswas{Style.RESET_ALL}")
  print(f"   Instagram: {Fore.LIGHTBLACK_EX}https://instagram.com/0x_swastikbiswas{Style.RESET_ALL}")
  print(f"   YouTube: {Fore.LIGHTBLACK_EX}https://youtube.com/@SwastikBiswas{Style.RESET_ALL}")
  print(f"   LinkedIn: {Fore.LIGHTBLACK_EX}https://www.linkedin.com/in/swastikpolybitbiswas/{Style.RESET_ALL}")
  print("")
  input("   Press Enter to return...")
  main_page()

def main_page():
  clearscreen()
  show_title("Main Page")
  print("   Choose what action to perform: \n")
  options = ['Run Automation', f'Settings {f'{Fore.RED}[Incomplete]{Style.RESET_ALL}' if is_toml_empty() else f'{Fore.GREEN}[OK]{Style.RESET_ALL}'}', 'Credits', 'Quit App']
  selection = display_menu(options, 0)
  if selection == 0:
    if is_toml_empty():
      settings_page(True)
    else:
      run_automation_page()
  elif selection == 1:
    settings_page()
  elif selection == 2:
    credits_page()
  elif selection == 3:
    clearscreen()
    quit(0)

if __name__ == '__main__':
  os.system('mode con: cols=133 lines=47')
  main_page()