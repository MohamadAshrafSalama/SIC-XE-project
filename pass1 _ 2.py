import ast
global location
location=[]
global format
format=[]
global lables
lables=[]
global instructions
instructions=[]
global displacment
displacment=[]
global code
code=[]
global symtableloc
symtableloc=[]
global symtablelab
symtablelab=[]
global database
database= (['ADD', 3, '18', 0], ['ADDF', 3, '58', 1], ['ADDR', 2, '90', 2], ['AND', 3, '40', 3], ['CLEAR', 2, 'b4', 4],
        ['COMP', 3, '28', 5], ['COMPF', 3, '88', 6], ['COMPF', 3, '88', 7], ['COMPR', 2, 'a0', 8],
        ['DIV', 3, '24', 9], ['DIVF', 3, '64', 10],
        ['DIVR', 2, '9c', 11], ['FIX', 1, 'c4', 12], ['FLOAT', 1, 'c0', 13], ['HIO', 1, 'f4', 14], ['J', 3, '3c', 15],
         ['JEQ', 3, '30', 16], ['JGT', 3, '34', 17], ['JLT', 3, '38', 18], ['JSUB', 3, '48', 19], ['LDA', 3, '00', 20],
         ['LDB', 3, '68', 21], ['LDCH', 3, '50', 22], ['LDF', 3, '70', 23], ['LDL', 3, '08', 24], ['LDS', 3, '6c', 25],
         ['LDT', 3, '74', 26], ['LDX', 3, '04', 27], ['LPS', 3, 'd0', 28], ['MUL', 3, '20', 29], ['MULF', 3, '60', 30],
         ['MULR', 2, '98', 31], ['NORM', 1, 'c8', 32], ['OR', 3, '44', 33], ['RD', 3, 'd8', 34], ['RMO', 2, 'ac', 35],
         ['RSUB', 3, '4c', 36], ['SHIFTL', 2, 'a4', 37], ['SHIFTR', 2, 'a8', 38], ['SIO', 1, 'f0', 39], ['SSK', 3, 'ec',
         40],['STA', 3, 'Oc', 41], ['STB', 3, '78', 42], ['STCH', 3, '54', 43], ['STF', 3, '80', 44], ['STI', 3, 'd4', 45],
        ['STL', 3, '14', 46], ['STS', 3, '7c', 47], ['STSW', 3, 'e8', 48], ['STT', 3, '84', 49], ['STX', 3, '10', 50],
        ['SUB', 3, '1c', 51], ['SUBF', 3, '5c', 52], ['SUBR', 2, '94', 53], ['SVC', 2, 'b0', 54], ['TD', 3, 'e0', 55],
        ['TIO', 1, 'F8', 56], ['TIX', 3, '2c', 57], ['TIXR', 2, 'B8', 58], ['WD', 3, 'dc', 59],['BASE', 0, 'dc', 60]
        )
global base






def negone(i):

    return'-'




def zero(i):

    sum = ''
    y=displacment[i]
    if instructions[i]=='BYTE':

        if y[0]=='C' :
            y = y.strip('C')
            y = y.replace("'", '')


            for i in range(len(y)-1):
                x = ord(y[i])
                x = hex(x)
                x = x[2:]
                sum = sum + str(x)
        elif y[0]=='X':
            for i in range(len(y)):
                if y[i]=='X':
                    x=y[i+2]
                    z=y[i+3]
                    sum=sum+x+z
    else:
        y=int(y)
        y=hex(y)
        y=y[2:]
        y=str(y)
        sum=y


    return sum






def one (i):
    y=instructions[i]
    for i in range (len(database)):
        if database[i][0]== y:
            y=database[i][2]

    return y







