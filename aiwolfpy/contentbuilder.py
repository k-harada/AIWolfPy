# 2018/06/15 Kei Harada

# ref: http://aiwolf.org/control-panel/wp-content/uploads/2014/03/0.4.4での発話生成の方法（修正版2）-2.pdf
# 1
def estimate(target, role):
    return 'ESTIMATE Agent[' + "{0:02d}".format(target) + '] ' + role

# 2
def comingout(target, role):
    return 'COMINGOUT Agent[' + "{0:02d}".format(target) + '] ' + role

# 3
def divination(target):
    return 'DIVINATION Agent[' + "{0:02d}".format(target) + ']'

# 4
def divined(target, result):
    return 'DIVINED Agent[' + "{0:02d}".format(target) + '] ' + result

# 5
def identified(target, result):
    return 'IDENTIFIED Agent[' + "{0:02d}".format(target) + '] ' + result

# 6
def guard(target):
    return 'GUARD Agent[' + "{0:02d}".format(target) + ']'

# 7    
def guarded(target):
    return 'GUARDED Agent[' + "{0:02d}".format(target) + ']'

# 8
def vote(target):
    return 'VOTE Agent[' + "{0:02d}".format(target) + ']'

# 9
def attack(target):
    return 'ATTACK Agent[' + "{0:02d}".format(target) + ']'

# 10
def agree(talkType, talkDay, talkID):
    return 'AGREE '+ talkType + ' day' + str(talkDay) + ' ID:' + str(talkID)

# 11
def disagree(talkType, talkDay, talkID):
    return 'DISAGREE '+ talkType + ' day' + str(talkDay) + ' ID:' + str(talkID)

# 12
def request(content, agent=None):
    if agent is None:
        return 'REQUEST('+ content + ')'
    else:
        return 'REQUEST(Agent[' + "{0:02d}".format(target) + '] '+ content +  ')'

# 13
def skip():
    return 'Skip'

# 14
def over():
    return 'Over'

# parser
def parse(text, agent=None):
    
    res_dict = dict()
    
    res_dict["operator"] = None
    res_dict["topic"] = None
    if text[:6] == "Agent[":
        res_dict["subject"] = int(text[6:8])
        text = text[9:]
    else:
        res_dict["subject"] = agent
    res_dict["target"] = None
    res_dict["role"] = None
    res_dict["result"] = None
    res_dict["talkType"] = None
    res_dict["talkDay"] = -1
    res_dict["talkID"] = -1
    res_dict["contentList"] = []
    
    
    # 12. REQUEST
    if text[:8] == "REQUEST(":
        res_dict["operator"] = "REQUEST"
        res_dict["topic"] = "OPERATOR"
        res_dict["contentList"].append(parse(text[8:(-1)]))
    else:
        text_split = text.split()
        topic = text_split[0]
        res_dict["topic"] = topic
        
        if topic == "ESTIMATE":
            # 1. estimate(target, role)
            res_dict["target"] = int(text_split[1][6:8])
            res_dict["role"] = text_split[2]
        elif topic == "COMINGOUT":
            # 2. comingout(target, role)
            res_dict["target"] = int(text_split[1][6:8])
            res_dict["role"] = text_split[2]
        elif topic == "DIVINATION":
            # 3. divination(target)
            res_dict["target"] = int(text_split[1][6:8])
        elif topic == "DIVINED":
            # 4. divined(target, result)
            res_dict["target"] = int(text_split[1][6:8])
            res_dict["result"] = text_split[2]
        elif topic == "IDENTIFIED":
            # 5. identified(target, result)
            res_dict["target"] = int(text_split[1][6:8])
            res_dict["result"] = text_split[2]
        elif topic == "GUARD":
            # 6. guard(target)
            res_dict["target"] = int(text_split[1][6:8])
        elif topic == "GUARDED":
            # 7. guarded(target)
            res_dict["target"] = int(text_split[1][6:8])
        elif topic == "VOTE":
            # 8. vote(target)
            res_dict["target"] = int(text_split[1][6:8])
        elif topic == "ATTACK":
            # 9. attack(target)
            res_dict["target"] = int(text_split[1][6:8])
        elif topic == "AGREE":
            # 10. agree(talkType, talkDay, talkID)
            res_dict["talkType"] = text_split[1]
            res_dict["talkDay"] = int(text_split[2][3:])
            res_dict["talkID"] = int(text_split[3][3:])
        elif topic == "DISAGREE":
            # 11. disagree(talkType, talkDay, talkID)
            res_dict["talkType"] = text_split[1]
            res_dict["talkDay"] = int(text_split[2][3:])
            res_dict["talkID"] = int(text_split[3][3:])
            
    return res_dict
