import sys
import copy
from decimal import *
import itertools

def prob(First,evidence):
    global dataSet
    if dataSet[First]['type'] == 'simple':
        if dataSet[First]['parent'] != -1:
            Symbol=""
            for p in dataSet[First]['parent']:
                Symbol=Symbol+' '+evidence[p]
            Symbol=Symbol.strip()
            #print Symbol
            if evidence[First] == "-":
                return 1-float(dataSet[First]['cprob'][Symbol])
            else:
                return float(dataSet[First]['cprob'][Symbol])

        elif dataSet[First]['parent'] == -1:
            if evidence[First] == '-':
                return float(dataSet[First]['jprob']['-'])
            else:
                return float(dataSet[First]['jprob']['+'])

    elif dataSet[First]['type'] == 'decision':
        #decision node
        return 1.0


def enum(nodeSet,evidence):
    global dataSet
    if len(nodeSet)==0:
        return 1.0
    First=nodeSet[0]
    if First in evidence:
        answer= prob(First,evidence)*enum(nodeSet[1:],evidence)
    else:
        temp_evidence=copy.deepcopy(evidence)
        answer=0.0
        for symbol in ['+','-']:
            temp_evidence[First] = symbol
            answer+=(prob(First,temp_evidence)*enum(nodeSet[1:],temp_evidence))
    return answer


def getRequiredNodes(EvidenceVar):
    global dataSet
    keys=dataSet.keys()
    orderNodes=[]
    while len(orderNodes)< len(keys):
        for key in keys:
            if key not in orderNodes:
                if dataSet[key]['parent']==-1:
                    orderNodes.append(key)
                elif all(par in orderNodes for par in dataSet[key]['parent']):
                    orderNodes.append(key)
    nodes=EvidenceVar.keys()
    nodePresentSet={}
    enumNodeSet=[]
    for n in nodes:
        if n in orderNodes:
            nodePresentSet[n]=1
        else:
            nodePresentSet[n]=0
    while len(nodes) !=0:
        node=nodes.pop()
        parent=dataSet[node]['parent']
        if parent!=-1:
            for par in parent:
                if par in orderNodes :
                    nodes.insert(0,par)
                    nodePresentSet[par]=1
    for n in orderNodes:
        if n in nodePresentSet:
            if nodePresentSet[n]==1:
                enumNodeSet.append(n)
    return enumNodeSet

def CondNormalize(partialObservedVar,compObservedVar):
    numSortSet=getRequiredNodes(compObservedVar)
    enumNum=enum(numSortSet,compObservedVar)
    denomSortSet=getRequiredNodes(partialObservedVar)
    enumDenom=enum(denomSortSet,partialObservedVar)
    return enumNum,enumDenom

def JointNormalize(partialObservedVar):
    # for utility function completely observed variables
    # for prob function partial observed variables
    sortSet=getRequiredNodes(partialObservedVar)
    answer=enum(sortSet,partialObservedVar)
    return answer

def getLiteral(term):
    sign=term.split(" = ")[1]
    var=term.split(" = ")[0]
    var=var.strip()
    return var,sign