def two (i):
    R=['A','X','L','B','S','T','F','Z','PC','SW']
    sum=''
    y = instructions[i]
    for j in range(len(database)):
        if database[j][0] == y:
            y = database[j][2]
    sum=y

    dis=displacment[i].split(',')
    if '\n' in dis[0]:

         dis[0]=dis[0].strip('\n')

    if len(dis)==1:
        dis.append('A')
    dis[1] = dis[1].strip('\n')
    r1=dis[0]
    r2=dis[1]
    r1value=0
    r2value=0

    for K in range (len(R)):

        if r1==R[K]:
            r1value=K

        if r2 == R[K]:
            r2value=K

    sum=sum+str(r1value)+str(r2value)

    return sum


def address(i):

    k=0
    y=displacment[i].strip('\n')
    if '@' in y:
        y=y.strip('@')
    if ',X' in y:
        y=y.replace(',X','')
    flag=0
    flag1=0
    if y[0]=='#':
        flag1=1
        y=y.strip('#')
        for j in range(len(symtablelab)):
            if symtablelab[j]==y:
                flag=1




    if flag==0 and flag1==1:
        y=int(y)
        y=hex(y)
        y=y[2:]
        y=str(y)
        if format[i]==3 or format[i]==5:
            if len(y)==1:
                y='00'+y
            elif len(y)==2:
                y='0'+y
        else:
            if len(y)==1:
                y='0000'+y
            elif len(y)==2:
                y='000'+y
            elif  len(y)==3:
                y='00'+y
            elif len(y)==4:
                 y='0'+y


        k=2
        return y,k




    loc=symtableloc[0]
    pc=location[i+1]
    j=0

    for j in range(len(symtablelab)):
        if y==symtablelab[j]:
            loc=symtableloc[j]



    if format[i]==4 or format[i]==6:
        k=2
        y=loc[2:]

        if len(y) == 1:
            y = '0000' + y
        elif len(y) == 2:
            y = '000' + y
        elif len(y) == 3:
            y = '00' + y
        elif len(y) == 4:
            y = '0' + y

        return y,k


    loc = ast.literal_eval(loc)

    sub=loc-pc
    if sub>2047 or sub< -2049:
        sub=loc-base
        k=1


    if sub <0:
        sub=hex(sub & (2 ** 32 - 1))
        sub=sub[-3:]
    else:
        sub=hex(sub)
        sub=sub[2:]
        if len(sub)==1:
            sub='00'+sub
        elif len(sub)==2:
            sub='0'+sub


    return sub,k




def nixbpe (z):
    n=i=x=b=p=e=0
    y=displacment[z]
    if y[0]=='#':
        n=0
        i=1
    elif y[0]=='@':
        n=1
        i=0
    else:
        n=1
        i=1

    if ',X' in y:
        x=1

    if format[z]==4:
        e=1


    p,o=address(z)

    if o ==0:
        p=1
        b=0
    elif o==1:
        p=0
        b=1
    else:
        p=0
        b=0

    sum=str(n)+str(i)+str(x)+str(b)+str(p)+str(e)
    return sum




def opcode(i):

    y = instructions[i]
    y=y.strip('+')
    y=y.strip('$')
    y=y.strip('&')
    for j in range(len(database)):
        if database[j][0] == y:
            y = database[j][2]
    y='0X'+y
    y=ast.literal_eval(y)
    y=bin(y)
    y=y[2:-2]


    return y



def  threefour(i):
    out =''

    op=opcode(i)
    ni=nixbpe(i)
    add,_=address(i)
    sum=op+ni
    sum=int(sum,2)
    sum=hex(sum)
    sum=sum[2:]
    sum=sum+add
    out=sum

    return out
def five(z):
    sum=''

    op=opcode(z)
    n,i,x,b,p,e=nixbpe(z)
    add,_=address(z)
    add1=add
    add=ast.literal_eval('0X'+add)
    lol=bin(add)
    lol=lol[2:]
    f1=0
    f2=1
    f3=0
    if add %2 == 0:
        f1=1
    if lol[0] == 0:
        f2=0
    if add == 0 :
        f3=1

    sum=op+str(f1)+str(f2)+x+b+p+str(f3)

    sum=int(sum,2)
    sum=hex(sum)
    sum=sum[2:]
    sum=sum+add1
    return sum


