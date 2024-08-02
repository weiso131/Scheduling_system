def scanf(token : str, target : str):

    output = []
    token_list = token.split('/')
    target_list = target.split('/')

    if len(token_list) != len(target_list):
        return "格式不符"

    for i in range(len(target_list)):
        if target_list[i] == 's':
            output.append(token_list[i])
        elif target_list[i] == 'd':
            try:
                output.append(int(token_list[i]) - 1) #電腦是從0開始的
            except ValueError:
                return f"{token_list[i]}無效的日子"
        elif target_list[i] == 'w': #星期幾
            try:
                output.append((int(token_list[i]) + 7) % 7)
            except ValueError:
                return f"{token_list[i]}無效的日子"
        elif target_list[i] == 'p':
            if token_list[i] == '上午':
                output.append(0)
            elif token_list[i] == '下午':
                output.append(1)
            else:
                return f"{token_list[i]}無效時段"
        
            
    
    return tuple(output)


def get_personal_leave(tokens : str):
    tokens = tokens.replace(' ', '')
    token_list = tokens.split(',')

    output = []

    for token in token_list:
        if len(token) == 0:
            continue
        periods = token.split('~')
        if len(periods) != 2:
            return ""
        
        start = scanf(periods[0], 'd/p')
        end = scanf(periods[1], 'd/p')

        if type(start) is not tuple or type(end) is not tuple:
            return ""
        
        output.append(start + end)
        
    
    return output

def get_period(tokens : str):
    tokens = tokens.replace(' ', '')
    token_list = tokens.split(',')

    output = []

    for token in token_list:
        if len(token) == 0:
            continue
        period = scanf(token, 's/w/p')
        if type(period) is not tuple:
            return period
        
        output.append(period)
    return output

# inputs = "09/上午~ 10/下午, 11/上午~ 12/下午, "
# inputs1 = "87/1/上午, "
# print(get_personal_leave(inputs))
# print(get_period(inputs1))