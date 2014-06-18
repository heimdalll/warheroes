# -*- coding: utf-8  -*-

import pickle
import time
import requests

import tools

class War:
    def __init__(self):
        self.war_data_list = pickle.load(open("war_base", "rb"))
        self.free_war_data_list = pickle.load(open("free_war_base", "rb"))
        self.nonfree_war_data_list = pickle.load(open("nonfree_war_base", "rb"))
        self.meta_dic = pickle.load(open("war_meta_data", "rb"))

    def debug_print(self, msg):
        tools.debug_print(msg, file_name="war_log")

    def save_all(self):
        pickle.dump(self.war_data_list, open("war_base", "wb"))

    def save_free(self):
        pickle.dump(self.free_war_data_list, open("free_war_base", "wb"))

    def save_nonfree(self):
        pickle.dump(self.nonfree_war_data_list, open("nonfree_war_base", "wb"))

    def save_meta(self):
        pickle.dump(self.meta_dic, open("war_meta_data", "wb"))

    def save(self):
        self.save_all()
        self.save_free()
        self.save_nonfree()
        self.save_meta()

    # update info from warheroes.ru
    # start number = prev stop number or handmade
    def update_from_warheroes(self):
        war_base_url = "http://www.warheroes.ru/hero/hero.asp?Hero_id="
        session = requests.session()
        if "start_num" in self.meta_dic:
            # get start num from file
            start_num = self.meta_dic["start_num"]
        else:
            # input start num and save to file
            start_num = input("No start number! Please input >>> ")
            if not start_num.isdigit():
                return
            self.meta_dic["start_num"] = start_num
            self.save_meta()
        # go from start to the end
        num = start_num
        while(True):
            id = str(num)
            data = ""
            # trying to get data by url
            is_get_res = False
            try_count = 0
            while not is_get_res and try_count < 10:
                try:
                    res = session.get(war_base_url + id)
                    data = res.text
                    is_get_res = True
                except:
                    try_count += 1
                    time.sleep(1)
            # check for success
            if data == "":
                self.debug_print("Can't get data from "+id)
                num += 1
                continue
            # check for last entry on site
            if data.find("Fatal error") != -1:
                self.meta_dic["start_num"] = num
                self.save_meta()
                break
            if data.find("<font class=\"hero_fio\">") == -1:
                continue


def create_warheroes_list(start=1, stop=18350):
    war_base_url = "http://www.warheroes.ru/hero/hero.asp?Hero_id="
    session = requests.session()
    for num in range(start, stop, 1):
        id = str(num)
        print(id)
        war_url = war_base_url + id
        is_get_res = False
        try_count = 0
        while not is_get_res and try_count < 10:
            try:
                res = session.get(war_url)
                war_data = res.text
                is_get_res = True
            except:
                try_count += 1
                time.sleep(1)
        if war_data.find("<font class=\"hero_fio\">") == -1:
            try:
                bad_list = pickle.load(open("bad_war_base", "rb"))
                bad_list.append(num)
                bad_list.dump(bad_list, open("bad_war_base", "wb"))
            except:
                tools.debug_print("Bad pickle save.")
            continue
        name = war_data[war_data.find("<font class=\"hero_fio\">")+23:]
        name = name[:name.find("<")]
        name = name.replace("&nbsp;", ", ")
        name = name.replace(" ,", ",")
        name = name.replace("  ", " ")
        name = name.strip()
        if name.find("(") != -1:
            try:
                bad_list = pickle.load(open("bad_war_base", "rb"))
                bad_list.append(num)
                bad_list.dump(bad_list, open("bad_war_base", "wb"))
            except:
                tools.debug_print("Bad pickle save1. "+id)
            continue
        art = ""
        title = ""
        is_get_res = False
        try_count = 0
        while not is_get_res and try_count < 10:
            try:
                res = test_get_art(name)
                title = res[0]
                art = res[1]
                is_get_res = True
            except:
                try_count += 1
                time.sleep(1)
        if art == "":
            unit = [num, name]
            try:
                print(unit)
                good_list = pickle.load(open("war_base", "rb"))
                good_list.append(unit)
                pickle.dump(good_list, open("war_base", "wb"))
            except:
                tools.debug_print("Bad pickle save2. "+id)