def six(z):
    sum = ''

    op = opcode(z)
    n, i, x, b, p, e = nixbpe(z)
    add, _ = address(z)
    add1 = add
    add = ast.literal_eval('0X' + add)
    lol = bin(add)
    lol = lol[2:]
    f4 = 1
    f5 = 1
    f6 = 1
    if add % 2 == 0:
        f4 = 0
    if add == 0:
        f5 = 0
    if add == base:
        f6 = 0
    sum = op + n+i+x+str(f4) + str(f5) +str(f6)

    sum = int(sum, 2)
    sum = hex(sum)
    sum = sum[2:]
    sum = sum + add1


    return sum

def seven (i):


    sum = ''
    y = displacment[i].strip('=')


    if y[0] == 'C':
        y = y.strip('C')
        y = y.replace("'", '')

        for i in range(len(y) - 1):
            x = ord(y[i])
            x = hex(x)
            x = x[2:]
            sum = sum + str(x)
    elif y[0] == 'X':
        for i in range(len(y)):
            if y[i] == 'X':
                x = y[i + 2]
                z = y[i + 3]
                sum = sum + x + z


    return sum


def operation(words,i):
    if'EQU' in words:
        format.append(-1)
        return 0


    b=0
    f=3
    if '+'in words:
        words=words.strip('+')
        f=4
        b=1
    elif'&' in words:
        words=words.strip('&')
        f=5
    elif '$' in words:
        words=words.strip('$')
        b=1
        f=6
    if words=='RESB':
        f=-1
        format.append(f)
        return int(displacment[i])
    if words=='RESW':
        f=-1
        format.append(f)
        return int(displacment[i])*3
    if words=='BYTE':
        f=0
        c=0

        y=displacment[i]

        if(y[0]=='C'):
            y=y.strip('C')
            y=y.replace("'",'')
            format.append(f)

            return len(y)-1

        elif(y[0]=='X'):
            for i in range(len(y)):
                if y[i]=='X':
                    c=c+1
        format.append(f)
        return c
    if words=='WORD':
        f=0
        format.append(f)
        return 3


    data = (['ADD', 3, '18', 0], ['ADDF', 3, '58', 1], ['ADDR', 2, '90', 2], ['AND', 3, '40', 3], ['CLEAR', 2, 'B4', 4],
        ['COMP', 3, '28', 5], ['COMPF', 3, '88', 6], ['COMPF', 3, '88', 7], ['COMPR', 2, 'A0', 8],
        ['DIV', 3, '24', 9], ['DIVF', 3, '64', 10],
            ['DIVR', 2, '9C', 11], ['FIX', 1, 'C4', 12], ['FLOAT', 1, 'C0', 13], ['HIO', 1, 'F4', 14], ['J', 3, '3C', 15],
         ['JEQ', 3, '30', 16], ['JGT', 3, '34', 17], ['JLT', 3, '38', 18], ['JSUB', 3, '48', 19], ['LDA', 3, '00', 20],
         ['LDB', 3, '68', 21], ['LDCH', 3, '50', 22], ['LDF', 3, '70', 23], ['LDL', 3, '08', 24], ['LDS', 3, '6C', 25],
         ['LDT', 3, '74', 26], ['LDX', 3, '04', 27], ['LPS', 3, 'D0', 28], ['MUL', 3, '20', 29], ['MULF', 3, '60', 30],
         ['MULR', 2, '98', 31], ['NORM', 1, 'C8', 32], ['OR', 3, '44', 33], ['RD', 3, 'D8', 34], ['RMO', 2, 'AC', 35],
         ['RSUB', 3, '4C', 36], ['SHIFTL', 2, 'A4', 37], ['SHIFTR', 2, 'A8', 38], ['SIO', 1, 'F0', 39], ['SSK', 3, 'EC',
         40],['STA', 3, 'OC', 41], ['STB', 3, '78', 42], ['STCH', 3, '54', 43], ['STF', 3, '80', 44], ['STI', 3, 'D4', 45],
        ['STL', 3, '14', 46], ['STS', 3, '7C', 47], ['STSW', 3, 'E8', 48], ['STT', 3, '84', 49], ['STX', 3, '10', 50],
        ['SUB', 3, '1C', 51], ['SUBF', 3, '5C', 52], ['SUBR', 2, '94', 53], ['SVC', 2, 'B0', 54], ['TD', 3, 'E0', 55],
        ['TIO', 1, 'F8', 56], ['TIX', 3, '2C', 57], ['TIXR', 2, 'B8', 58], ['WD', 3, 'DC', 59],['BASE', 0, 'DC', 60]
        )
    for i in range (len(data)):
        if data[i][0]== words:


            if data[i][1] ==1:
                f=1

            elif data[i][1]==2:
                f=2
            format.append(f)
            return data[i][1]+b