def callMaxUtil(max_util_q):
    global dataSet
    maxvalues={}
    for q in max_util_q:
        compObservedVar={}
        partialObservedVar={}
        minmaxVar=[]
        if "|" in q:
            q=q[q.find("(")+1:q.find(")")]
            first=q.split(" | ")[0]
            if "," in first:
                fr=first.split(',')
                for val in fr:
                    val=val.strip()
                    if "=" in val:
                        var,sign=getLiteral(val)
                        compObservedVar[var]=sign
                    else:
                        minmaxVar.append(val)
            elif "," not in first:
                if '=' in first:
                    var,sign=getLiteral(first)
                    compObservedVar[var]=sign
                else:
                    first=first.strip()
                    minmaxVar.append(first)
            compObservedVar['utility']='+'
            rest=q.split(" | ")[1]
            if "," in rest:
                rest_var=rest.split(',')
                for term in rest_var:
                    term=term.strip()
                    if "=" in term:
                        var,sign=getLiteral(term)
                        compObservedVar[var]=sign
                        partialObservedVar[var]=sign
                    else:
                        minmaxVar.append(term)
            else:
                if "=" in rest:
                    var,sign=getLiteral(rest)
                    compObservedVar[var]=sign
                    partialObservedVar[var]=sign
                else:
                    minmaxVar.append(rest)
            symbols = list(itertools.product(['+', '-'], repeat=len(minmaxVar)))
            for x in range(0,len(symbols)):
                compEvidence = copy.deepcopy(compObservedVar)
                sym = ''
                y = 0
                for value in minmaxVar:
                    compEvidence[value] = symbols[x][y]
                    sym+=symbols[x][y]
                    y+=1
                enumNum,enumDenom=CondNormalize(partialObservedVar,compEvidence)
                answer = enumNum/enumDenom
                maxvalues[sym]=answer

        else:
            #joint and marginal
            compObservedVar['utility']='+'
            q=q[q.find("(")+1:q.find(")")]
            if("," in q):
                terms=q.split(',')
                for term in terms:
                    term=term.strip()
                    if '=' in term:
                        var,sign=getLiteral(term)
                        compObservedVar[var]=sign
                        partialObservedVar[var]=sign
                    else:
                        minmaxVar.append(term)
            else:
                if("=" in q):
                    var,sign=getLiteral(q)
                    compObservedVar[var]=sign
                    partialObservedVar[var]=sign

                else:
                    minmaxVar.append(q)
            # complete observed variables
            symbols = list(itertools.product(['+', '-'], repeat=len(minmaxVar)))
            for x in range(0,len(symbols)):
                compEvidence = copy.deepcopy(compObservedVar)
                sym = ''
                y = 0
                for value in minmaxVar:
                    compEvidence[value] = symbols[x][y]
                    sym+=" "+symbols[x][y]
                    y+=1
                sym=sym.strip()
                answer=JointNormalize(compEvidence)
                maxvalues[sym]=answer
        maxVal=0.0
        for a in maxvalues:
            if maxvalues[a]>maxVal:
                maxVal=maxvalues[a]
        finalSym=""
        for b in maxvalues:
            if maxvalues[b]==maxVal:
                finalSym=b
        finalVal=finalSym+" "+str(int(round(maxVal)))
        otpt.write(str(finalVal)+'\n')



def callUtility(util_q):
    global dataSet
    for q in util_q:
        compObservedVar={}
        partialObservedVar={}
        if "|" in q:
            q=q[q.find("(")+1:q.find(")")]
            first=q.split(" | ")[0]
            if "," in first:
                for val in first:
                    var,sign=getLiteral(val)
                    compObservedVar[var]=sign
            else:
                var,sign=getLiteral(first)
                compObservedVar[var]=sign
            compObservedVar['utility']='+'
            rest=q.split(" | ")[1]
            if "," in rest:
                rest_var=rest.split(',')
                for term in rest_var:
                    var,sign=getLiteral(term)
                    compObservedVar[var]=sign
                    partialObservedVar[var]=sign
            else:
                var,sign=getLiteral(rest)
                compObservedVar[var]=sign
                partialObservedVar[var]=sign
            enumNum,enumDenom=CondNormalize(partialObservedVar,compObservedVar)
            answer = enumNum/enumDenom
            answer = int(round(answer))
            otpt.write(str(answer)+'\n')


        else:
            #joint and marginal
            compObservedVar['utility']='+'
            q=q[q.find("(")+1:q.find(")")]
            if("," in q):
                terms=q.split(',')
                for term in terms:
                    var,sign=getLiteral(term)
                    compObservedVar[var]=sign
                    partialObservedVar[var]=sign
            else:
                var,sign=getLiteral(q)
                compObservedVar[var]=sign
                partialObservedVar[var]=sign
            #complete observed variables
            answer=JointNormalize(compObservedVar)
            answer = int(round(answer))
            otpt.write(str(answer)+'\n')

def callQuery(prob_q):
    global dataSet
    for q in prob_q:
        compObservedVar={}
        partialObservedVar={}
        if "|" in q:
            q=q[q.find("(")+1:q.find(")")]
            first=q.split(" | ")[0]
            if "," in first:
                first_var=first.split(',')
                for term in first_var:
                    var,sign=getLiteral(term)
                    compObservedVar[var]=sign
            else:
                var,sign=getLiteral(first)
                compObservedVar[var]=sign
            rest=q.split(" | ")[1]
            if "," in rest:
                rest_var=rest.split(',')
                for term in rest_var:
                    var,sign=getLiteral(term)
                    compObservedVar[var]=sign
                    partialObservedVar[var]=sign
            else:
                var,sign=getLiteral(rest)
                compObservedVar[var]=sign
                partialObservedVar[var]=sign
            enumNum,enumDenom=CondNormalize(partialObservedVar,compObservedVar)
            answer = enumNum/enumDenom
            answer = Decimal(str(answer)).quantize(Decimal('.01'))
            otpt.write(str(answer)+'\n')

        else:
            #joint and marginal
            q=q[q.find("(")+1:q.find(")")]
            if("," in q):
                terms=q.split(',')
                for term in terms:
                    var,sign=getLiteral(term)
                    compObservedVar[var]=sign
                    partialObservedVar[var]=sign
            else:
                var,sign=getLiteral(q)
                compObservedVar[var]=sign
                partialObservedVar[var]=sign
            answer=JointNormalize(partialObservedVar)
            answer = Decimal(str(answer)).quantize(Decimal('.01'))
            otpt.write(str(answer)+'\n')


