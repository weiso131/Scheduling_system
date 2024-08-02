def scanf(token : str, target : str):

    output = []
    token_list = token.split('/')
    target_list = target.split('/')
    
    for i in range(len(target_list)):
        if target_list[i] == 's':
            output.append(token_list[i])
        elif target_list[i] == 'd':
            try:
                output.append(int(token_list[i]))
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
        if len(periods) < 2:
            return "少了 \'~\'"
        elif len(periods) > 2:
            return "多了 \'~\'"
        

        start = scanf(periods[0], 'd/p')
        end = scanf(periods[1], 'd/p')

        if type(start) is not tuple:
            return start
        if type(end) is not tuple:
            return end
        
        output.append({"start" : start, "end" : end})
        
    
    return output

def get_period(tokens : str):
    tokens = tokens.replace(' ', '')
    token_list = tokens.split(',')

    output = []

    for token in token_list:
        if len(token) == 0:
            continue
        period = scanf(token, 's/d/p')
        if type(period) is not tuple:
            return period
        
        output.append(period)
    return output