lit=[]

with open('test.txt','r') as f:
    line = f.readline()
    words=line.split(' ')
    code_name=words[0]
    startindex=int(words[2])
    base=startindex
    location.append(startindex)
    while line:
        line = f.readline()
        words=line.split(' ')
        if '='in words[2]:
            lit.append(words[2])
        if words[0]=='.':
            continue

        if words==['']:
            continue

        if words[1]=='LTORG':
            lables.append('-')
            instructions.append('LTORG')
            displacment.append('-')

            for i in lit   :
                lables.append(i)
                instructions.append(i.strip('\n'))
                displacment.append(i)
            lit.clear()
            continue
        if words[1]=='END':
            lables.append('-')
            instructions.append('END')
            displacment.append('-')
            for i in lit   :
                lables.append(i)
                instructions.append(i)
                displacment.append(i)
            break

        lables.append(words[0])
        instructions.append(words[1])
        displacment.append(words[2])



sum=startindex


for i in range(len(instructions)):

    if '=' in instructions[i]:
        if instructions[i][1]=='C':
            sum =sum+3
        if instructions[i][1]=='X':
            sum=sum+1
        location.append(sum)
        format.append(7)
        continue

    if instructions[i]=='LTORG':
        sum=sum+0
        location.append(sum)
        format.append(-1)
        continue
    if instructions[i]=='END':
        sum=sum+0
        location.append(sum)
        format.append(-1)
        continue

    a=operation(instructions[i],i)
    sum=sum+a
    location.append(sum)

for i in range(len(instructions)):

    if instructions[i]=='EQU' and displacment[i].strip('\n')!='*':
        A=B=0

        for j in range(len(lables)) :
            if lables[j] in displacment[i] and lables[j] != '-':
                A=location[j]
                break

        for j in range(len(lables)):
            if lables[j] in displacment[i] and lables[j] != '-' and location[j]!=A:

                B = location[j]


        if '-' in displacment[i]:
            location[i]=abs(A-B)
            vvv=location[i]
        elif '+' in displacment[i]:
            location[i]=A+B
            vvv=location[i]




for i in range(len (lables)):
    if lables[i]=='-':
        continue
    symtableloc.append(hex(location[i]))
    symtablelab.append(lables[i].strip('\n'))



for i in range(len(instructions)):
    if instructions[i]=='BASE':
        y=displacment[i]
        y=y[:-1]
        for j in range(len(symtablelab)):
            if y==symtablelab[j]:

                base=ast.literal_eval(symtableloc[j])



for i in range(len(format)):
    if instructions[i]=='BASE':
        code.append('_')
    if format[i] == -1 :
        code.append(negone(i))
    elif format[i] == 0 :
        code.append(zero(i))
    elif format[i] == 1 :
        code.append(one(i))
    elif format[i] == 2 :
        code.append(two(i))
    elif format[i] == 3 :
        code.append(threefour(i))
    elif format[i] == 4 :
        code.append(threefour(i))
    elif format[i] == 5 :
        code.append(five(i))
    elif format[i] == 6:
        code.append(six(i))
    elif format[i]==7:
        code.append((seven(i)))



