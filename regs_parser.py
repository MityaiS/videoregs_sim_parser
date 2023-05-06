import csv
import phonenumbers
import os

source_path = os.path.join(os.path.dirname(__file__), "source_csv")

mts_file = open(os.path.join(source_path, "mts.csv"), "r", encoding='utf-8-sig', newline="")
mts_reader = csv.DictReader(mts_file, delimiter=";")

meg_file = open(os.path.join(source_path, "meg.csv"), "r", encoding='utf-8-sig', newline="")
meg_reader = csv.DictReader(meg_file, delimiter=";")

tele2_file = open(os.path.join(source_path, "tele2.csv"), "r", encoding='utf-8-sig', newline="")
tele2_reader = csv.DictReader(tele2_file, delimiter=";")

summary_file = open("summary.csv", "w", encoding="windows-1251", newline="")
fieldnames = ["Клиент", "МТС Акт", "Мегафон Акт", "Теле2 Акт", "МТС Ост", "Мегафон Ост", "Теле2 Ост",
              "Акт сим", "Ост сим", "МТС начисл", "Мегафон начисл", "Теле2 начисл", "Итого"]
sum_writer = csv.DictWriter(summary_file, fieldnames=fieldnames, delimiter=";")

regs_list = []
summary = {}
reg_phones = []
found_phones = []

regs_file = open(os.path.join(source_path, "reg.csv"), "r", encoding='utf-8-sig')
regs_reader = csv.DictReader(regs_file, delimiter=";")

for line in regs_reader:

    summary[line["Компания"]] = {}
    for oper in ("mts", "meg", "tele2"):
        summary[line["Компания"]][oper] = {}
        for status in ("active", "stoped"):
            summary[line["Компания"]][oper][status] = 0
        summary[line["Компания"]][oper]["cons"] = 0

    try:
        line["SIM Card Number"] = phonenumbers.parse(line["SIM Card Number"], "RU")
    except phonenumbers.NumberParseException:
        line["SIM Card Number"] = None

    regs_list.append(line)


for line_mts in mts_reader:

    try:
        mts_phone = phonenumbers.parse(line_mts["Номер"], "RU")
    except phonenumbers.NumberParseException:
        continue

    for line_regs in regs_list:

        reg_phone = line_regs["SIM Card Number"]

        if mts_phone == reg_phone:
            found_phones.append(reg_phone)

            cons = float(line_mts["Общие затраты руб."].replace(",", "."))
            if cons == 0:
                summary[line_regs["Компания"]]["mts"]["stoped"] += 1
            else:
                summary[line_regs["Компания"]]["mts"]["active"] += 1
            summary[line_regs["Компания"]]["mts"]["cons"] += cons

for line_meg in meg_reader:

    try:
        meg_phone = phonenumbers.parse(line_meg["Номер"], "RU")
    except phonenumbers.NumberParseException:
        continue

    for line_regs in regs_list:

        reg_phone = line_regs["SIM Card Number"]

        if reg_phone == meg_phone:
            found_phones.append(reg_phone)

            cons = float(line_meg["Всего"].replace(",", "."))
            if cons == 0:
                summary[line_regs["Компания"]]["meg"]["stoped"] += 1
            else:
                summary[line_regs["Компания"]]["meg"]["active"] += 1
            summary[line_regs["Компания"]]["meg"]["cons"] += cons

for line_tele2 in tele2_reader:

    try:
        tele2_phone = phonenumbers.parse(line_tele2["Номер"], "RU")
    except phonenumbers.NumberParseException:
        continue

    for line_regs in regs_list:

        reg_phone = line_regs["SIM Card Number"]

        if tele2_phone == reg_phone:
            found_phones.append(reg_phone)

            cons = float(line_tele2["Начисления"].replace(",", "."))
            if line_tele2["Статус"] == "Приостановлен":
                summary[line_regs["Компания"]]["tele2"]["stoped"] += 1
            else:
                summary[line_regs["Компания"]]["tele2"]["active"] += 1
            summary[line_regs["Компания"]]["tele2"]["cons"] += cons

# print(summary)

sum_writer.writeheader()
for client_name, client in summary.items():

    active_sims = client["mts"]["active"] + client["meg"]["active"] + client["tele2"]["active"]
    stoped_sims = client["mts"]["stoped"] + client["meg"]["stoped"] + client["tele2"]["stoped"]
    sum_cons = client["mts"]["cons"] + client["meg"]["cons"] + client["tele2"]["cons"]

    line = {"Клиент": client_name, "МТС Акт": client["mts"]["active"], "Мегафон Акт": client["meg"]["active"],
            "Теле2 Акт": client["tele2"]["active"], "МТС Ост": client["mts"]["stoped"], "Мегафон Ост": client["meg"]["stoped"],
            "Теле2 Ост": client["tele2"]["stoped"], "Акт сим": active_sims, "Ост сим": stoped_sims,
            "МТС начисл": client["mts"]["cons"], "Мегафон начисл": client["meg"]["cons"],
            "Теле2 начисл": client["tele2"]["cons"], "Итого": sum_cons}

    sum_writer.writerow(line)

print("Файл с данными находится в summary.csv")

# print("Хотите ли вы видеть симки видеорегистраторов по которым расход равен нулю?(Да\нет)")
# ans = input()

for line_regs in regs_list:
    found = False

    regs_phone = line_regs["SIM Card Number"]
    if regs_phone is None:
        continue

    for found_phone in found_phones:
        if regs_phone == found_phone:
            found = True
            break

    if found:
        continue

    phone_string = phonenumbers.format_number(regs_phone, phonenumbers.PhoneNumberFormat.E164)[1:]
    org = line_regs["Компания"]
    print(f"Не нашел симку {phone_string} у {org}")

input()