#-------------- Parse Input File------------------#
if __name__ == '__main__':
    #filename=str(sys.argv[2])
    filename="input_4.txt"
    inpt1=open(filename,"r")
    prob_q=[]
    util_q=[]
    max_util_q=[]
    dataSet={}
    l_count=0
    answer=0.0
    ipt=inpt1.readlines()
    for a in range(len(ipt)):
        ipt[a]=ipt[a].strip()
    inpt1.close()
    inpt2=open(filename,"r")
    line_count=len(ipt)
    line=inpt2.readline()
    l_count+=1
    while "*" not in line:
        line=line.strip()
        f_temp=""
        op=line.split("(")[0]
        if op=="P":
            prob_q.append(line)
        elif op=="EU":
            util_q.append(line)
        elif op=="MEU":
            max_util_q.append(line)
        l_count+=1
        line=inpt2.readline()

    if "*" in line:
        line=line.strip()
        star_count=line.split("*")
        if(len(star_count)==7):
            while(l_count<=line_count):
                line=inpt2.readline()
                line=line.strip()
                l_count+=1
                while "*" not in line and len(line)>0:
                    if "|" not in line:
                        line=line.strip()
                        if 'decision' in ipt[l_count]:
                            #utility node
                            key=line
                            dataSet[line]={}
                            line=inpt2.readline()
                            line=line.strip()
                            l_count+=1
                            dataSet[key]['type']='decision'
                            dataSet[key]['parent']=-1
                        #elif "decision" not in ipt[l_count+1]:
                        else:
                            key=line
                            dataSet[line]={}
                            line=inpt2.readline()
                            line=line.strip()
                            l_count+=1
                            dataSet[key]['jprob']={}
                            dataSet[key]['jprob']['+']=line
                            n_pr=1-float(line)
                            dataSet[key]['jprob']['-']=n_pr
                            dataSet[key]['parent']=-1
                            dataSet[key]['type']='simple'
                            dataSet[key]['child']=[]
                    elif "|" in line:
                        first=line.split("|")[0]
                        first=first.strip()
                        if("utility" not in first):
                            rest=line.split("|")[1]
                            rest=rest.strip()
                            dataSet[first]={}
                            #r=rest.split(" ")
                            prnt=rest.split(" ")
                            dataSet[first]['parent']=[]
                            dataSet[first]['child']=[]
                            for p in prnt:
                                if 'child' not in dataSet[p]:
                                    dataSet[p]['child']=[]
                                dataSet[first]['parent'].append(p)
                                dataSet[p]['child'].append(first)
                            dataSet[first]['type']='simple'
                            dataSet[first]['cprob']={}
                            for n in range(2**len(prnt)):
                                line=inpt2.readline()
                                line=line.strip()
                                l_count+=1
                                val=line.split(" ",1)[0]
                                sign=line.split(" ",1)[1]
                                dataSet[first]['cprob'][sign]=float(val)
                    line=inpt2.readline()
                    line=line.strip()
                    l_count+=1
                    line=line.strip()
                    if("*" in line):
                        s_count=line.split("*")
                        if(len(s_count)==7):
                            line=inpt2.readline()
                            line=line.strip()
                            l_count+=1
                            if("utility" in line):
                                if ("|" in line):
                                    f_val=line.split(" | ")[0]
                                    f_val.strip()
                                    dataSet[f_val]={}
                                    r_vl=line.split("|")[1]
                                    r_vl=r_vl.strip()
                                    pr=r_vl.split(" ")
                                    #dataSet[f_val]['node']=r_vl
                                    dataSet[f_val]['cprob']={}
                                    dataSet[f_val]['type']='simple'
                                    dataSet[f_val]['parent']=[]
                                    for m in range(len(pr)):
                                        dataSet[f_val]['parent'].append(pr[m])
                                    for n in range(2**len(pr)):
                                        line=inpt2.readline()
                                        line=line.strip()
                                        l_count+=1
                                        val=line.split(" ",1)[0]
                                        sign=line.split(" ",1)[1]
                                        dataSet[f_val]['cprob'][sign]=val
                            line=inpt2.readline()
                            line=line.strip()
                            l_count+=1
                            line=line.strip()

    #print dataSet
    inpt2.close()
    otpt=open("output.txt","w")
    callQuery(prob_q)
    callUtility(util_q)
    callMaxUtil(max_util_q)
    otpt.close()