f=open("lit.txt","w+")
f.write('name \t value \t adress\n')
for i in range(len(instructions)):
    if '=' in instructions[i]:
        f.write('-------------------------------------------------------------------------\n')
        f.write(str(lables[i].strip('\n')+'\t'+code[i]+'\t'+hex(location[i])[2:])+'\n')




for i in range(len(instructions)):
    if '=' in instructions[i]:
        lables[i]='-'
        displacment[i]='-'





for i in range(len(instructions)):
    if instructions[i]=='EQU':
        for j in range(len(symtablelab)):
            if lables[i]==symtablelab[j]:
                symtablelab[j]='----'
                symtableloc[j]=hex(0)


# for i in range(len(instructions)):
#     print('I',location[i],'I',lables[i].strip('\n'),'I',instructions[i].strip('\n'),'I',displacment[i].strip('\n'),'I',code[i],'I',format[i],'I')
#
# for i in range(len(symtablelab)):
#     print('I',symtableloc[i],'I',symtablelab[i],'I')

f=open("SYMTABLE.txt","w+")
f.write('location\tlable\n')
for i in range(len(symtableloc)):
    if '=' in symtablelab[i]:
        continue
    if symtablelab[i]=='----':
        continue
    f.write('--------------------------------------------\n')
    f.write(str("{0:0>6}".format(symtableloc[i][2:])+'\t   \t'+"{0:<10}".format(symtablelab[i]))+'\n')
f.close()

f=open("out.txt","w+")

f.write('loc\tlables\t\tInstruction\tDisplacment\t\t Obj code\n')

for i in range(len(instructions)):

    f.write('--------------------------------------------------------------------------------------\n')
    f.write(str( "{0:0>6}".format(hex(location[i])[2:])+'\t'+"{0:<10}".format(lables[i])+'\t'+"{0:<9}".format(instructions[i].strip('\n'))+'\t'+"{0:<20}".format(displacment[i].strip('\n'))+'\t'+"{0:<10}".format(code[i].strip('\n')))+'\n')





f = open("HTE.txt", "w+")

f.write('H.'+"{0:_<6}".format(code_name)+'.'+"{0:0>6}".format( str(startindex))+'.'+"{0:0>6}".format (hex(location[len(location)-1]-startindex+1)[2:])+'\n')

t=[]
taddress=[]
size=[]

for i in range(len(location)-1):
    size.append(location[i+1]-location[i])

c=0

for i in range(len(code)):



    if (instructions[i]=='RESB' or instructions[i]=='RESW' ):

        if len(t)!=0:
            f.write(str('T.'+"{0:0>6}".format(hex(taddress[0])[2:])+'.'+hex(c)[2:]))
            for j in t:
                f.write('.'+j)
            f.write('\n')

        t.clear()
        taddress.clear()
        c=0
        continue
    if instructions[i]=='RESB' or instructions[i]=='RESW':
        c=0
        continue

    if code[i]=='-':
        continue


    if c>28:

        if len(t) != 0:

            f.write(str('T.' + "{0:0>6}".format(hex(taddress[0])[2:] )+ '.' + hex(c)[2:]))
            for j in t:
                f.write('.' + j)
            f.write('\n')

        t.clear()
        taddress.clear()
        c = 0

    t.append(code[i])
    taddress.append((location[i]))

    c = c + size[i]

f.write(str('T.' + "{0:0>6}".format(hex(location[len(location)-1])[2:]) + '.' + hex(1)[2:]+'.'+code[len(code)-1]+'\n'))


for i in range(len(format)):
    if format[i]==4 or format[i]==6:
        f.write(str('M.'+"{0:0>6}".format(hex(location[i]+1)[2:])+'.05\n'))

f.write(str('E.'+"{0:0<6}".format(str(startindex))))



f.close()
