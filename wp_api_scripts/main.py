# -*- coding: utf-8  -*-

###
# main script
###

import pickle
import requests
import time

import tools


def login():
    # correct first: {"login":{"result":"NeedToken","token":"xxx","cookieprefix":"ruwiki","sessionid":"xxx"}}
    # correct 2nd: {"login":{"result":"Success","lguserid":1151236,"lgusername":"xxx","lgtoken":"xxx","cookieprefix":"ruwiki","sessionid":"xxx"}}
    # bad 2nd: {"login":{"result":"WrongPass"}}
    # bad 2nd: {"login":{"result":"NotExists"}}
    username = "HeimdallBot"
    userpass = "1643187992"

    try:
        session = requests.Session()
        login_url = "https://ru.wikipedia.org/w/api.php?action=login&format=json"
        post_data1 = {'lgname': username, 'lgpassword': userpass}
        res1 = session.post(login_url, post_data1)
        result1 = res1.json()["login"]["result"]
        if result1 != "NeedToken":
            tools.debug_print("ACHTUNG! Bad login try. Wrong 1st result.")
            return False
        token1 = res1.json()["login"]["token"]
        cookieprefix1 = res1.json()["login"]["cookieprefix"]
        sessionid1 =  res1.json()["login"]["sessionid"]
    except:
        tools.debug_print("EXCEPTION! Bad login try. 1st part.")
        return False

    try:
        post_data2 = post_data1
        post_data2["lgtoken"] = token1
        res2 = session.post(login_url, post_data2)
        result2 = res2.json()["login"]["result"]
        if result2 != "Success":
            tools.debug_print("ACHTUNG! Bad login try. Wrong 2nd result.")
            return False
        userid2 = res2.json()["login"]["lguserid"]
        username2 = res2.json()["login"]["lgusername"]
        if username2 != username:
            tools.debug_print("ACHTUNG! Bad login try. Get wrong username.")
            return False
        token2 = res2.json()["login"]["lgtoken"]
        cookieprefix2 = res2.json()["login"]["cookieprefix"]
        if cookieprefix2 != cookieprefix1:
            tools.debug_print("ACHTUNG! Bad login try. Wrong cookie prefix.")
            return False
        sessionid2 =  res2.json()["login"]["sessionid"]
        if sessionid2 != sessionid1:
            tools.debug_print("ACHTUNG! Bad login try. Wrong session id.")
            return False
    except:
        tools.debug_print("EXCEPTION! Bad login try. 2nd part.")
        return False

    try:
        f = open("session_keeper", "wb")
        pickle.dump(session, f)
        f.close()
    except:
        tools.debug_print("EXCEPTION! Can't save session.")
        return False

    tools.debug_print("Success login. User: " + username)
    return True


def check_login():
    # good {"query":{"userinfo":{"id":1151236,"name":"Sebiumeker","editcount":115}}}
    # bad {"query":{"userinfo":{"id":0,"name":"93.175.12.119","anon":"","editcount":0}}}
    s = pickle.load(open("session_keeper", "rb"))
    req_url = "https://ru.wikipedia.org/w/api.php?action=query&meta=userinfo&format=json"
    res = s.get(req_url)
    print(res.text)
    id = res.json()["query"]["userinfo"]["id"]
    print(id)
    if id == 0:
        print("bad login! try again")


def test_get_art(title):
    session = pickle.load(open("session_keeper", "rb"))
    url = "https://ru.wikipedia.org/w/api.php?action=query&prop=revisions&format=json&rvprop=content&rvlimit=1&titles="+title+"&redirects="
    res = session.get(url)
    versions = res.json()["query"]["pages"]
    #print(versions)
    name = ""
    version = ""
    for key in versions:
        if key == "-1":
            continue
        version = versions[key]
    if version == "":
        return [name, version]
    name = version["title"]
    rev = version["revisions"][0]["*"]
    return [name, rev]


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


def is_otrs_exists(data):
    names_list = ["Воробьёв", "Каргапольцев", "Мельников", "Симонов",
                  "Осовик", "Примаченк", "Сердюков", "Уфаркин"]
    #проверяем наличие подписи
    if data.find(u"<!-- podpis start -->") == -1 or data.find(u"<!-- podpis end -->") == -1:
        return False
    sign = data[data.find(u"<!-- podpis start -->"):data.find(u"<!-- podpis end -->")]
    #ищем одного из людей
    for unit in names_list:
        if sign.find(unit) != -1:
            return True
    return False


def sort_warheroes_list():
    data_list = pickle.load(open("war_base", "rb"))
    war_base_url = "http://www.warheroes.ru/hero/hero.asp?Hero_id="
    session = requests.session()
    for unit in data_list:
        num = unit[0]
        title = unit[1]
        print(unit)
        id = str(num)
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
        if is_otrs_exists(war_data):
            try:
                print("  - otrs exists")
                good_list = pickle.load(open("free_war_base", "rb"))
                good_list.append(unit)
                pickle.dump(good_list, open("free_war_base", "wb"))
            except:
                tools.debug_print("Bad pickle save3. "+id)
        else:
            try:
                bad_list = pickle.load(open("nonfree_war_base", "rb"))
                bad_list.append(unit)
                pickle.dump(bad_list, open("nonfree_war_base", "wb"))
            except:
                tools.debug_print("Bad pickle save3. "+id)


if __name__ == "__main__":
    print("hello and welcome!")
    #create_warheroes_list(start=18350)
    #data = pickle.load(open("war_base", "rb"))
    #sort_warheroes_list()
    #ata = pickle.load(open("free_war_base", "rb"))
    #print(len(data))
    #d = {"start_num" : 18350}
    #pickle.dump(d, open("war_meta_data", "wb"))
    res = requests.get("http://www.warheroes.ru/hero/hero.asp?Hero_id=100000")
    if res.text.find("Fatal error") != -1:
        print("UPI")